import os
import werkzeug
from flask import Blueprint, request, jsonify, current_app, url_for
from app import db
from app.models import Incident, User
from app.utils import token_required
from app.ai_analyzer import analyzer
from werkzeug.utils import secure_filename
import json

incident_bp = Blueprint('incidents', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@incident_bp.route('/', methods=['GET'])
def get_incidents():
    status = request.args.get('status')
    if status:
        incidents = Incident.query.filter_by(status=status).all()
    else:
        incidents = Incident.query.all()
    
    return jsonify([i.to_dict() for i in incidents])

@incident_bp.route('/', methods=['POST'])
@token_required
def create_incident(current_user):
    # Form data
    category = request.form.get('category')
    description = request.form.get('description')
    x = request.form.get('x', 0)
    y = request.form.get('y', 0)
    
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Make unique
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            # Store relative path for serving
            image_path = unique_filename 
            
    incident = Incident(
        user_id=current_user.id,
        category=category,
        description=description,
        image_path=image_path,
        x=x,
        y=y
    )
    db.session.add(incident)
    db.session.commit()
    
    return jsonify(incident.to_dict()), 201

@incident_bp.route('/analyze', methods=['POST'])
def analyze_incident():
    # Can take 'incident_id' (to analyze existing) OR 'image' file directly
    incident_id = request.form.get('incident_id')
    
    image_bytes = None
    incident = None

    if incident_id:
        incident = Incident.query.get(incident_id)
        if not incident or not incident.image_path:
             return jsonify({'message': 'Incident found but no image to analyze'}), 400
        
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], incident.image_path)
        try:
            with open(full_path, 'rb') as f:
                image_bytes = f.read()
        except FileNotFoundError:
             return jsonify({'message': 'Image file missing'}), 404
             
    elif 'image' in request.files:
        file = request.files['image']
        if file:
            image_bytes = file.read()
    
    if not image_bytes:
        return jsonify({'message': 'No image provided'}), 400

    # Perform Analysis
    result = analyzer.analyze_image(image_bytes)

    # Save to incident if it exists
    if incident:
        incident.ai_labels = result['labels']
        incident.ai_severity = result['severity']
        incident.ai_recommendation = result['recommendation']
        incident.ai_analyzed_at = result['analyzed_at']
        db.session.commit()
        return jsonify(incident.to_dict())
    
    return jsonify(result)

@incident_bp.route('/<int:id>', methods=['GET'])
def get_incident_detail(id):
    incident = Incident.query.get_or_404(id)
    return jsonify(incident.to_dict())
