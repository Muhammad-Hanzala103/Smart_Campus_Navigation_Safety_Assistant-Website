import os
from app import create_app, db
from app.models import User, MapNode, Room, Booking, Incident, AuditLog
from datetime import datetime, timedelta
import random

app = create_app('development')

def seed_db():
    with app.app_context():
        print("Creating CIIAS Database...")
        db.create_all()

        # Clear existing data for fresh seed
        if User.query.filter_by(email='admin@university.edu').first():
            print("Updating existing database...")
        
        # Create/Update Users
        users_data = [
            {'name': 'Admin User', 'email': 'admin@university.edu', 'role': 'admin', 'password': 'admin123'},
            {'name': 'Security Officer', 'email': 'officer@university.edu', 'role': 'security', 'password': 'officer123'},
            {'name': 'Staff Member', 'email': 'staff@university.edu', 'role': 'staff', 'password': 'staff123'},
            {'name': 'Student User', 'email': 'student@university.edu', 'role': 'student', 'password': 'student123'},
        ]
        
        users = []
        for u_data in users_data:
            user = User.query.filter_by(email=u_data['email']).first()
            if not user:
                user = User(name=u_data['name'], email=u_data['email'], role=u_data['role'], phone='+92 300 1234567')
            user.set_password(u_data['password'])
            db.session.add(user)
            users.append(user)
        db.session.commit()
        print(f"Users: {len(users)} created/updated")

        # Create Incidents
        if Incident.query.count() < 5:
            categories = ['Security', 'Safety', 'Fire', 'Medical', 'Suspicious', 'Crowd']
            severities = ['HIGH', 'MEDIUM', 'LOW']
            statuses = ['open', 'in_progress', 'resolved']
            
            incidents_data = [
                {'category': 'Security', 'desc': 'Unauthorized access attempt at main gate', 'severity': 'HIGH', 'status': 'open'},
                {'category': 'Safety', 'desc': 'Fire extinguisher expired in Block A corridor', 'severity': 'MEDIUM', 'status': 'in_progress'},
                {'category': 'Suspicious', 'desc': 'Unattended bag found near cafeteria entrance', 'severity': 'HIGH', 'status': 'open'},
                {'category': 'Crowd', 'desc': 'Large gathering near parking lot', 'severity': 'MEDIUM', 'status': 'resolved'},
                {'category': 'Medical', 'desc': 'Student reported feeling unwell in lecture hall', 'severity': 'LOW', 'status': 'resolved'},
                {'category': 'Security', 'desc': 'Broken window spotted on second floor', 'severity': 'MEDIUM', 'status': 'open'},
                {'category': 'Fire', 'desc': 'Smoke detected in server room', 'severity': 'HIGH', 'status': 'in_progress'},
            ]
            
            for inc_data in incidents_data:
                inc = Incident(
                    user_id=random.choice(users).id,
                    category=inc_data['category'],
                    description=inc_data['desc'],
                    x=73.158 + random.uniform(-0.002, 0.002),
                    y=33.565 + random.uniform(-0.002, 0.002),
                    status=inc_data['status'],
                    ai_severity=inc_data['severity'],
                    ai_recommendation=f"Recommended action for {inc_data['severity']} severity incident",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
                )
                db.session.add(inc)
            db.session.commit()
            print(f"Incidents: {len(incidents_data)} created")

        # Create Audit Logs
        if AuditLog.query.count() < 5:
            logs = [
                {'action': 'LOGIN', 'details': 'Admin user logged in'},
                {'action': 'INCIDENT_CREATE', 'details': 'New incident #1 created'},
                {'action': 'USER_UPDATE', 'details': 'User role changed to security'},
                {'action': 'INCIDENT_STATUS_CHANGE', 'details': 'Incident #2 status: open → in_progress'},
                {'action': 'LOGIN', 'details': 'Security officer logged in'},
            ]
            for log_data in logs:
                log = AuditLog(
                    user_id=users[0].id,
                    action=log_data['action'],
                    details=log_data['details'],
                    timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                )
                db.session.add(log)
            db.session.commit()
            print("Audit logs created")

        print("\n" + "="*50)
        print("CIIAS Database Ready!")
        print("="*50)
        print("\nLogin Credentials:")
        print("-" * 30)
        print("Admin:    admin@university.edu / admin123")
        print("Security: officer@university.edu / officer123")
        print("Staff:    staff@university.edu / staff123")
        print("Student:  student@university.edu / student123")
        print("="*50)

if __name__ == '__main__':
    seed_db()
