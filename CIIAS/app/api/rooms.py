from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app import db
from app.models import Room, Booking

rooms_bp = Blueprint('rooms', __name__)


@rooms_bp.route('', methods=['GET'])
def get_rooms():
    """Get all rooms with optional filters"""
    query = Room.query
    
    # Apply filters
    building = request.args.get('building')
    if building:
        query = query.filter(Room.building.ilike(f'%{building}%'))
    
    has_projector = request.args.get('has_projector')
    if has_projector and has_projector.lower() == 'true':
        query = query.filter_by(has_projector=True)
    
    has_whiteboard = request.args.get('has_whiteboard')
    if has_whiteboard and has_whiteboard.lower() == 'true':
        query = query.filter_by(has_whiteboard=True)
    
    has_ac = request.args.get('has_ac')
    if has_ac and has_ac.lower() == 'true':
        query = query.filter_by(has_ac=True)
    
    min_capacity = request.args.get('min_capacity', type=int)
    if min_capacity:
        query = query.filter(Room.capacity >= min_capacity)
    
    rooms = query.filter_by(is_available=True).all()
    
    return jsonify([r.to_dict() for r in rooms]), 200


@rooms_bp.route('/<int:id>/availability', methods=['GET'])
def get_room_availability(id):
    """Get room availability for a specific date"""
    room = Room.query.get_or_404(id)
    
    date_str = request.args.get('date')
    if not date_str:
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Get all bookings for this room on this date
    bookings = Booking.query.filter(
        Booking.room_id == id,
        Booking.date == date,
        Booking.status.in_(['pending', 'approved'])
    ).all()
    
    booked_slots = []
    for booking in bookings:
        booked_slots.append({
            'start': booking.start_time.strftime('%H:%M'),
            'end': booking.end_time.strftime('%H:%M'),
            'status': booking.status
        })
    
    # Generate available slots (assuming 8 AM to 8 PM operation)
    available_slots = _calculate_available_slots(booked_slots)
    
    return jsonify({
        'room': room.to_dict(),
        'date': date_str,
        'available_slots': available_slots,
        'booked_slots': booked_slots
    }), 200


def _calculate_available_slots(booked_slots):
    """Calculate available time slots based on booked slots"""
    # Define operating hours (8 AM to 8 PM, 1-hour slots)
    all_slots = []
    for hour in range(8, 20):
        slot = {
            'start': f'{hour:02d}:00',
            'end': f'{hour+1:02d}:00'
        }
        all_slots.append(slot)
    
    available = []
    for slot in all_slots:
        is_booked = False
        for booked in booked_slots:
            # Check overlap
            if slot['start'] < booked['end'] and slot['end'] > booked['start']:
                is_booked = True
                break
        
        if not is_booked:
            available.append(slot)
    
    return available
