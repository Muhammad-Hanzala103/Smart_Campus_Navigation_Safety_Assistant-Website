from flask import Blueprint, request, jsonify
from app import db
from app.models import Notification, User, University
from app.utils import token_required

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('', methods=['GET'])
@token_required
def get_notifications(current_user):
    """Get all notifications for current user and their university"""
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        university_id=current_user.university_id
    ).order_by(Notification.created_at.desc()).all()
    
    return jsonify([n.to_dict() for n in notifications]), 200


@notifications_bp.route('/<int:id>/read', methods=['PUT'])
@token_required
def mark_as_read(current_user, id):
    """Mark a notification as read"""
    notification = Notification.query.filter_by(
        id=id, 
        user_id=current_user.id
    ).first_or_404()
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True}), 200


@notifications_bp.route('/read-all', methods=['PUT'])
@token_required
def mark_all_as_read(current_user):
    """Mark all notifications as read"""
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    
    db.session.commit()
    
    return jsonify({'success': True}), 200


@notifications_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_notification(current_user, id):
    """Delete a notification"""
    notification = Notification.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'success': True}), 200


@notifications_bp.route('/register-token', methods=['POST'])
@token_required
def update_fcm_token(current_user):
    """Store FCM token for push notifications"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'success': False, 'message': 'Token required'}), 400
    
    current_user.fcm_token = token
    db.session.commit()
    
    return jsonify({'success': True}), 200
