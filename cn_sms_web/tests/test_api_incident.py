import pytest
from app import create_app, db # type: ignore
from models import User, Incident # type: ignore
from werkzeug.security import generate_password_hash # type: ignore
import io

@pytest.fixture
def client():
    app = create_app()
    app.config.update({ "TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:" })
    with app.app_context():
        db.create_all()
        u = User(email='user@test.com', password_hash=generate_password_hash('pass'), role='staff')
        db.session.add(u)
        db.session.commit()
        yield app.test_client()
        db.drop_all()

def test_incident_flow(client):
    # Login
    client.post('/api/login', json={'username': 'user@test.com', 'password': 'pass'})
    
    # Post Incident
    data = {
        'description': 'Test Leak',
        'category': 'Plumbing',
        'x': 100,
        'y': 100,
        'image': (io.BytesIO(b"fakeimage"), 'test.jpg')
    }
    rv = client.post('/api/incidents', data=data, content_type='multipart/form-data')
    assert rv.status_code == 201
    assert rv.get_json()['message'] == 'Incident reported'
    
    # Verify in list
    rv = client.get('/api/incidents')
    assert len(rv.get_json()) == 1
    assert rv.get_json()[0]['category'] == 'Plumbing'
