import json

def test_index(client):
    """Test landing page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"CIIAS" in response.data

def test_register_login(client):
    """Test user registration and login flow"""
    # 1. Register
    reg_data = {
        "email": "student@test.com",
        "password": "pass",
        "name": "Test Student",
        "role": "student",
        "university_id": 1
    }
    rv = client.post('/api/auth/register', json=reg_data)
    assert rv.status_code == 201

    # 2. Login
    login_data = {"email": "student@test.com", "password": "pass"}
    rv = client.post('/api/auth/login', json=login_data)
    assert rv.status_code == 200
    json_data = json.loads(rv.data)
    assert "token" in json_data

def test_access_protected_route_without_token(client):
    """Test accessing dashboard requires login"""
    rv = client.get('/dashboard', follow_redirects=True)
    # Should redirect to login
    assert rv.status_code == 200 
    assert b"Login" in rv.data or b"login" in rv.data
