import random
from flask import Blueprint, request, jsonify
from app import db
from app.models import User
import jwt
import datetime
from config import Config

auth_bp = Blueprint('auth', __name__)
reset_codes = {}

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    new_user = User(name=data.get('name'), email=data.get('email'), role=data.get('role', 'student'), phone=data.get('phone'))
    new_user.set_password(data.get('password'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        token = jwt.encode({'user_id': user.id, 'role': user.role, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, 
                          Config.JWT_SECRET, algorithm='HS256')
        return jsonify({'token': token, 'user': user.to_dict()}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/forgot', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        code = str(random.randint(100000, 999999))
        reset_codes[email] = code
        return jsonify({'message': 'Reset code generated', 'demo_code': code}), 200
    return jsonify({'message': 'Email not found'}), 404

@auth_bp.route('/reset', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')
    
    if reset_codes.get(email) == code:
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            del reset_codes[email]
            return jsonify({'message': 'Password reset successfully'}), 200
    return jsonify({'message': 'Invalid code or email'}), 400
