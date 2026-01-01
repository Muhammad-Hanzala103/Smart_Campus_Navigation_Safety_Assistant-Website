from app import create_app, db
from app.models import User

app = create_app('development')

with app.app_context():
    # Reset password for admin
    user = User.query.filter_by(email='admin@university.edu').first()
    if user:
        user.set_password('admin123')
        db.session.commit()
        print(f"Password reset for: {user.email}")
    else:
        # Create admin if doesn't exist
        admin = User(name='Admin User', email='admin@university.edu', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin created: admin@university.edu / admin123")
