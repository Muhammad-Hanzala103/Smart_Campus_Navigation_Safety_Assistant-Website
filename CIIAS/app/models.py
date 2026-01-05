from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, staff, security, admin
    phone = db.Column(db.String(20))
    profile_photo = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    fcm_token = db.Column(db.String(256))  # For push notifications

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_phone=True):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'profile_photo': self.profile_photo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_phone:
            data['phone'] = self.phone
        return data


class Incident(db.Model):
    __tablename__ = 'incidents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # security, fire, medical, accident, infrastructure
    severity = db.Column(db.String(20), default='medium')  # low, medium, high
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved
    image_url = db.Column(db.String(256))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    ai_category = db.Column(db.String(50))
    ai_confidence = db.Column(db.Float)
    ai_labels = db.Column(db.Text)
    ai_severity = db.Column(db.String(20))
    ai_recommendation = db.Column(db.Text)
    ai_analyzed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='incidents')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': {'name': self.user.name} if self.user else None,
            'description': self.description,
            'category': self.category,
            'severity': self.severity,
            'status': self.status,
            'image_url': self.image_url,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'x': self.x,
            'y': self.y,
            'ai_category': self.ai_category,
            'ai_confidence': self.ai_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class IncidentComment(db.Model):
    __tablename__ = 'incident_comments'
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('Incident', backref='comments')
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Unknown',
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SOSAlert(db.Model):
    __tablename__ = 'sos_alerts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(50))  # medical, fire, security, accident
    message = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')  # active, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='sos_alerts')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': {'name': self.user.name} if self.user else None,
            'alert_type': self.alert_type,
            'message': self.message,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    type = db.Column(db.String(50))  # incident, sos, booking, system
    is_read = db.Column(db.Boolean, default=False)
    data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100))
    floor = db.Column(db.String(20))
    capacity = db.Column(db.Integer)
    has_projector = db.Column(db.Boolean, default=False)
    has_whiteboard = db.Column(db.Boolean, default=False)
    has_ac = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(256))
    is_available = db.Column(db.Boolean, default=True)
    node_id = db.Column(db.Integer, db.ForeignKey('map_nodes.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'building': self.building,
            'floor': self.floor,
            'capacity': self.capacity,
            'has_projector': self.has_projector,
            'has_whiteboard': self.has_whiteboard,
            'has_ac': self.has_ac,
            'image_url': self.image_url,
            'is_available': self.is_available
        }


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    purpose = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='bookings')
    room = db.relationship('Room', backref='bookings')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'room': self.room.to_dict() if self.room else None,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'purpose': self.purpose,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MapNode(db.Model):
    __tablename__ = 'map_nodes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    node_type = db.Column(db.String(50))  # building, room, exit, parking, emergency
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    building = db.Column(db.String(100))
    floor = db.Column(db.String(20))
    description = db.Column(db.Text)
    is_accessible = db.Column(db.Boolean, default=True)
    is_emergency_exit = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'node_type': self.node_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'x': self.x,
            'y': self.y,
            'building': self.building,
            'floor': self.floor,
            'description': self.description,
            'is_accessible': self.is_accessible,
            'is_emergency_exit': self.is_emergency_exit
        }


class MapEdge(db.Model):
    __tablename__ = 'map_edges'
    id = db.Column(db.Integer, primary_key=True)
    from_node_id = db.Column(db.Integer, db.ForeignKey('map_nodes.id'), nullable=False)
    to_node_id = db.Column(db.Integer, db.ForeignKey('map_nodes.id'), nullable=False)
    weight = db.Column(db.Float, default=1.0)

    from_node = db.relationship('MapNode', foreign_keys=[from_node_id], backref='edges_from')
    to_node = db.relationship('MapNode', foreign_keys=[to_node_id], backref='edges_to')

    def to_dict(self):
        return {
            'id': self.id,
            'from_node_id': self.from_node_id,
            'to_node_id': self.to_node_id,
            'weight': self.weight
        }


class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(50))  # security, medical, fire, police
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'type': self.type,
            'is_active': self.is_active
        }


class SafeZone(db.Model):
    __tablename__ = 'safe_zones'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'capacity': self.capacity,
            'description': self.description
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(64))
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
