from flask import Blueprint, jsonify
from app.models import Incident, Booking
from sqlalchemy import func
from app import db

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/incidents', methods=['GET'])
def incident_analytics():
    status_counts = db.session.query(Incident.status, func.count(Incident.id)).group_by(Incident.status).all()
    severity_counts = db.session.query(Incident.ai_severity, func.count(Incident.id)).group_by(Incident.ai_severity).all()
    return jsonify({'status_breakdown': dict(status_counts), 'severity_breakdown': dict(severity_counts), 'total': Incident.query.count()})

@analytics_bp.route('/bookings', methods=['GET'])
def booking_analytics():
    status_counts = db.session.query(Booking.status, func.count(Booking.id)).group_by(Booking.status).all()
    return jsonify({'status_breakdown': dict(status_counts), 'total': Booking.query.count()})
