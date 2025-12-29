from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), nullable=False) # admin, security, staff
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MapNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))

class MapEdge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_node_id = db.Column(db.Integer, db.ForeignKey('map_node.id'), nullable=False)
    end_node_id = db.Column(db.Integer, db.ForeignKey('map_node.id'), nullable=False)
    weight = db.Column(db.Float, default=1.0)

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
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    status = db.Column(db.String(20), default='open') # open, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
