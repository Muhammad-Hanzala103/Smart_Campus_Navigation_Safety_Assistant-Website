"""
Pytest Configuration
Provides fixtures for testing the CNSMS application.
"""
import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import User
from config import TestConfig
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user and return user data."""
    with app.app_context():
        user = User(
            full_name='Test User',
            email='test@example.com',
            password_hash=generate_password_hash('testpass123'),
            role='user',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }


@pytest.fixture
def admin_user(app):
    """Create an admin user and return user data."""
    with app.app_context():
        user = User(
            full_name='Admin User',
            email='admin@example.com',
            password_hash=generate_password_hash('adminpass123'),
            role='admin',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        return {
            'id': user.id,
            'email': 'admin@example.com',
            'password': 'adminpass123',
            'name': 'Admin User'
        }


@pytest.fixture
def auth_token(client, test_user):
    """Get JWT token for test user."""
    response = client.post('/api/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    return response.get_json()['token']


@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers with JWT token."""
    return {'Authorization': f'Bearer {auth_token}'}


@pytest.fixture
def sample_image():
    """Create a minimal valid image for testing."""
    # 1x1 red PNG image (smallest valid PNG)
    import base64
    png_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
    )
    return png_data
