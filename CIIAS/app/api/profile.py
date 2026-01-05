import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User
from app.utils import token_required
from werkzeug.utils import secure_filename
from PIL import Image

profile_bp = Blueprint('profile', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@profile_bp.route('', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile"""
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'role': current_user.role,
        'phone': current_user.phone,
        'profile_photo': current_user.profile_photo,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None
    }), 200


@profile_bp.route('', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile (name, phone)"""
    data = request.get_json()
    
    if 'name' in data:
        current_user.name = data['name']
    if 'phone' in data:
        current_user.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    }), 200


@profile_bp.route('/photo', methods=['POST'])
@token_required
def upload_photo(current_user):
    """Upload profile photo"""
    if 'photo' not in request.files:
        return jsonify({'success': False, 'message': 'No photo provided'}), 400
    
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'File type not allowed'}), 400
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"profile_{current_user.id}_{uuid.uuid4().hex}.{ext}"
    
    # Save file
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # Create thumbnail (optional, for optimization)
    try:
        img = Image.open(filepath)
        img.thumbnail((256, 256))
        img.save(filepath)
    except Exception:
        pass  # If PIL fails, keep original
    
    # Update user profile photo path
    current_user.profile_photo = f'/uploads/{filename}'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'photo_url': current_user.profile_photo
    }), 200


@profile_bp.route('', methods=['DELETE'])
@token_required
def delete_account(current_user):
    """Deactivate user account"""
    current_user.is_active = False
    db.session.commit()
    
    return jsonify({'success': True}), 200
