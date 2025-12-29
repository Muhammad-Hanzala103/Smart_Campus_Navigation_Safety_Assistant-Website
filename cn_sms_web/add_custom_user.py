from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = 'user@example.com'
    password = 'yourpassword'
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    
    if user:
        print(f"User {email} already exists. Updating password...")
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        print("Password updated successfully.")
    else:
        print(f"Creating user {email}...")
        new_user = User(
            full_name='Test User',
            email=email,
            password_hash=generate_password_hash(password),
            role='user',
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()
        print("User created successfully.")
