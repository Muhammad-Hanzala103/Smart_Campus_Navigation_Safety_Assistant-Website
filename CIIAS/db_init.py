import os
from datetime import datetime, timedelta, time
import random

from app import create_app, db
from app.models import (
    User, Incident, IncidentComment, SOSAlert, Notification, 
    Room, Booking, MapNode, MapEdge, EmergencyContact, SafeZone, AuditLog
)

app = create_app('development')


def seed_db():
    """Initialize database with sample data"""
    with app.app_context():
        print("=" * 60)
        print("SSNS Database Initialization")
        print("=" * 60)
        
        db.create_all()
        print("✓ Database tables created")

        # Seed Users
        users = seed_users()
        print(f"✓ Created {len(users)} users")

        # Seed Emergency Contacts
        contacts = seed_emergency_contacts()
        print(f"✓ Created {len(contacts)} emergency contacts")

        # Seed Map Nodes
        nodes = seed_map_nodes()
        print(f"✓ Created {len(nodes)} map nodes")

        # Seed Map Edges
        edges = seed_map_edges(nodes)
        print(f"✓ Created {len(edges)} map edges")

        # Seed Safe Zones
        zones = seed_safe_zones()
        print(f"✓ Created {len(zones)} safe zones")

        # Seed Rooms
        rooms = seed_rooms()
        print(f"✓ Created {len(rooms)} rooms")

        # Seed Incidents
        incidents = seed_incidents(users)
        print(f"✓ Created {len(incidents)} incidents")

        # Seed Notifications
        notifications = seed_notifications(users)
        print(f"✓ Created {len(notifications)} notifications")

        print("\n" + "=" * 60)
        print("✅ SSNS Database Ready!")
        print("=" * 60)
        print("\n📋 Login Credentials:")
        print("-" * 40)
        print("Role       | Email                      | Password")
        print("-" * 40)
        print("Admin      | admin@university.edu       | admin123")
        print("Security   | security@university.edu    | security123")
        print("Staff      | staff@university.edu       | staff123")
        print("Student    | student@university.edu     | student123")
        print("=" * 60)


def seed_users():
    """Create sample users"""
    users_data = [
        {'name': 'Admin User', 'email': 'admin@university.edu', 'role': 'admin', 'password': 'admin123', 'phone': '+92 300 1234567'},
        {'name': 'Security Officer', 'email': 'security@university.edu', 'role': 'security', 'password': 'security123', 'phone': '+92 300 2345678'},
        {'name': 'Staff Member', 'email': 'staff@university.edu', 'role': 'staff', 'password': 'staff123', 'phone': '+92 300 3456789'},
        {'name': 'Student User', 'email': 'student@university.edu', 'role': 'student', 'password': 'student123', 'phone': '+92 300 4567890'},
    ]
    
    users = []
    for data in users_data:
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            user = User(
                name=data['name'],
                email=data['email'],
                role=data['role'],
                phone=data['phone'],
                is_active=True
            )
            user.set_password(data['password'])
            db.session.add(user)
        users.append(user)
    
    db.session.commit()
    return users


def seed_emergency_contacts():
    """Create emergency contacts"""
    contacts_data = [
        {'name': 'Campus Security', 'phone': '+92 51 1234567', 'type': 'security'},
        {'name': 'Emergency Hotline', 'phone': '1122', 'type': 'security'},
        {'name': 'Campus Medical Center', 'phone': '+92 51 2345678', 'type': 'medical'},
        {'name': 'Rescue 1122', 'phone': '1122', 'type': 'medical'},
        {'name': 'Fire Department', 'phone': '16', 'type': 'fire'},
        {'name': 'Campus Fire Safety', 'phone': '+92 51 3456789', 'type': 'fire'},
        {'name': 'Police Emergency', 'phone': '15', 'type': 'police'},
        {'name': 'Local Police Station', 'phone': '+92 51 4567890', 'type': 'police'},
    ]
    
    contacts = []
    for data in contacts_data:
        existing = EmergencyContact.query.filter_by(name=data['name']).first()
        if not existing:
            contact = EmergencyContact(**data)
            db.session.add(contact)
            contacts.append(contact)
    
    db.session.commit()
    return contacts


