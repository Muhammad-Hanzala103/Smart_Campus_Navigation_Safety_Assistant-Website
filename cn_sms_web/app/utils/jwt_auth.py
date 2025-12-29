"""
JWT Authentication Utilities
Provides decorators and helpers for JWT-based API authentication.
"""
from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from datetime import datetime, timedelta


def create_access_token(user_id: int, role: str) -> str:
    """
    Create a JWT access token for a user.
    
    Args:
        user_id: The user's database ID
        role: The user's role (admin, officer, analyst)
    
    Returns:
        Encoded JWT token string
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    }
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token string
    
    Returns:
        Decoded payload dict
    
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(
        token,
        current_app.config['JWT_SECRET_KEY'],
        algorithms=['HS256']
    )


def get_token_from_header():
    """Extract JWT token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def auth_required(f):
    """
    Decorator to require authentication (JWT or Session).
    Sets g.current_user_id and g.current_user_role on success.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask_login import current_user
        
        token = get_token_from_header()
        
        # 1. Try JWT Token
        if token:
            try:
                payload = decode_token(token)
                g.current_user_id = payload['user_id']
                g.current_user_role = payload.get('role', 'user')
                return f(*args, **kwargs)
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                pass # Fallthrough to session check
        
        # 2. Try Session (Flask-Login)
        if current_user.is_authenticated:
            g.current_user_id = current_user.id
            g.current_user_role = current_user.role
            return f(*args, **kwargs)

        # 3. Fail
        return jsonify({
            'error': 'Authorization required',
            'message': 'Missing valid JWT token or active session.'
        }), 401

    return decorated


def admin_required(f):
    """
    Decorator requiring admin role.
    Must be used after @auth_required.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.get('current_user_role') != 'admin':
            return jsonify({
                'error': 'Forbidden',
                'message': 'Admin access required for this endpoint.'
            }), 403
        return f(*args, **kwargs)
    return decorated


def role_required_api(roles: list):
    """
    Decorator factory for role-based access in API endpoints.
    
    Args:
        roles: List of allowed roles (e.g., ['admin', 'officer'])
    
    Usage:
        @app.route('/officers-only')
        @auth_required
        @role_required_api(['admin', 'officer'])
        def officers_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.get('current_user_role') not in roles:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Access restricted to: {", ".join(roles)}'
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
