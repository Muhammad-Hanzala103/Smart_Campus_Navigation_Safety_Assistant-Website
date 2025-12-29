"""
Incident & Data API Blueprint
Handles incident CRUD, AI analysis, and data retrieval.
"""
from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json
import logging

from app.extensions import db
from app.models import Incident, AuditLog, User
from app.utils.jwt_auth import auth_required
from app.utils.validators import validate_incident_data, allowed_file
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


@api_bp.route('/status')
def status():
    """
    Health check endpoint.
    
    Response:
        200: {"status": "online", "ai_mode": "mock|hf", "version": "1.0"}
    """
    return jsonify({
        'status': 'online',
        'ai_mode': current_app.config.get('AI_MODE', 'mock'),
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


@api_bp.route('/incidents', methods=['GET'])
@auth_required
def get_incidents():
    """
    List all incidents with optional filters.
    
    Query params:
        - status: Filter by status (new, under_review, resolved)
        - severity: Filter by AI severity (LOW, MEDIUM, HIGH, CRITICAL)
        - limit: Max results (default 50)
        - offset: Pagination offset
    
    Response:
        200: {"incidents": [...], "total": 100, "limit": 50, "offset": 0}
    """
    # Query params
    status_filter = request.args.get('status')
    severity_filter = request.args.get('severity')
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    
    # Build query
    query = Incident.query
    
    if status_filter:
        query = query.filter(Incident.status == status_filter)
    if severity_filter:
        query = query.filter(Incident.ai_severity == severity_filter.upper())
    
    total = query.count()
    incidents = query.order_by(Incident.created_at.desc()) \
                    .offset(offset).limit(limit).all()
    
    results = []
    for inc in incidents:
        results.append({
            'id': inc.id,
            'description': inc.description,
            'category': inc.category,
            'location_name': inc.location_name,
            'lat': inc.x,
            'lng': inc.y,
            'status': inc.status,
            'image_url': f"/{inc.image_path}" if inc.image_path else None,
            'ai_labels': json.loads(inc.ai_labels) if inc.ai_labels else [],
            'ai_severity': inc.ai_severity,
            'ai_risk_score': inc.ai_risk_score,
            'ai_recommendation': inc.ai_recommendation,
            'ai_analyzed_at': inc.ai_analyzed_at.isoformat() if inc.ai_analyzed_at else None,
            'created_at': inc.created_at.isoformat(),
            'updated_at': inc.updated_at.isoformat() if inc.updated_at else None,
            'reporter_id': inc.user_id,
            'assigned_to_id': inc.assigned_to_id
        })
    
    return jsonify({
        'incidents': results,
        'total': total,
        'limit': limit,
        'offset': offset
    })


@api_bp.route('/incidents/<int:incident_id>', methods=['GET'])
@auth_required
def get_incident(incident_id):
    """
    Get single incident details.
    
    Response:
        200: {incident object}
        404: {"error": "Incident not found"}
    """
    inc = Incident.query.get(incident_id)
    if not inc:
        return jsonify({'error': 'Incident not found'}), 404
    
    return jsonify({
        'id': inc.id,
        'description': inc.description,
        'category': inc.category,
        'location_name': inc.location_name,
        'lat': inc.x,
        'lng': inc.y,
        'status': inc.status,
        'image_url': f"/{inc.image_path}" if inc.image_path else None,
        'ai_labels': json.loads(inc.ai_labels) if inc.ai_labels else [],
        'ai_severity': inc.ai_severity,
        'ai_risk_score': inc.ai_risk_score,
        'ai_recommendation': inc.ai_recommendation,
        'ai_analyzed_at': inc.ai_analyzed_at.isoformat() if inc.ai_analyzed_at else None,
        'created_at': inc.created_at.isoformat(),
        'resolution_notes': inc.resolution_notes,
        'reporter_id': inc.user_id,
        'assigned_to_id': inc.assigned_to_id
    })


@api_bp.route('/incidents', methods=['POST'])
@auth_required
def create_incident():
    """
    Create a new incident with image upload.
    
    Request (multipart/form-data):
        - description: String (required)
        - category: String (optional)
        - location: String (optional)
        - lat: Float (optional)
        - lng: Float (optional)
        - image: File (required for AI analysis)
    
    Response:
        201: {"message": "...", "incident_id": 1, "ai_result": {...}}
        400: {"error": "..."}
    """
    # Validate image
    if 'image' not in request.files:
        return jsonify({'error': 'Image file is required'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400
    
    # Get form data
    description = request.form.get('description', '').strip()
    category = request.form.get('category', 'Unspecified')
    location = request.form.get('location', 'Unknown')
    lat = float(request.form.get('lat', 0))
    lng = float(request.form.get('lng', 0))
    
    if not description:
        return jsonify({'error': 'Description is required'}), 400
    
    # Save image
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{filename}"
    
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'incidents')
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, unique_filename)
    file.save(file_path)
    
    # Read file for AI analysis
    with open(file_path, 'rb') as f:
        image_bytes = f.read()
    
    # Run AI analysis
    ai_result = ai_service.analyze_image(image_bytes)
    
    # Create incident
    incident = Incident(
        user_id=g.current_user_id,
        description=description,
        category=category,
        location_name=location,
        x=lat,
        y=lng,
        image_path=f"static/uploads/incidents/{unique_filename}",
        status='new',
        ai_labels=json.dumps(ai_result['labels']),
        ai_risk_score=ai_result['risk_score'],
        ai_severity=ai_result['severity'],
        ai_recommendation=ai_result['recommendation'],
        ai_analyzed_at=ai_result['analyzed_at']
    )
    
    db.session.add(incident)
    db.session.commit()
    
    # Audit log
    log = AuditLog(
        user_id=g.current_user_id,
        action='INCIDENT_CREATED',
        details=f'Incident #{incident.id} created. AI Severity: {ai_result["severity"]}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    logger.info(f"Incident #{incident.id} created by user {g.current_user_id}")
    
    return jsonify({
        'message': 'Incident created and analyzed',
        'incident_id': incident.id,
        'ai_result': {
            'labels': ai_result['labels'],
            'severity': ai_result['severity'],
            'risk_score': ai_result['risk_score'],
            'recommendation': ai_result['recommendation']
        }
    }), 201


@api_bp.route('/incidents/analyze', methods=['POST'])
@auth_required
def analyze_incident():
    """
    Run AI analysis on an existing incident or uploaded image.
    
    Request (multipart or JSON):
        Option 1: {"incident_id": 1}
        Option 2: multipart with "image" file
    
    Response:
        200: {"labels": [...], "severity": "...", "risk_score": 85, "recommendation": "..."}
        400: {"error": "..."}
    """
    incident_id = None
    image_bytes = None
    
    # Check for incident_id in form or JSON
    if request.content_type and 'multipart' in request.content_type:
        incident_id = request.form.get('incident_id')
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                image_bytes = file.read()
    else:
        data = request.get_json() or {}
        incident_id = data.get('incident_id')
    
    # Get image from incident if no direct upload
    incident = None
    if incident_id and not image_bytes:
        incident = Incident.query.get(incident_id)
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        if not incident.image_path:
            return jsonify({'error': 'Incident has no image'}), 400
        
        image_path = os.path.join(current_app.root_path, '..', incident.image_path)
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
        else:
            return jsonify({'error': 'Image file not found'}), 404
    
    if not image_bytes:
        return jsonify({'error': 'No image provided. Send incident_id or image file.'}), 400
    
    # Run AI analysis
    ai_result = ai_service.analyze_image(image_bytes)
    
    # Update incident if analyzing existing one
    if incident:
        incident.ai_labels = json.dumps(ai_result['labels'])
        incident.ai_risk_score = ai_result['risk_score']
        incident.ai_severity = ai_result['severity']
        incident.ai_recommendation = ai_result['recommendation']
        incident.ai_analyzed_at = ai_result['analyzed_at']
        db.session.commit()
        
        # Audit log
        log = AuditLog(
            user_id=g.current_user_id,
            action='AI_ANALYSIS_RUN',
            details=f'AI analysis for incident #{incident.id}. Result: {ai_result["severity"]}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"AI analysis run on incident #{incident.id}")
    
    return jsonify({
        'labels': ai_result['labels'],
        'severity': ai_result['severity'],
        'risk_score': ai_result['risk_score'],
        'recommendation': ai_result['recommendation'],
        'analyzed_at': ai_result['analyzed_at'].isoformat() if hasattr(ai_result['analyzed_at'], 'isoformat') else ai_result['analyzed_at']
    })


@api_bp.route('/incidents/<int:incident_id>/status', methods=['PATCH'])
@auth_required
def update_incident_status(incident_id):
    """
    Update incident status.
    
    Request JSON:
        {"status": "resolved", "resolution_notes": "Issue handled."}
    
    Response:
        200: {"message": "Status updated", "status": "resolved"}
        400: {"error": "Invalid status"}
    """
    incident = Incident.query.get(incident_id)
    if not incident:
        return jsonify({'error': 'Incident not found'}), 404
    
    data = request.get_json() or {}
    new_status = data.get('status')
    
    valid_statuses = ['new', 'under_review', 'escalated', 'resolved', 'closed']
    if new_status not in valid_statuses:
        return jsonify({
            'error': 'Invalid status',
            'valid_statuses': valid_statuses
        }), 400
    
    old_status = incident.status
    incident.status = new_status
    
    if data.get('resolution_notes'):
        incident.resolution_notes = data['resolution_notes']
    
    if data.get('assigned_to_id'):
        incident.assigned_to_id = data['assigned_to_id']
    
    db.session.commit()
    
    # Audit log
    log = AuditLog(
        user_id=g.current_user_id,
        action='INCIDENT_STATUS_CHANGED',
        details=f'Incident #{incident_id} status: {old_status} -> {new_status}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': 'Status updated',
        'incident_id': incident_id,
        'status': new_status
    })


# --- Map Node API ---

@api_bp.route('/map/nodes', methods=['GET'])
@auth_required
def get_map_nodes():
    """Get all map nodes."""
    from app.models import MapNode
    nodes = MapNode.query.all()
    results = [{'id': n.id, 'name': n.name, 'x': n.x, 'y': n.y, 'desc': n.description} for n in nodes]
    return jsonify({'nodes': results})


@api_bp.route('/map/nodes', methods=['POST'])
@auth_required
def create_map_node():
    """Create a new map node."""
    from app.models import MapNode
    data = request.get_json() or {}
    
    if not data.get('name') or 'x' not in data or 'y' not in data:
        return jsonify({'error': 'Missing name, x, or y'}), 400
        
    node = MapNode(
        name=data['name'],
        x=float(data['x']),
        y=float(data['y']),
        description=data.get('description', ''),
        node_type=data.get('type', 'general')
    )
    db.session.add(node)
    db.session.commit()
    
    return jsonify({
        'message': 'Node created',
        'id': node.id,
        'node': {'id': node.id, 'name': node.name, 'x': node.x, 'y': node.y}
    }), 201


@api_bp.route('/map/nodes/<int:node_id>', methods=['DELETE'])
@auth_required
def delete_map_node(node_id):
    """Delete a map node."""
    from app.models import MapNode
    node = MapNode.query.get(node_id)
    if not node:
        return jsonify({'error': 'Node not found'}), 404
        
    db.session.delete(node)
    db.session.commit()
    return jsonify({'message': 'Node deleted'})
