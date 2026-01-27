import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    # Create tables
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    """Create a mock admin user"""
    with app.app_context():
        user = User(
            name="Test Admin",
            email="admin@test.com",
            role="admin",
            university_id=1
        )
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
    return user
