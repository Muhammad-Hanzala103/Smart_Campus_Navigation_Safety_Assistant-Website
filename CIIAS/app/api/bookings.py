from flask import Blueprint, request, jsonify
from app import db
from app.models import Booking
from app.utils import token_required
from datetime import datetime

booking_bp = Blueprint('bookings', __name__)

@booking_bp.route('/', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    return jsonify([b.to_dict() for b in bookings])

@booking_bp.route('/', methods=['POST'])
@token_required
def create_booking(current_user):
    data = request.get_json()
    room_id = data.get('room_id')
    try:
        start_time = datetime.fromisoformat(data.get('start_time'))
        end_time = datetime.fromisoformat(data.get('end_time'))
    except ValueError:
        return jsonify({'message': 'Invalid time format. Use ISO 8601'}), 400
        
    if start_time >= end_time:
        return jsonify({'message': 'Start time must be before end time'}), 400

    conflict = Booking.query.filter(
        Booking.room_id == room_id, Booking.status != 'cancelled',
        Booking.start_time < end_time, Booking.end_time > start_time
    ).first()
    
    if conflict:
        return jsonify({'message': 'Conflict detected', 'conflict_with': conflict.to_dict()}), 409
        
    booking = Booking(user_id=current_user.id, room_id=room_id, start_time=start_time, end_time=end_time, status='pending')
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking.to_dict()), 201

@booking_bp.route('/<int:id>/status', methods=['PUT'])
@token_required
def update_status(current_user, id):
    if current_user.role not in ['admin', 'staff', 'security']:
        return jsonify({'message': 'Permission denied'}), 403
    booking = Booking.query.get_or_404(id)
    data = request.get_json()
    new_status = data.get('status')
    if new_status in ['pending', 'approved', 'rejected', 'cancelled']:
        booking.status = new_status
        db.session.commit()
        return jsonify(booking.to_dict())
    return jsonify({'message': 'Invalid status'}), 400
