import pytest
from app import create_app, db
from models import User, MapNode

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        user = User(email='admin@demo.edu', password_hash='hash', role='admin')
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_header(client):
    # Mock login or just bypass if testing logic, but here we test endpoints
    # For simplicity in this demo test, we assume login works or we mock current_user
    # But since we have a real login endpoint, let's use it or `login_user` in test_request_context
    pass 
    # To keep it simple and robust without complex auth mocking in 5 mins:
    # We will just rely on the fact that we can post to login first.

def test_get_map(client):
    rv = client.get('/api/map')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'nodes' in json_data
    assert 'map_image' in json_data

def test_create_node_auth(client):
    # Login first
    with client.application.test_request_context():
         # Manual auth setup is tricky without session, let's use the login endpoint
         pass
    
    # Actually, let's just use the client to login
    # We need a user with password. In fixture we put 'hash' directly. 
    # Let's clean up fixture to use real hash if we want real login.
    from werkzeug.security import generate_password_hash
    with client.application.app_context():
        u = User.query.filter_by(email='admin@demo.edu').first()
        u.password_hash = generate_password_hash('password')
        db.session.commit()

    client.post('/api/login', json={'username': 'admin@demo.edu', 'password': 'password'})
    
    rv = client.post('/api/map/nodes', json={'name': 'Test Node', 'x': 10, 'y': 10, 'description': 'desc'})
    assert rv.status_code == 201
    assert rv.get_json()['message'] == 'Node created'
