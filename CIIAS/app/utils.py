from functools import wraps
from flask import request, jsonify, current_app, session, redirect, url_for, flash
import jwt
from app.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing!'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User invalid'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

def login_required(f):
    """Web session-based login required decorator"""
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
ROLE_SECURITY = 'security'
ROLE_STAFF = 'staff'
ROLE_STUDENT = 'student'

# Permission definitions
PERMISSIONS = {
    ROLE_ADMIN: ['dashboard', 'incidents', 'incidents.create', 'incidents.edit', 'incidents.delete', 
                 'map', 'users', 'users.create', 'users.edit', 'users.delete', 
                 'settings', 'analytics', 'audit_logs', 'academic', 'library', 'transport', 'cafeteria', 'financial', 'chat'],
    ROLE_SECURITY: ['dashboard', 'incidents', 'incidents.create', 'incidents.edit', 
                    'map', 'analytics', 'transport'],
    ROLE_STAFF: ['dashboard', 'incidents', 'incidents.create', 'map', 'academic', 'library'],
    ROLE_STUDENT: ['dashboard', 'incidents.create', 'library', 'transport', 'cafeteria', 'financial', 'chat']
}

def has_permission(user_role, permission):
    """Check if a role has a specific permission"""
    return permission in PERMISSIONS.get(user_role, [])
