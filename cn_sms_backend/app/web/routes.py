from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.models import User, Incident, Booking, AuditLog
from app import db
from functools import wraps

web_bp = Blueprint('web', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function

@web_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.role in ['admin', 'security', 'staff']:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            return redirect(url_for('web.dashboard'))
        else:
            flash('Invalid credentials or insufficient permissions')
    return render_template('login.html')

@web_bp.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('web.login'))

@web_bp.route('/admin/dashboard')
@login_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'open_incidents': Incident.query.filter_by(status='open').count(),
        'pending_bookings': Booking.query.filter_by(status='pending').count()
    }
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', stats=stats, activity=recent_activity)

@web_bp.route('/admin/map')
@login_required
def map_editor():
    return render_template('map_editor.html')

@web_bp.route('/admin/incidents')
@login_required
def incidents():
    all_incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    return render_template('incidents.html', incidents=all_incidents)

@web_bp.route('/admin/bookings')
@login_required
def bookings():
    all_bookings = Booking.query.order_by(Booking.start_time.desc()).all()
    return render_template('bookings.html', bookings=all_bookings)

@web_bp.route('/admin/users')
@login_required
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@web_bp.route('/admin/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@web_bp.route('/')
def index():
    return redirect(url_for('web.login'))
