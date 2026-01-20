from functools import wraps
from flask import request, jsonify, current_app, session, redirect, url_for, flash
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=["HS256"])
            from app.models import User
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User invalid'}), 401
        except Exception as e:
            return jsonify({'message': f'Token invalid: {str(e)}'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page')
            return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Role-based access control decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page')
                return redirect(url_for('web.login'))
            
            user_role = session.get('user_role', 'student')
            if user_role not in roles:
                flash('You do not have permission to access this page')
                return redirect(url_for('web.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Role constants
ROLE_ADMIN = 'admin'
ROLE_HOD = 'hod'
ROLE_TEACHER = 'teacher'
ROLE_FINANCE = 'finance'
ROLE_TRANSPORT = 'transport_mgr'
ROLE_CAFETERIA = 'cafeteria_mgr'
ROLE_LIBRARIAN = 'librarian'
ROLE_REGISTRAR = 'registrar'
ROLE_HR = 'hr'
ROLE_STAFF = 'staff'
ROLE_SECURITY = 'security'
ROLE_STUDENT = 'student'

# Permission definitions
PERMISSIONS = {
    ROLE_ADMIN: ['*'],
    ROLE_HOD: ['dashboard', 'incidents', 'department.staff', 'department.reports', 'academic.manage', 'analytics'],
    ROLE_TEACHER: ['dashboard', 'academic.lms', 'academic.grading', 'academic.attendance', 'chat', 'incidents.create'],
    ROLE_FINANCE: ['dashboard', 'financial.fee', 'financial.payroll', 'audit_logs'],
    ROLE_TRANSPORT: ['dashboard', 'transport.fleet', 'transport.drivers', 'map', 'incidents.create'],
    ROLE_CAFETERIA: ['dashboard', 'cafeteria.menu', 'cafeteria.orders'],
    ROLE_LIBRARIAN: ['dashboard', 'library.books', 'library.issues'],
    ROLE_REGISTRAR: ['dashboard', 'users.manage', 'academic.records'],
    ROLE_HR: ['dashboard', 'users.staff', 'audit_logs'],
    ROLE_STAFF: ['dashboard', 'academic.view', 'chat'],
    ROLE_SECURITY: ['dashboard', 'incidents', 'incidents.manage', 'map', 'transport.view'],
    ROLE_STUDENT: ['dashboard', 'academic.view', 'library.view', 'transport.view', 'cafeteria.view', 'chat', 'incidents.create']
}

def has_permission(user_role, permission):
    """Check if a role has a specific permission (supports wildcard and prefix)"""
    role_perms = PERMISSIONS.get(user_role, [])
    if '*' in role_perms:
        return True
    
    # Check for direct match or prefix match (e.g. 'academic' matches 'academic.manage')
    for p in role_perms:
        if p == permission or p.startswith(f"{permission}."):
            return True
    return False
