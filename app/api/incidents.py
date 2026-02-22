import os
import uuid
import base64
from datetime import datetime
from app.encryption import encryption_manager
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Incident, IncidentComment, University
from app.utils import token_required, tenant_required
from app.ai_analyzer import analyzer
from werkzeug.utils import secure_filename

incident_bp = Blueprint('incidents', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@incident_bp.route('', methods=['GET'])
@tenant_required
def get_incidents(uni):
    """Get all incidents for a specific university"""
    query = Incident.query.options(db.joinedload(Incident.user)).filter_by(university_id=uni.id)
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    category = request.args.get('category')
    if category:
        query = query.filter_by(category=category)
    
    incidents = query.order_by(Incident.created_at.desc()).all()
    
    return jsonify([i.to_dict() for i in incidents]), 200


@incident_bp.route('/my', methods=['GET'])
@token_required
def get_my_incidents(current_user):
    """Get incidents created by current user"""
    incidents = Incident.query.options(db.joinedload(Incident.user)).filter_by(user_id=current_user.id)\
        .order_by(Incident.created_at.desc()).all()
    
    return jsonify([i.to_dict() for i in incidents]), 200


@incident_bp.route('/<int:id>', methods=['GET'])
def get_incident_detail(id):
    """Get single incident with comments"""
    incident = Incident.query.options(db.joinedload(Incident.user)).get_or_404(id)
    
    result = incident.to_dict()
    result['comments'] = [c.to_dict() for c in incident.comments]
    
    return jsonify(result), 200


@incident_bp.route('', methods=['POST'])
@token_required
def create_incident(current_user):
    """Create a new incident"""
    # Handle both form data and JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        description = request.form.get('description')
        category = request.form.get('category')
        severity = request.form.get('severity', 'medium')
        x = request.form.get('x', type=int)
        y = request.form.get('y', type=int)
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
    else:
        data = request.get_json() or {}
        description = data.get('description')
        category = data.get('category')
        severity = data.get('severity', 'medium')
        x = data.get('x')
        y = data.get('y')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
    
    if not description:
        return jsonify({'message': 'Description is required'}), 400
    
    # Handle image upload
    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"incident_{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = f'/uploads/{filename}'
    
    incident = Incident(
        university_id=current_user.university_id,
        user_id=current_user.id,
        description=description,
        category=category,
        severity=severity,
        x=x,
        y=y,
        latitude=latitude,
        longitude=longitude,
        image_url=image_url,
        status='open'
    )
    # Encrypt description before saving
    incident.description = encryption_manager.encrypt(description)
    
    db.session.add(incident)
    db.session.commit()
    
    return jsonify(incident.to_dict()), 201


@incident_bp.route('/<int:id>/status', methods=['PUT'])
@token_required
def update_incident_status(current_user, id):
    """Update incident status"""
    incident = Incident.query.get_or_404(id)
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['open', 'in_progress', 'resolved']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    incident.status = new_status
    
    if new_status == 'resolved':
        incident.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True}), 200


@incident_bp.route('/<int:id>/comment', methods=['POST'])
@token_required
def add_comment(current_user, id):
    """Add a comment to an incident"""
    incident = Incident.query.get_or_404(id)
    
    data = request.get_json()
    comment_text = data.get('comment')
    
    if not comment_text:
        return jsonify({'success': False, 'message': 'Comment is required'}), 400
    
    comment = IncidentComment(
        incident_id=incident.id,
        user_id=current_user.id,
        comment=comment_text
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': comment.to_dict()
    }), 201


@incident_bp.route('/analyze', methods=['POST'])
def analyze_incident():
    """Analyze incident image with AI"""
    image_bytes = None
    
    # Try to get image from different sources
    if 'image' in request.files:
        file = request.files['image']
        if file:
            image_bytes = file.read()
    elif request.is_json:
        data = request.get_json()
        if data.get('image_base64'):
            try:
                image_bytes = base64.b64decode(data['image_base64'])
            except Exception:
                return jsonify({'message': 'Invalid base64 image'}), 400
    
    if not image_bytes:
        return jsonify({'message': 'No image provided'}), 400
    
    result = analyzer.analyze_image(image_bytes)
    
    return jsonify({
        'category': result.get('category', 'unknown'),
        'severity': result.get('severity', 'medium'),
        'confidence': result.get('confidence', 0.5)
    }), 200


@incident_bp.route('/analyze/image', methods=['POST'])
def analyze_image():
    """Analyze uploaded image file"""
    if 'image' not in request.files:
        return jsonify({'message': 'No image file provided'}), 400
    
    file = request.files['image']
    if not file or not file.filename:
        return jsonify({'message': 'Empty file'}), 400
    
    image_bytes = file.read()
    result = analyzer.analyze_image(image_bytes)
    
    return jsonify({
        'category': result.get('category', 'security'),
        'severity': result.get('severity', 'medium'),
        'confidence': result.get('confidence', 0.78)
    }), 200
