import os
from app import create_app, db
from app.models import User, MapNode, Room, Booking, Incident
from datetime import datetime, timedelta

app = create_app('development')

def seed_db():
    with app.app_context():
        print("Creating Database...")
        db.create_all()

        if User.query.first():
            print("DB already seeded.")
            return

        print("Seeding Users...")
        # Password for all: 'password'
        admin = User(name='Admin User', email='admin@cn.sms', role='admin', phone='123456')
        admin.set_password('password')
        
        security = User(name='Security Chief', email='security@cn.sms', role='security', phone='111222')
        security.set_password('password')

        staff = User(name='Staff Member', email='staff@cn.sms', role='staff', phone='333444')
        staff.set_password('password')

        db.session.add_all([admin, security, staff])
        db.session.commit()

        print("Seeding Map...")
        nodes = [
            MapNode(name='Gate', x=50, y=550, description='Main Campus Gate', node_type='gate'),
            MapNode(name='Admin Block', x=150, y=400, description='Administration', node_type='building'),
            MapNode(name='Library', x=300, y=300, description='Central Library', node_type='building'),
            MapNode(name='Lab 1', x=500, y=200, description='Computer Lab 1', node_type='room'),
            MapNode(name='Lab 2', x=550, y=200, description='Computer Lab 2', node_type='room'),
            MapNode(name='Canteen', x=700, y=500, description='Food Court', node_type='amenity'),
            MapNode(name='Sports Complex', x=800, y=100, description='Gym and Courts', node_type='amenity')
        ]
        db.session.add_all(nodes)
        db.session.commit()

        print("Seeding Rooms...")
        # Assign rooms to nodes (simplified)
        lab1_room = Room(name='Lab 1', node_id=nodes[3].id, capacity=30)
        lab2_room = Room(name='Lab 2', node_id=nodes[4].id, capacity=35)
        conf_room = Room(name='Conference Hall', node_id=nodes[1].id, capacity=100)
        
        db.session.add_all([lab1_room, lab2_room, conf_room])
        db.session.commit()

        print("Seeding Bookings...")
        b1 = Booking(user_id=staff.id, room_id=conf_room.id, 
                     start_time=datetime.utcnow() + timedelta(days=1, hours=2),
                     end_time=datetime.utcnow() + timedelta(days=1, hours=4),
                     status='approved')
        b2 = Booking(user_id=staff.id, room_id=lab1_room.id,
                     start_time=datetime.utcnow() + timedelta(days=2),
                     end_time=datetime.utcnow() + timedelta(days=2, hours=1),
                     status='pending')
        db.session.add_all([b1, b2])

        print("Seeding Incident...")
        inc = Incident(user_id=security.id, category='Safety', description='Suspicious bag found near gate',
                       x=60, y=540, status='open', ai_severity='HIGH', 
                       ai_recommendation='Investigate immediately', 
                       ai_analyzed_at=datetime.utcnow())
        db.session.add(inc)
        db.session.commit()

        print("Database Seeded Successfully!")

if __name__ == '__main__':
    seed_db()
