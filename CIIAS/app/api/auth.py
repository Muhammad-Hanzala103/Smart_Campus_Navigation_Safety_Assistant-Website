import random
from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.utils import token_required
import jwt
import datetime
from config import Config

auth_bp = Blueprint('auth', __name__)
reset_codes = {}


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    new_user = User(
        name=data.get('name', ''),
        email=data.get('email'),
        role=data.get('role', 'student'),
        phone=data.get('phone')
    )
    new_user.set_password(data.get('password'))
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Registration successful'
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and get JWT token"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        if not user.is_active:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        token = jwt.encode({
            'user_id': user.id,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        }, Config.JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'profile_photo': user.profile_photo
            }
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('/forgot', methods=['POST'])
def forgot_password():
    """Request password reset code"""
    data = request.get_json()
    email = data.get('email')
    
    user = User.query.filter_by(email=email).first()
    if user:
        code = str(random.randint(100000, 999999))
        reset_codes[email] = {
            'code': code,
            'expires': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }
        # In production, send this code via email
        return jsonify({
            'success': True,
            'message': 'Reset email sent',
            'demo_code': code  # Remove in production
        }), 200
    
    return jsonify({'success': False, 'message': 'Email not found'}), 404


@auth_bp.route('/reset', methods=['POST'])
def reset_password():
    """Reset password with code or token"""
    data = request.get_json()
    email = data.get('email')
    code = data.get('code') or data.get('token')
    new_password = data.get('new_password')
    
    if not email or not code or not new_password:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    reset_data = reset_codes.get(email)
    if reset_data and reset_data['code'] == code:
        if datetime.datetime.utcnow() > reset_data['expires']:
            del reset_codes[email]
            return jsonify({'success': False, 'message': 'Code expired'}), 400
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            del reset_codes[email]
            return jsonify({'success': True, 'message': 'Password reset successfully'}), 200
    
    return jsonify({'success': False, 'message': 'Invalid code or email'}), 400


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Change password for authenticated user"""
    data = request.get_json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'success': False, 'message': 'Current and new password required'}), 400
    
    if not current_user.check_password(current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401
    
    current_user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password changed successfully'}), 200


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout user (stateless - just returns success)"""
    # In a stateful implementation, you would invalidate the token here
    # For JWT, the token remains valid until expiration
    return jsonify({'success': True}), 200

@auth_bp.route('/biometric-login', methods=['POST'])
def biometric_login():
    """Login using biometric signature/token from mobile"""
    data = request.get_json()
    bio_token = data.get('biometric_token')
    email = data.get('email')
    
    # In production, verify the cryptographic signature of bio_token
    # For now, we trust the mobile app if it sends a valid email + mock token
    
    if not email or not bio_token:
        return jsonify({'message': 'Missing credentials'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user:
         return jsonify({'message': 'User not found'}), 404
         
    # Generate Token
    token = jwt.encode({
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }, Config.JWT_SECRET, algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
    }), 200
