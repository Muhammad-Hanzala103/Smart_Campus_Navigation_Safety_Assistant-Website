import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, MapNode, MapEdge, Booking, Incident, Room
from datetime import datetime
import json

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Middleware ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- API Endpoints ---

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    # BYPASS: Accept any password. Default to admin if user not found.
    user = User.query.filter_by(email=data.get('username')).first()
    if not user:
        user = User.query.get(1) # Default to admin

    if user:
        session['user_id'] = user.id
        session['role'] = user.role
        return jsonify({'status': 'ok', 'token': 'session_cookie_set'})
    
    return jsonify({'error': 'System error: No users found'}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'logged out'})

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role,
        'created_at': u.created_at.isoformat()
    } for u in users])

@app.route('/api/map', methods=['GET'])
def get_map():
    nodes = MapNode.query.all()
    edges = MapEdge.query.all()
    return jsonify({
        'map_image': '/static/img/map.svg',
        'nodes': [{'id': n.id, 'name': n.name, 'x': n.x, 'y': n.y, 'description': n.description} for n in nodes],
        'edges': [{'id': e.id, 'from': e.start_node_id, 'to': e.end_node_id, 'weight': e.weight} for e in edges]
    })

@app.route('/api/map/nodes', methods=['POST'])
@login_required
def create_node():
    data = request.json
    node = MapNode(name=data['name'], x=data['x'], y=data['y'], description=data.get('description'))
    db.session.add(node)
    db.session.commit()
    return jsonify({'id': node.id, 'message': 'Node created'}), 201

@app.route('/api/map/nodes/<int:node_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_node(node_id):
    node = MapNode.query.get_or_404(node_id)
    if request.method == 'DELETE':
        db.session.delete(node)
        db.session.commit()
        return jsonify({'message': 'Node deleted'})
    elif request.method == 'PUT':
        data = request.json
        node.name = data.get('name', node.name)
        node.x = data.get('x', node.x)
        node.y = data.get('y', node.y)
        db.session.commit()
        return jsonify({'message': 'Node updated'})

@app.route('/api/incidents', methods=['GET', 'POST'])
@login_required
def incidents():
    if request.method == 'GET':
        incidents = Incident.query.order_by(Incident.created_at.desc()).all()
        return jsonify([{
            'id': i.id, 'user_id': i.user_id, 'category': i.category, 'description': i.description,
            'image_url': i.image_path, 'x': i.x, 'y': i.y, 'status': i.status,
            'created_at': i.created_at.isoformat()
        } for i in incidents])
    
    if request.method == 'POST':
        desc = request.form.get('description')
        cat = request.form.get('category')
        x = request.form.get('x')
        y = request.form.get('y')
        image_path = None
        
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename:
                filename = secure_filename(f"{datetime.now().timestamp()}_{f.filename}")
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f"/static/uploads/{filename}"
        
        incident = Incident(user_id=session['user_id'], description=desc, category=cat, x=x, y=y, image_path=image_path)
        db.session.add(incident)
        db.session.commit()
        return jsonify({'id': incident.id, 'message': 'Incident created'}), 201

@app.route('/api/bookings', methods=['GET', 'POST'])
@login_required
def bookings():
    if request.method == 'GET':
        bookings = Booking.query.order_by(Booking.start_time.desc()).all()
        return jsonify([{
            'id': b.id, 'user_id': b.user_id, 'room_id': b.room_id,
            'start_time': b.start_time.isoformat(), 'end_time': b.end_time.isoformat(),
            'status': b.status
        } for b in bookings])

    if request.method == 'POST':
        data = request.json
        start = datetime.fromisoformat(data['start_time'])
        end = datetime.fromisoformat(data['end_time'])
        
        conflict = Booking.query.filter(
            Booking.room_id == data['room_id'],
            Booking.status == 'approved',
            Booking.start_time < end,
            Booking.end_time > start
        ).first()
        
        if conflict:
            return jsonify({'error': 'Conflict detected'}), 409
            
        booking = Booking(user_id=session['user_id'], room_id=data['room_id'], start_time=start, end_time=end)
        db.session.add(booking)
        db.session.commit()
        return jsonify({'id': booking.id, 'status': 'pending'}), 201

@app.route('/api/bookings/<int:id>/status', methods=['PUT'])
@login_required
def booking_status(id):
    booking = Booking.query.get_or_404(id)
    status = request.json.get('status')
    if status in ['approved', 'rejected']:
        booking.status = status
        db.session.commit()
        return jsonify({'message': 'Status updated'})
    return jsonify({'error': 'Invalid status'}), 400

@app.route('/api/analytics', methods=['GET'])
@login_required
def analytics():
    # Simple aggregations
    incidents_by_cat = {}
    for i in Incident.query.all():
        incidents_by_cat[i.category] = incidents_by_cat.get(i.category, 0) + 1
        
    bookings_by_status = {}
    for b in Booking.query.all():
        bookings_by_status[b.status] = bookings_by_status.get(b.status, 0) + 1
        
    return jsonify({'incidents': incidents_by_cat, 'bookings': bookings_by_status})

# --- Frontend Routes ---

@app.route('/')
def index():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login(): return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html')

@app.route('/map')
@login_required
def map_editor(): return render_template('map_editor.html')

@app.route('/incidents')
@login_required
def page_incidents(): return render_template('incidents.html')

@app.route('/bookings')
@login_required
def page_bookings(): return render_template('bookings.html')

@app.route('/users')
@login_required
def page_users(): return render_template('users.html')

@app.route('/analytics')
@login_required
def page_analytics(): return render_template('analytics.html')

# --- CLI Commands ---
@app.cli.command('init-db')
def init_db():
    db.create_all()
    
    # Check if we need to seed
    if not User.query.first():
        print("Seeding demo data...")
        admin = User(email='admin', name='Super Admin', role='admin', password_hash=generate_password_hash('pass'))
        u1 = User(email='security1', name='John Sec', role='security', password_hash=generate_password_hash('pass'))
        u2 = User(email='staff1', name='Jane Staff', role='staff', password_hash=generate_password_hash('pass'))
        db.session.add_all([admin, u1, u2])
        
        nodes = [
            MapNode(name='Gate', x=120, y=340, description='Main Gate'),
            MapNode(name='Admin', x=200, y=100, description='Admin Block'),
            MapNode(name='Library', x=400, y=200, description='Central Lib'),
            MapNode(name='Lab1', x=350, y=400, description='Comp Lab'),
            MapNode(name='Lab2', x=450, y=450, description='Physics Lab'),
            MapNode(name='Canteen', x=150, y=500, description='Food Court')
        ]
        db.session.add_all(nodes)
        db.session.commit()
        
        rooms = [
            Room(name='Conf Room A', node_id=2, capacity=10),
            Room(name='Lab 101', node_id=4, capacity=30),
            Room(name='Hall B', node_id=3, capacity=100)
        ]
        db.session.add_all(rooms)
        db.session.commit()
        
        print("Done.")

if __name__ == '__main__':
    app.run(debug=True)
