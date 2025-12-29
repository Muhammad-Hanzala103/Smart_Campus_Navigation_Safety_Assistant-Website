import pytest
import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        # Create admin user
        admin = User(email='admin', role='admin', password_hash=generate_password_hash('pass'))
        db.session.add(admin)
        db.session.commit()
        
        yield app.test_client()
        db.drop_all()

def test_login(client):
    rv = client.post('/api/login', json={'username': 'admin', 'password': 'pass'})
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'ok'

def test_get_map_public(client):
    rv = client.get('/api/map')
    assert rv.status_code == 200
    assert 'nodes' in rv.get_json()

def test_incident_create_auth(client):
    # Public shouldn't create
    rv = client.post('/api/incidents', data={})
    assert rv.status_code == 401
    
    # Login
    client.post('/api/login', json={'username': 'admin', 'password': 'pass'})
    
    # Create incident
    rv = client.post('/api/incidents', data={'category': 'Test', 'description': 'Desc'})
    assert rv.status_code == 201
