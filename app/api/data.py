import csv
import io
from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Course, Enrollment, Department
from app.utils import token_required, ROLE_ADMIN

data_bp = Blueprint('data', __name__)

@data_bp.route('/migrate/students', methods=['POST'])
@token_required
def migrate_students(current_user):
    """Bulk import students from CSV (Nexus 2.0 Legacy Migrator)"""
    if current_user.role != ROLE_ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400
        
    stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
    csv_input = csv.DictReader(stream)
    
    count = 0
    errors = []
    
    for row in csv_input:
        try:
            email = row.get('email')
            if not email: continue
            
            if User.query.filter_by(email=email).first():
                errors.append(f"Email {email} already exists")
                continue
                
            user = User(
                name=row.get('name'),
                email=email,
                role='student',
                phone=row.get('phone'),
                dept_id=row.get('dept_id')
            )
            user.set_password(row.get('password', 'Ciias@123'))
            db.session.add(user)
            count += 1
        except Exception as e:
            errors.append(str(e))
            
    db.session.commit()
    return jsonify({
        'message': f'Successfully imported {count} students',
        'errors': errors
    }), 201

@data_bp.route('/search', methods=['GET'])
def universal_search():
    """Universal industrial search across students, staff, and courses"""
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify([])
        
    # Search Users
    users = User.query.filter(
        (User.name.ilike(f'%{q}%')) | (User.email.ilike(f'%{q}%'))
    ).limit(10).all()
    
    # Search Courses
    courses = Course.query.filter(
        (Course.name.ilike(f'%{q}%')) | (Course.code.ilike(f'%{q}%'))
    ).limit(10).all()
    
    results = []
    for u in users:
        results.append({
            'type': 'user', 
            'id': u.id, 
            'title': u.name, 
            'subtitle': u.role,
            'meta': u.email
        })
    for c in courses:
        results.append({
            'type': 'course', 
            'id': c.id, 
            'title': c.name, 
            'subtitle': c.code,
            'meta': f"{c.credit_hours} Credits"
        })
        
    return jsonify(results), 200
