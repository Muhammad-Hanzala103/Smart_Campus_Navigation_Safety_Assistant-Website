from flask import Blueprint, request, jsonify
from app import db
from app.models import ChatMessage, User
from app.utils import token_required
from datetime import datetime
from sqlalchemy import or_, and_

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    """Get list of recent conversations"""
    # This is a simplified query; in a real app, this would be more complex to group by user
    # For now, let's return users the current user has chatted with
    
    # Subquery to find the last message between users
    sent = db.session.query(ChatMessage.receiver_id).filter(ChatMessage.sender_id == current_user.id)
    received = db.session.query(ChatMessage.sender_id).filter(ChatMessage.receiver_id == current_user.id)
    
    contact_ids = sent.union(received).all()
    contact_ids = [c[0] for c in contact_ids]
    
    contacts = User.query.filter(User.id.in_(contact_ids)).all()
    
    # Enrich with last message info if needed (skipping for basic implementation)
    return jsonify([{
        'user_id': u.id,
        'name': u.name,
        'profile_photo': u.profile_photo,
        'role': u.role
    } for u in contacts]), 200

@chat_bp.route('/messages/<int:contact_id>', methods=['GET'])
@token_required
def get_messages(current_user, contact_id):
    """Get chat history with a specific user"""
    messages = ChatMessage.query.filter(
        or_(
            and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id == contact_id),
            and_(ChatMessage.receiver_id == current_user.id, ChatMessage.sender_id == contact_id)
        )
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return jsonify([m.to_dict() for m in messages]), 200

@chat_bp.route('/send', methods=['POST'])
@token_required
def send_message(current_user):
    """Send a chat message"""
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    message_text = data.get('message')
    
    if not receiver_id or not message_text:
        return jsonify({'error': 'Missing receiver_id or message'}), 400
        
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'error': 'User not found'}), 404
        
    msg = ChatMessage(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        message=message_text
    )
    
    db.session.add(msg)
    db.session.commit()
    
    return jsonify(msg.to_dict()), 201
