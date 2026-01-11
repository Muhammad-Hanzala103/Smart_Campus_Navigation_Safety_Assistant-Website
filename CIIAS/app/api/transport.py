from flask import Blueprint, request, jsonify
from app import db
from app.models import Shuttle
from datetime import datetime

transport_bp = Blueprint('transport', __name__)

@transport_bp.route('/live', methods=['GET'])
def get_live_shuttles():
    """Get live location of all active shuttles"""
    shuttles = Shuttle.query.filter_by(status='Active').all()
    return jsonify([s.to_dict() for s in shuttles]), 200

@transport_bp.route('/shuttles', methods=['GET'])
def get_all_shuttles():
    shuttles = Shuttle.query.all()
    # Sort: Active first
    shuttles.sort(key=lambda x: x.status == 'Active', reverse=True)
    return jsonify([s.to_dict() for s in shuttles]), 200

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
