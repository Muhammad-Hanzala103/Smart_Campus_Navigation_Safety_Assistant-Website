"""
Database Seed Script
Populates database with demo data for testing.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models import User, Incident, MapNode, Room, Booking, AuditLog
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json


def seed_database():
    """Seed database with demo data."""
    app = create_app()
    
    with app.app_context():
        print("🗑️  Dropping existing tables...")
        db.drop_all()
        
        print("📦 Creating tables...")
        db.create_all()
        
        # ============ USERS ============
        print("👤 Creating users...")
        
        admin = User(
            full_name='Admin User',
            email='admin@university.edu',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            department='Security Operations',
            is_active=True
        )
        
        officer = User(
            full_name='Security Officer',
            email='officer@university.edu',
            password_hash=generate_password_hash('officer123'),
            role='officer',
            department='Campus Security',
            is_active=True
        )
        
        analyst = User(
            full_name='Security Analyst',
            email='analyst@university.edu',
            password_hash=generate_password_hash('analyst123'),
            role='analyst',
            department='Intelligence Unit',
            is_active=True
        )
        
        user = User(
            full_name='Regular User',
            email='user@university.edu',
            password_hash=generate_password_hash('user123'),
            role='user',
            department='Student Services',
            is_active=True
        )
        
        db.session.add_all([admin, officer, analyst, user])
        db.session.commit()
        print(f"   ✅ Created {User.query.count()} users")
        
        # ============ MAP NODES ============
        print("🗺️  Creating map nodes...")
        
        nodes = [
            MapNode(name='Main Gate', x=10, y=50, node_type='entrance'),
            MapNode(name='Library', x=30, y=40, node_type='building'),
            MapNode(name='Science Block', x=50, y=30, node_type='building'),
            MapNode(name='Admin Building', x=40, y=60, node_type='building'),
            MapNode(name='Cafeteria', x=60, y=50, node_type='facility'),
            MapNode(name='Sports Complex', x=80, y=40, node_type='facility'),
            MapNode(name='Parking Lot A', x=20, y=80, node_type='parking'),
            MapNode(name='Parking Lot B', x=70, y=70, node_type='parking'),
        ]
        
        db.session.add_all(nodes)
        db.session.commit()
        print(f"   ✅ Created {MapNode.query.count()} map nodes")
        
        # ============ ROOMS ============
        print("🏢 Creating rooms...")
        
        rooms = [
            Room(name='Conference Room A', capacity=20),
            Room(name='Conference Room B', capacity=15),
            Room(name='Lecture Hall 1', capacity=100),
            Room(name='Lab 101', capacity=30),
            Room(name='Meeting Room', capacity=8),
        ]
        
        db.session.add_all(rooms)
        db.session.commit()
        print(f"   ✅ Created {Room.query.count()} rooms")

        # ============ INCIDENTS ============
        print("🚨 Creating sample incidents...")
        
        incidents = [
            Incident(
                user_id=user.id,
                description='Suspicious person loitering near library entrance',
                category='Suspicious',
                location_name='Library - Main Entrance',
                x=30.5, y=40.2,
                status='new',
                ai_labels=json.dumps([{'name': 'person', 'confidence': 0.95}]),
                ai_risk_score=45,
                ai_severity='MEDIUM',
                ai_recommendation='Monitor via CCTV and log for analysis.',
                ai_analyzed_at=datetime.utcnow() - timedelta(hours=2)
            ),
            Incident(
                user_id=officer.id,
                description='Smoke detected near electrical room',
                category='Fire',
                location_name='Science Block - Basement',
                x=50.3, y=30.8,
                status='escalated',
                ai_labels=json.dumps([{'name': 'smoke', 'confidence': 0.88}]),
                ai_risk_score=92,
                ai_severity='CRITICAL',
                ai_recommendation='URGENT: Immediately dispatch fire safety team.',
                ai_analyzed_at=datetime.utcnow() - timedelta(hours=1)
            ),
            Incident(
                user_id=user.id,
                description='Large crowd gathering in parking lot',
                category='Crowd',
                location_name='Parking Lot A',
                x=20.1, y=80.5,
                status='under_review',
                ai_labels=json.dumps([
                    {'name': 'crowd', 'confidence': 0.91},
                    {'name': 'car', 'confidence': 0.85}
                ]),
                ai_risk_score=55,
                ai_severity='MEDIUM',
                ai_recommendation='Increased monitoring recommended.',
                ai_analyzed_at=datetime.utcnow() - timedelta(minutes=30)
            ),
            Incident(
                user_id=analyst.id,
                description='Unattended backpack found near cafeteria',
                category='Suspicious',
                location_name='Cafeteria - Outdoor Seating',
                x=60.7, y=50.2,
                status='resolved',
                ai_labels=json.dumps([
                    {'name': 'backpack', 'confidence': 0.97},
                    {'name': 'person', 'confidence': 0.72}
                ]),
                ai_risk_score=68,
                ai_severity='HIGH',
                ai_recommendation='Investigate immediately. Check for owner.',
                ai_analyzed_at=datetime.utcnow() - timedelta(days=1),
                resolution_notes='Owner identified. False alarm.'
            ),
            Incident(
                user_id=user.id,
                description='Normal activity at main gate during peak hours',
                category='Routine',
                location_name='Main Gate',
                x=10.2, y=50.1,
                status='closed',
                ai_labels=json.dumps([
                    {'name': 'person', 'confidence': 0.89},
                    {'name': 'bicycle', 'confidence': 0.76}
                ]),
                ai_risk_score=15,
                ai_severity='LOW',
                ai_recommendation='No action required. Normal activity.',
                ai_analyzed_at=datetime.utcnow() - timedelta(days=2)
            ),
        ]
        
        db.session.add_all(incidents)
        db.session.commit()
        print(f"   ✅ Created {Incident.query.count()} incidents")
        
        # ============ BOOKINGS ============
        print("📅 Creating bookings...")
        
        bookings = [
            Booking(
                user_id=admin.id,
                room_id=1,
                start_time=datetime.utcnow() + timedelta(hours=2),
                end_time=datetime.utcnow() + timedelta(hours=4)
            ),
            Booking(
                user_id=officer.id,
                room_id=2,
                start_time=datetime.utcnow() + timedelta(days=1),
                end_time=datetime.utcnow() + timedelta(days=1, hours=2)
            ),
        ]
        
        db.session.add_all(bookings)
        db.session.commit()
        print(f"   ✅ Created {Booking.query.count()} bookings")
        
        # ============ SUMMARY ============
        print("\n" + "="*50)
        print("✅ Database seeded successfully!")
        print("="*50)
        print("\n📋 Demo Credentials:")
        print("   Admin:   admin@university.edu / admin123")
        print("   Officer: officer@university.edu / officer123")
        print("   Analyst: analyst@university.edu / analyst123")
        print("   User:    user@university.edu / user123")
        print("\n🚀 Run 'python app.py' to start the server")


if __name__ == '__main__':
    seed_database()
