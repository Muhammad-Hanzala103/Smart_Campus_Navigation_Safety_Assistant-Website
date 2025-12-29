from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("--- User List ---")
    for u in users:
        print(f"ID: {u.id} | Email: {u.email} | Role: {u.role}")
    if not users:
        print("No users found! Please run 'python db_init.py' to seed the database.")
