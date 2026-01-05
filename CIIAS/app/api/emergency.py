from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models import SOSAlert, EmergencyContact, SafeZone, MapNode, Notification
from app.utils import token_required
import math

emergency_bp = Blueprint('emergency', __name__)


@emergency_bp.route('/sos', methods=['POST'])
@token_required
def create_sos(current_user):
    """Create new SOS alert"""
    data = request.get_json()
    
    sos = SOSAlert(
        user_id=current_user.id,
        alert_type=data.get('alert_type'),
        message=data.get('message'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        status='active'
    )
    
    db.session.add(sos)
    db.session.commit()
    
    # Create notification for security personnel
    _notify_security(sos)
    
    return jsonify({
        'success': True,
        'sos_id': sos.id
    }), 201


def _notify_security(sos):
    """Create notifications for security users about SOS alert"""
    from app.models import User
    security_users = User.query.filter(User.role.in_(['security', 'admin'])).all()
    
    for user in security_users:
        notification = Notification(
            user_id=user.id,
            title=f'SOS Alert: {sos.alert_type}',
            message=sos.message or f'Emergency {sos.alert_type} alert triggered',
            type='sos',
            data={'sos_id': sos.id, 'latitude': sos.latitude, 'longitude': sos.longitude}
        )
        db.session.add(notification)
    
    db.session.commit()


@emergency_bp.route('/contacts', methods=['GET'])
def get_contacts():
    """Get all active emergency contacts"""
    contacts = EmergencyContact.query.filter_by(is_active=True).all()
    
    return jsonify({
        'contacts': [c.to_dict() for c in contacts]
    }), 200


@emergency_bp.route('/evacuation-routes', methods=['GET'])
def get_evacuation_routes():
    """Get evacuation routes from current location"""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    # Find emergency exits
    exits = MapNode.query.filter_by(is_emergency_exit=True).all()
    
    routes = []
    for exit_node in exits:
        if exit_node.latitude and exit_node.longitude:
            distance = _calculate_distance(lat, lng, exit_node.latitude, exit_node.longitude)
            routes.append({
                'id': exit_node.id,
                'name': exit_node.name,
                'path': [
                    {'lat': lat, 'lng': lng},
                    {'lat': exit_node.latitude, 'lng': exit_node.longitude}
                ],
                'distance': round(distance, 2),
                'estimated_time': f'{max(1, int(distance / 50))} min'
            })
    
    # Sort by distance
    routes.sort(key=lambda x: x['distance'])
    
    return jsonify(routes), 200


def _calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters (Haversine formula)"""
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')
    
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


@emergency_bp.route('/safe-zones', methods=['GET'])
def get_safe_zones():
    """Get all safe zones"""
    zones = SafeZone.query.all()
    
    return jsonify([z.to_dict() for z in zones]), 200


@emergency_bp.route('/sos/<int:id>/resolve', methods=['PUT'])
@token_required
def resolve_sos(current_user, id):
    """Resolve an SOS alert (security/admin only)"""
    if current_user.role not in ['security', 'admin']:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    sos = SOSAlert.query.get_or_404(id)
    sos.status = 'resolved'
    sos.resolved_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True}), 200
