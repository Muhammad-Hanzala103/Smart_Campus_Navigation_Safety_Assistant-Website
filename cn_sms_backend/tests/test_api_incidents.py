import pytest
import io
from app import create_app, db
from app.models import User, Incident

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create user
            u = User(name='Test', email='test@test.com', role='student')
            u.set_password('pass')
            db.session.add(u)
            db.session.commit()
            yield client
            db.session.remove()
            db.drop_all()

def test_create_incident(client):
    # Login
    auth = client.post('/api/auth/login', json={'email': 'test@test.com', 'password': 'pass'})
    token = auth.get_json()['token']
    
    # Create Incident
    data = {
        'category': 'Safety',
        'description': 'Test Desc',
        'x': 100,
        'y': 100
    }
    
    # Mock image upload
    data['image'] = (io.BytesIO(b"abcdef"), 'test.jpg')
    
    resp = client.post('/api/incidents/', 
                       content_type='multipart/form-data',
                       data=data,
                       headers={'Authorization': f'Bearer {token}'})
    
    assert resp.status_code == 201
    assert resp.get_json()['status'] == 'open'
    
def test_analyze_incident(client):
    # Just test the route exists and returns mock result for now
    data = {'image': (io.BytesIO(b"1234567890"), 'test.jpg')}
    resp = client.post('/api/incidents/analyze', 
                       content_type='multipart/form-data',
                       data=data)
    
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert 'severity' in json_data
