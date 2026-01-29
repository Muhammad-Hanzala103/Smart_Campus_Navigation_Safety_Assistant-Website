from flask import Blueprint, request, jsonify
from app import db
from app.models import Shuttle, University
from app.utils import tenant_required
from datetime import datetime

transport_bp = Blueprint('transport', __name__)

@transport_bp.route('/live', methods=['GET'])
@tenant_required
def get_live_shuttles(uni):
    """Get live location of all active shuttles for a specific university"""
    campus_id = request.args.get('campus_id')
    query = Shuttle.query.filter_by(university_id=uni.id, status='Active')
    if campus_id:
        query = query.filter_by(campus_id=campus_id)
        
    shuttles = query.all()
    return jsonify([s.to_dict() for s in shuttles]), 200

@transport_bp.route('/shuttles', methods=['GET'])
@tenant_required
def get_all_shuttles(uni):
    """Get all shuttles for a specific university with optional campus filtering"""
    campus_id = request.args.get('campus_id')
    query = Shuttle.query.filter_by(university_id=uni.id)
    if campus_id:
        query = query.filter_by(campus_id=campus_id)
        
    shuttles = query.all()
    # Industrial Sort: Active first
    shuttles.sort(key=lambda s: (s.status == 'Active'), reverse=True)
    
    return jsonify([{
        **s.to_dict(),
        'campus_name': s.campus.name if s.campus else 'N/A',
        'driver_phone': s.driver.phone if s.driver else 'N/A'
    } for s in shuttles]), 200

@transport_bp.route('/driver/<int:driver_id>', methods=['GET'])
def get_driver_details(driver_id):
    """Get detailed record of a driver (Nexus 2.0 HR Record)"""
    from app.models import User
    driver = User.query.get(driver_id)
    if not driver:
        return jsonify({'error': 'Driver not found'}), 404
        
    return jsonify({
        'name': driver.name,
        'phone': driver.phone,
        'email': driver.email,
        'address': driver.staff_record.address if driver.staff_record else 'N/A',
        'licence': driver.staff_record.licence_number if driver.staff_record else 'N/A'
    }), 200

@transport_bp.route('/shuttle/update_location', methods=['POST'])
def update_location():
    # To be called by the GPS Tracker (Driver App or Simulator)
    data = request.json
    plate = data.get('plate_number')
    lat = data.get('lat')
    lng = data.get('lng')
    heading = data.get('heading', 0.0)
    
    shuttle = Shuttle.query.filter_by(plate_number=plate).first()
    if not shuttle:
        return jsonify({'error': 'Shuttle not found'}), 404
        
    shuttle.current_lat = lat
    shuttle.current_lng = lng
    shuttle.heading = heading
    shuttle.last_updated = datetime.utcnow()
    shuttle.status = 'Active'
    
    db.session.commit()
    return jsonify({'message': 'Location updated'}), 200
