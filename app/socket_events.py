from app import socketio, db
from flask_socketio import emit
from app.models import AuditLog, Shuttle, Incident
from flask import request
import datetime

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    # Optional: Authentication check via token

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('update_location')
def handle_location_update(data):
    """
    Received from Android App (User or Driver).
    Broadcast to Security/Transport Rooms.
    data = {'user_id': 123, 'lat': 33.6, 'lng': 73.0, 'type': 'user|shuttle'}
    """
    if data.get('type') == 'shuttle':
        # Update Database
        shuttle = Shuttle.query.filter_by(id=data.get('id')).first()
        if shuttle:
            shuttle.current_lat = data['lat']
            shuttle.current_lng = data['lng']
            shuttle.heading = data.get('heading', 0)
            shuttle.last_updated = datetime.datetime.utcnow()
            db.session.commit()
        
        # Broadcast to Transport Dashboard
        emit('shuttle_update', data, broadcast=True)
    
    else:
        # Broadcast User Location to Security Dashboard
        emit('user_location', data, broadcast=True)

@socketio.on('new_incident')
def handle_new_incident(data):
    """
    Triggered when a new incident is reported via API (or directly socket).
    Broadcast to Security Dashboard.
    """
    emit('new_incident', data, broadcast=True)

@socketio.on('join_room')
def handle_join_room(data):
    # Logic to join specific rooms (e.g. 'security_room')
    pass
