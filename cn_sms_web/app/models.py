from datetime import datetime
from flask_login import UserMixin
from .extensions import db

# --- User & Role Management ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'officer', 'analyst'
    department = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def has_role(self, role_name):
        return self.role == role_name

# --- Map & Graph Data ---
class MapNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    # E.g., 'Entrance', 'Hallway', 'Room'
    node_type = db.Column(db.String(50), default='general')

class MapEdge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_node_id = db.Column(db.Integer, db.ForeignKey('map_node.id'), nullable=False)
    end_node_id = db.Column(db.Integer, db.ForeignKey('map_node.id'), nullable=False)
    weight = db.Column(db.Float)
    
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    node_id = db.Column(db.Integer, db.ForeignKey('map_node.id'))
    capacity = db.Column(db.Integer)
    resources = db.Column(db.String(200)) # e.g. "Projector, Whiteboard"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # approved, rejected, pending
    reason = db.Column(db.String(200))

# --- Incident Intelligence ---
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Reporter
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Officer
    
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50)) # Theft, Fire, Medical, Weapon, Suspicious, Other
    location_name = db.Column(db.String(100)) # "Near Library Entrance"
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    image_path = db.Column(db.String(200))
    
    status = db.Column(db.String(20), default='new') # new, under_review, escalated, resolved, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    resolution_notes = db.Column(db.Text)
    
    # AI Analysis Fields
    ai_labels = db.Column(db.Text) # JSON string: [{"name": "fire", "confidence": 0.98}, ...]
    ai_risk_score = db.Column(db.Integer, default=0) # 0 to 100
    ai_severity = db.Column(db.String(20), default='LOW') # CRITICAL, HIGH, MEDIUM, LOW
    ai_recommendation = db.Column(db.Text)
    ai_analyzed_at = db.Column(db.DateTime)

    reporter = db.relationship('User', foreign_keys=[user_id], backref='reported_incidents')
    assigned_officer = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_incidents')

# --- Audit & Logs ---
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