def seed_map_nodes():
    """Create map nodes for KICSIT campus"""
    # KICSIT approximate coordinates: 33.5651, 73.1584
    base_lat, base_lng = 33.5651, 73.1584
    
    nodes_data = [
        # Buildings
        {'name': 'Main Building', 'node_type': 'building', 'latitude': base_lat, 'longitude': base_lng, 
         'building': 'Main', 'floor': 'Ground', 'description': 'Main academic building', 'x': 400, 'y': 300},
        {'name': 'Library', 'node_type': 'building', 'latitude': base_lat + 0.001, 'longitude': base_lng + 0.001,
         'building': 'Library', 'floor': 'Ground', 'description': 'Central library', 'x': 500, 'y': 200},
        {'name': 'Cafeteria', 'node_type': 'building', 'latitude': base_lat - 0.001, 'longitude': base_lng + 0.0005,
         'building': 'Cafeteria', 'floor': 'Ground', 'description': 'Student cafeteria', 'x': 300, 'y': 400},
        {'name': 'Admin Block', 'node_type': 'building', 'latitude': base_lat + 0.0005, 'longitude': base_lng - 0.001,
         'building': 'Admin', 'floor': 'Ground', 'description': 'Administration offices', 'x': 250, 'y': 250},
        {'name': 'IT Lab', 'node_type': 'building', 'latitude': base_lat - 0.0005, 'longitude': base_lng - 0.0008,
         'building': 'IT', 'floor': '1st', 'description': 'Computer and IT laboratories', 'x': 350, 'y': 350},
        
        # Parking
        {'name': 'Main Parking', 'node_type': 'parking', 'latitude': base_lat - 0.002, 'longitude': base_lng,
         'description': 'Main parking area', 'x': 400, 'y': 500},
        {'name': 'Staff Parking', 'node_type': 'parking', 'latitude': base_lat + 0.002, 'longitude': base_lng - 0.001,
         'description': 'Staff and faculty parking', 'x': 200, 'y': 150},
        
        # Exits
        {'name': 'Main Gate', 'node_type': 'exit', 'latitude': base_lat - 0.003, 'longitude': base_lng,
         'description': 'Main entrance/exit gate', 'is_emergency_exit': True, 'x': 400, 'y': 600},
        {'name': 'Emergency Exit A', 'node_type': 'exit', 'latitude': base_lat, 'longitude': base_lng + 0.002,
         'description': 'Emergency exit near library', 'is_emergency_exit': True, 'x': 600, 'y': 300},
        {'name': 'Emergency Exit B', 'node_type': 'exit', 'latitude': base_lat, 'longitude': base_lng - 0.002,
         'description': 'Emergency exit near admin', 'is_emergency_exit': True, 'x': 100, 'y': 300},
        
        # Emergency
        {'name': 'Security Post', 'node_type': 'emergency', 'latitude': base_lat - 0.0025, 'longitude': base_lng,
         'description': '24/7 Security checkpoint', 'x': 400, 'y': 550},
        {'name': 'First Aid Station', 'node_type': 'emergency', 'latitude': base_lat + 0.0003, 'longitude': base_lng,
         'building': 'Main', 'description': 'Medical first aid station', 'x': 420, 'y': 280},
    ]
    
    nodes = []
    for data in nodes_data:
        existing = MapNode.query.filter_by(name=data['name']).first()
        if not existing:
            node = MapNode(**data)
            db.session.add(node)
            nodes.append(node)
    
    db.session.commit()
    return MapNode.query.all()


def seed_map_edges(nodes):
    """Create connections between map nodes"""
    if not nodes:
        return []
    
    # Create edges between nearby nodes
    node_dict = {n.name: n for n in nodes}
    
    edges_data = [
        ('Main Gate', 'Main Parking', 50),
        ('Main Parking', 'Main Building', 80),
        ('Main Building', 'Library', 60),
        ('Main Building', 'Cafeteria', 50),
        ('Main Building', 'Admin Block', 70),
        ('Main Building', 'IT Lab', 40),
        ('Admin Block', 'Staff Parking', 100),
        ('Library', 'Emergency Exit A', 30),
        ('Admin Block', 'Emergency Exit B', 25),
        ('Main Parking', 'Security Post', 30),
        ('Main Building', 'First Aid Station', 10),
        ('Security Post', 'Main Gate', 20),
    ]
    
    edges = []
    for from_name, to_name, weight in edges_data:
        if from_name in node_dict and to_name in node_dict:
            existing = MapEdge.query.filter_by(
                from_node_id=node_dict[from_name].id,
                to_node_id=node_dict[to_name].id
            ).first()
            if not existing:
                edge = MapEdge(
                    from_node_id=node_dict[from_name].id,
                    to_node_id=node_dict[to_name].id,
                    weight=weight
                )
                db.session.add(edge)
                edges.append(edge)
    
    db.session.commit()
    return edges


