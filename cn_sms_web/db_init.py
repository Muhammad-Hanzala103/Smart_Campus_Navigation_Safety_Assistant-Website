from werkzeug.security import generate_password_hash
from app import create_app
from models import db, User, MapNode, Room, Booking, Incident
from datetime import datetime, timedelta

app = create_app()

def seed_data():
    with app.app_context():
        db.create_all()
        
        if User.query.first():
            print("Database already seeded.")
            return

        # Users
        u1 = User(email='admin@demo.edu', password_hash=generate_password_hash('Password123'), role='admin')
        u2 = User(email='security@demo.edu', password_hash=generate_password_hash('Password123'), role='security')
        u3 = User(email='staff@demo.edu', password_hash=generate_password_hash('Password123'), role='staff')
        db.session.add_all([u1, u2, u3])
        db.session.commit()

        # Map Nodes
        nodes = [
            MapNode(name='Gate', x=100, y=500, description='Main Entrance'),
            MapNode(name='Admin', x=200, y=400, description='Administration Block'),
            MapNode(name='Library', x=300, y=300, description='Central Library'),
            MapNode(name='Lab1', x=400, y=200, description='Computer Lab 1'),
            MapNode(name='Lab2', x=450, y=250, description='Physics Lab'),
            MapNode(name='Canteen', x=500, y=500, description='Stu. Center'),
            MapNode(name='Sports', x=600, y=100, description='Sports Complex')
        ]
        db.session.add_all(nodes)
        db.session.commit()

        # Rooms
        rooms = [
            Room(name='Conference Room A', node_id=2, capacity=20),
            Room(name='Lecture Hall 1', node_id=3, capacity=100),
            Room(name='Lab 101', node_id=4, capacity=30),
            Room(name='Gym Hall', node_id=7, capacity=50)
        ]
        db.session.add_all(rooms)
        db.session.commit()

        # Bookings
        b1 = Booking(user_id=3, room_id=1, start_time=datetime.now() + timedelta(days=1), end_time=datetime.now() + timedelta(days=1, hours=2), status='approved', reason='Staff Meeting')
        b2 = Booking(user_id=3, room_id=2, start_time=datetime.now() + timedelta(days=2), end_time=datetime.now() + timedelta(days=2, hours=1), status='pending', reason='Class lecture')
        db.session.add_all([b1, b2])

        # Incidents
        i1 = Incident(user_id=2, description='Broken window near Lab 1', category='Maintenance', x=405, y=205, status='open')
        db.session.add(i1)
        
        db.session.commit()
        print("Database seeded successfully.")
        
        # Dump to demo_data.sql for requirement compliance
        with open('demo_data.sql', 'w') as f:
            for line in db.session.connection().connection.iterdump():
                f.write(f'{line}\n')

if __name__ == '__main__':
    seed_data()
