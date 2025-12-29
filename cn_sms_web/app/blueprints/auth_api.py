"""
Authentication API Blueprint
Handles user registration, login, and password reset flows.
Designed for Android client integration.
"""
from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

from app.extensions import db
from app.models import User, AuditLog
from app.utils.jwt_auth import create_access_token, auth_required
from app.utils.validators import validate_email, validate_password, validate_name
from app.services.email_service import generate_reset_token, verify_reset_token

logger = logging.getLogger(__name__)

auth_api_bp = Blueprint('auth_api', __name__)


@auth_api_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    Request JSON:
        {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123"
        }
    
    Response:
        201: {"message": "User registered successfully", "user_id": 1}
        400: {"error": "Validation error", "message": "..."}
        409: {"error": "Email already registered"}
    """
    data = request.get_json() or {}
    
    # Validate input
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    valid, error = validate_name(name)
    if not valid:
        return jsonify({'error': 'Validation error', 'message': error}), 400
    
    valid, error = validate_email(email)
    if not valid:
        return jsonify({'error': 'Validation error', 'message': error}), 400
    
    valid, error = validate_password(password)
    if not valid:
        return jsonify({'error': 'Validation error', 'message': error}), 400
    
    # Check if email exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create user
    user = User(
        full_name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role='user',  # Default role, can be upgraded by admin
        is_active=True
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Audit log
    log = AuditLog(user_id=user.id, action='USER_REGISTERED', 
                   details=f'New user registered: {email}',
                   ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    
    logger.info(f"User registered: {email}")
    
    return jsonify({
        'message': 'User registered successfully',
        'user_id': user.id
    }), 201


@auth_api_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token.
    """
    try:
        # force=True ignores Content-Type header (handles text/plain or missing type)
        # silent=True returns None instead of crashing on bad JSON
        data = request.get_json(force=True, silent=True)
        
        if data is None:
             return jsonify({'error': 'Invalid JSON body or empty request'}), 400
             
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            log = AuditLog(action='LOGIN_FAILED', 
                           details=f'Failed login attempt for: {email}',
                           ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate JWT token
        token = create_access_token(user.id, user.role)
        
        # Audit log
        log = AuditLog(user_id=user.id, action='LOGIN_SUCCESS',
                       details='User logged in',
                       ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user.id,
                'name': user.full_name,
                'email': user.email,
                'role': user.role
            }
        }), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@auth_api_bp.route('/password-reset-request', methods=['POST'])
def password_reset_request():
    """
    Request password reset. Sends email or returns token in dev mode.
    
    Request JSON:
        {"email": "john@example.com"}
    
    Response:
        200: {"message": "Reset instructions sent"}
        200 (dev): {"message": "...", "token": "...", "dev_mode": true}
        404: {"error": "Email not found"}
    """
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Don't reveal if email exists (security best practice)
        # But for dev/testing, we'll return 404
        return jsonify({'error': 'Email not found'}), 404
    
    # Generate reset token
    token = generate_reset_token(email)
    
    # Audit log
    log = AuditLog(user_id=user.id, action='PASSWORD_RESET_REQUESTED',
                   details='Password reset token generated',
                   ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    
    # Dev mode: return token directly
    if current_app.config.get('PASSWORD_RESET_DEV_MODE'):
        logger.info(f"DEV MODE: Reset token for {email}: {token}")
        return jsonify({
            'message': 'Password reset token generated (dev mode)',
            'token': token,
            'dev_mode': True,
            'note': 'In production, this token would be sent via email'
        }), 200
    
    # Production: send email
    reset_url = f"{request.host_url}reset-password?token={token}&email={email}"
    from app.services.email_service import send_reset_email
    send_reset_email(email, token, reset_url)
    
    return jsonify({
        'message': 'If the email exists, reset instructions have been sent'
    }), 200


@auth_api_bp.route('/password-reset-confirm', methods=['POST'])
def password_reset_confirm():
    """
    Confirm password reset with token.
    
    Request JSON:
        {
            "email": "john@example.com",
            "token": "reset-token-here",
            "new_password": "newSecurePass123"
        }
    
    Response:
        200: {"message": "Password reset successful"}
        400: {"error": "Invalid or expired token"}
    """
    data = request.get_json() or {}
    
    email = data.get('email', '').strip().lower()
    token = data.get('token', '')
    new_password = data.get('new_password', '')
    
    if not all([email, token, new_password]):
        return jsonify({'error': 'Email, token, and new_password are required'}), 400
    
    valid, error = validate_password(new_password)
    if not valid:
        return jsonify({'error': 'Validation error', 'message': error}), 400
    
    # Verify token
    try:
        token_email = verify_reset_token(token)
        if token_email.lower() != email:
            raise ValueError("Email mismatch")
    except Exception as e:
        logger.warning(f"Invalid reset token for {email}: {e}")
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    # Update password
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    # Audit log
    log = AuditLog(user_id=user.id, action='PASSWORD_RESET_SUCCESS',
                   details='Password was reset via token',
                   ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    
    logger.info(f"Password reset successful for: {email}")
    
    return jsonify({'message': 'Password reset successful'}), 200


@auth_api_bp.route('/users/<int:user_id>', methods=['GET'])
@auth_required
def get_user(user_id):
    """
    Get user information. Protected endpoint.
    Users can only access their own info unless admin.
    
    Response:
        200: {"id": 1, "name": "...", "email": "...", "role": "..."}
        403: {"error": "Forbidden"}
        404: {"error": "User not found"}
    """
    # Check authorization: owner or admin
    if g.current_user_id != user_id and g.current_user_role != 'admin':
        return jsonify({'error': 'Forbidden', 
                       'message': 'You can only access your own profile'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'name': user.full_name,
        'email': user.email,
        'role': user.role,
        'department': user.department,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_login': user.last_login.isoformat() if user.last_login else None
    }), 200


@auth_api_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user():
    """
    Get current authenticated user's info.
    Shortcut for /users/<id> using token.
    """
    return get_user(g.current_user_id)
