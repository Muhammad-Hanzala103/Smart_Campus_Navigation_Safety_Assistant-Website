from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # admin, security, staff

class MapNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    # Relationships can be added if needed, e.g. connected edges

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

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # approved, rejected, pending
    reason = db.Column(db.String(200))

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    image_path = db.Column(db.String(200))
    status = db.Column(db.String(20), default='open') # open, resolved, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI Analysis Fields
    ai_labels = db.Column(db.Text) # JSON string of labels
    ai_severity = db.Column(db.String(20)) # HIGH, MEDIUM, LOW
    ai_recommendation = db.Column(db.Text)
    ai_analyzed_at = db.Column(db.DateTime)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(500))
