import random
from flask import Blueprint, request, jsonify
from app import db
from app.models import User, University
from app.utils import token_required
import jwt
import datetime
from config import Config

auth_bp = Blueprint('auth', __name__)
reset_codes = {}


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user associated with a specific university.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - university_id
          properties:
            email:
              type: string
              example: student@university.edu
            password:
              type: string
              example: password123
            university_id:
              type: integer
              example: 1
            name:
              type: string
            phone:
              type: string
            role:
              type: string
              default: student
    responses:
      201:
        description: User registered successfully
      400:
        description: Missing fields or email already exists
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    university_id = data.get('university_id')
    
    if not email or not password or not university_id:
        return jsonify({'success': False, 'message': 'Email, password, and university_id are required'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    new_user = User(
        name=data.get('name', ''),
        email=email,
        university_id=university_id,
        role=data.get('role', 'student'),
        phone=data.get('phone')
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Registration successful'
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login and get JWT token.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: student@university.edu
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            token:
              type: string
            user:
              type: object
      401:
        description: Invalid credentials
    """
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
    """
    Login using biometric signature/token from mobile.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            biometric_token:
              type: string
              description: Cryptographic signature from Android Keystore
    responses:
      200:
        description: Login successful
      400:
        description: Validation error
    """
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
@auth_bp.route('/link-child', methods=['POST'])
@token_required
def link_child(current_user):
    """Link a student to a parent account via email/CNIC or ID"""
    if current_user.role != 'parent':
        return jsonify({'message': 'Only parents can perform this action'}), 403
        
    data = request.json
    child_email = data.get('child_email')
    
    if not child_email:
        return jsonify({'message': 'Child email is required'}), 400
        
    child = User.query.filter_by(email=child_email, university_id=current_user.university_id).first()
    
    if not child:
        return jsonify({'message': 'Student not found in this university'}), 404
        
    if child in current_user.children:
        return jsonify({'message': 'Child already linked'}), 409
        
    current_user.children.append(child)
    db.session.commit()
    
    return jsonify({
        'message': 'Child linked successfully',
        'child': {'id': child.id, 'name': child.name}
    }), 200

@auth_bp.route('/my-children', methods=['GET'])
@token_required
def get_my_children(current_user):
    if current_user.role != 'parent':
        return jsonify({'message': 'Unauthorized'}), 403
        
    children = [c.to_dict() for c in current_user.children]
    return jsonify(children), 200
