from flask import Blueprint, jsonify
from app.models import Incident, Booking
from sqlalchemy import func
from app import db
from app.services.cache import cache, make_cache_key

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/incidents', methods=['GET'])
@cache.cached(timeout=60, key_prefix=make_cache_key)
def incident_analytics():
    status_counts = db.session.query(Incident.status, func.count(Incident.id)).group_by(Incident.status).all()
    severity_counts = db.session.query(Incident.ai_severity, func.count(Incident.id)).group_by(Incident.ai_severity).all()
    return jsonify({'status_breakdown': dict(status_counts), 'severity_breakdown': dict(severity_counts), 'total': Incident.query.count()})

@analytics_bp.route('/bookings', methods=['GET'])
@cache.cached(timeout=60, key_prefix=make_cache_key)
def booking_analytics():
    status_counts = db.session.query(Booking.status, func.count(Booking.id)).group_by(Booking.status).all()
    return jsonify({'status_breakdown': dict(status_counts), 'total': Booking.query.count()})
