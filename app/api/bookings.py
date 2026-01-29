from datetime import datetime, time
from flask import Blueprint, request, jsonify
from app import db
from app.models import Booking, Room
from app.utils import token_required

booking_bp = Blueprint('bookings', __name__)


@booking_bp.route('', methods=['GET'])
def get_bookings():
    """Get all bookings"""
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@booking_bp.route('/my', methods=['GET'])
@token_required
def get_my_bookings(current_user):
    """Get current user's bookings"""
    bookings = Booking.query.filter_by(user_id=current_user.id)\
        .order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@booking_bp.route('', methods=['POST'])
@token_required
def create_booking(current_user):
    """Create a new booking"""
    data = request.get_json()
    
    room_id = data.get('room_id')
    date_str = data.get('date')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    purpose = data.get('purpose')
    
    # Validate required fields
    if not all([room_id, date_str, start_time_str, end_time_str]):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Verify room exists
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'success': False, 'message': 'Room not found'}), 404
    
    # Parse date and times
    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date/time format. Use YYYY-MM-DD and HH:MM'}), 400
    
    if start_time >= end_time:
        return jsonify({'success': False, 'message': 'Start time must be before end time'}), 400
    
    # Check for conflicts
    conflict = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.date == booking_date,
        Booking.status.in_(['pending', 'approved']),
        Booking.start_time < end_time,
        Booking.end_time > start_time
    ).first()
    
    if conflict:
        return jsonify({
            'success': False,
            'message': 'Time slot already booked',
            'conflict_with': conflict.to_dict()
        }), 409
    
    booking = Booking(
        user_id=current_user.id,
        room_id=room_id,
        date=booking_date,
        start_time=start_time,
        end_time=end_time,
        purpose=purpose,
        status='pending'
    )
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'booking': booking.to_dict()
    }), 201


@booking_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_booking(current_user, id):
    """Update booking (status or details)"""
    booking = Booking.query.get_or_404(id)
    
    # Only allow owner or admin/staff/security to modify
    if booking.user_id != current_user.id and current_user.role not in ['admin', 'staff', 'security']:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    
    # Update status if provided
    if 'status' in data:
        new_status = data['status']
        if new_status in ['pending', 'approved', 'rejected', 'cancelled']:
            booking.status = new_status
    
    # Update purpose if provided
    if 'purpose' in data:
        booking.purpose = data['purpose']
    
    db.session.commit()
    
    return jsonify({'success': True, 'booking': booking.to_dict()}), 200


@booking_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_booking(current_user, id):
    """Delete (cancel) a booking"""
    booking = Booking.query.get_or_404(id)
    
    # Only allow owner or admin to delete
    if booking.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    # Either soft delete (cancel) or hard delete
    booking.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'success': True}), 200


@booking_bp.route('/<int:id>/status', methods=['PUT'])
@token_required
def update_booking_status(current_user, id):
    """Update booking status (for admin/staff/security)"""
    if current_user.role not in ['admin', 'staff', 'security']:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    booking = Booking.query.get_or_404(id)
    data = request.get_json()
    
    new_status = data.get('status')
    if new_status in ['pending', 'approved', 'rejected', 'cancelled']:
        booking.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'booking': booking.to_dict()}), 200
    
    return jsonify({'success': False, 'message': 'Invalid status'}), 400