def seed_safe_zones():
    """Create safe zones for evacuation"""
    base_lat, base_lng = 33.5651, 73.1584
    
    zones_data = [
        {'name': 'Assembly Point A', 'latitude': base_lat - 0.003, 'longitude': base_lng + 0.001,
         'capacity': 500, 'description': 'Main assembly point near parking'},
        {'name': 'Assembly Point B', 'latitude': base_lat + 0.002, 'longitude': base_lng - 0.002,
         'capacity': 300, 'description': 'Secondary assembly point near staff parking'},
        {'name': 'Open Ground', 'latitude': base_lat - 0.004, 'longitude': base_lng,
         'capacity': 1000, 'description': 'Large open ground for mass evacuation'},
    ]
    
    zones = []
    for data in zones_data:
        existing = SafeZone.query.filter_by(name=data['name']).first()
        if not existing:
            zone = SafeZone(**data)
            db.session.add(zone)
            zones.append(zone)
    
    db.session.commit()
    return zones


def seed_rooms():
    """Create bookable rooms"""
    rooms_data = [
        {'name': 'Conference Room A', 'building': 'Main Building', 'floor': 'Ground',
         'capacity': 20, 'has_projector': True, 'has_whiteboard': True, 'has_ac': True},
        {'name': 'Conference Room B', 'building': 'Main Building', 'floor': '1st',
         'capacity': 15, 'has_projector': True, 'has_whiteboard': True, 'has_ac': True},
        {'name': 'Seminar Hall', 'building': 'Main Building', 'floor': 'Ground',
         'capacity': 100, 'has_projector': True, 'has_whiteboard': False, 'has_ac': True},
        {'name': 'Study Room 1', 'building': 'Library', 'floor': '1st',
         'capacity': 8, 'has_projector': False, 'has_whiteboard': True, 'has_ac': True},
        {'name': 'Study Room 2', 'building': 'Library', 'floor': '1st',
         'capacity': 6, 'has_projector': False, 'has_whiteboard': True, 'has_ac': False},
        {'name': 'Computer Lab 1', 'building': 'IT Lab', 'floor': '1st',
         'capacity': 40, 'has_projector': True, 'has_whiteboard': True, 'has_ac': True},
        {'name': 'Training Room', 'building': 'Admin Block', 'floor': '2nd',
         'capacity': 25, 'has_projector': True, 'has_whiteboard': True, 'has_ac': True},
    ]
    
    rooms = []
    for data in rooms_data:
        existing = Room.query.filter_by(name=data['name']).first()
        if not existing:
            room = Room(**data, is_available=True)
            db.session.add(room)
            rooms.append(room)
    
    db.session.commit()
    return rooms


def seed_incidents(users):
    """Create sample incidents"""
    if Incident.query.count() >= 5:
        return []
    
    incidents_data = [
        {'category': 'security', 'description': 'Unauthorized person spotted near IT Lab', 
         'severity': 'high', 'status': 'open'},
        {'category': 'fire', 'description': 'Smoke detector triggered in cafeteria kitchen',
         'severity': 'high', 'status': 'in_progress'},
        {'category': 'infrastructure', 'description': 'Water leakage in library basement',
         'severity': 'medium', 'status': 'open'},
        {'category': 'medical', 'description': 'Student fainted during lecture',
         'severity': 'medium', 'status': 'resolved'},
        {'category': 'security', 'description': 'Suspicious package found near main gate',
         'severity': 'high', 'status': 'resolved'},
        {'category': 'accident', 'description': 'Minor vehicle collision in parking',
         'severity': 'low', 'status': 'resolved'},
        {'category': 'infrastructure', 'description': 'AC not working in Conference Room A',
         'severity': 'low', 'status': 'in_progress'},
    ]
    
    base_lat, base_lng = 33.5651, 73.1584
    incidents = []
    
    for i, data in enumerate(incidents_data):
        incident = Incident(
            user_id=users[i % len(users)].id,
            category=data['category'],
            description=data['description'],
            severity=data['severity'],
            status=data['status'],
            latitude=base_lat + random.uniform(-0.002, 0.002),
            longitude=base_lng + random.uniform(-0.002, 0.002),
            x=random.randint(100, 600),
            y=random.randint(100, 500),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
        )
        if data['status'] == 'resolved':
            incident.resolved_at = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
        
        db.session.add(incident)
        incidents.append(incident)
    
    db.session.commit()
    return incidents


def seed_notifications(users):
    """Create sample notifications"""
    notifications_data = [
        {'title': 'Welcome to SSNS', 'message': 'Your account has been created successfully.', 'type': 'system'},
        {'title': 'Security Update', 'message': 'New security protocols have been implemented.', 'type': 'system'},
        {'title': 'Incident Reported', 'message': 'An incident near your area has been reported.', 'type': 'incident'},
    ]
    
    notifications = []
    for user in users[:2]:  # Only for first 2 users
        for data in notifications_data:
            notification = Notification(
                user_id=user.id,
                title=data['title'],
                message=data['message'],
                type=data['type'],
                is_read=False,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            )
            db.session.add(notification)
            notifications.append(notification)
    
    db.session.commit()
    return notifications


if __name__ == '__main__':
    seed_db()
