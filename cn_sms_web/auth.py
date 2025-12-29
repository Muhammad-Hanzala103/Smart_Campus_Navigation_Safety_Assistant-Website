from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
        
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(email=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'status': 'ok', 'user': {'id': user.id, 'role': user.role, 'email': user.email}})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'logged out'})
