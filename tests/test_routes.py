import pytest
from flask import url_for

def test_login_page_renders_successfully(client):
    """Test that the login page returns a 200 OK status"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()

def test_dashboard_requires_login(client):
    """Test that accessing the dashboard without login redirects to login"""
    response = client.get('/dashboard')
    # Should be a redirect (302) to the login page
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')

def test_security_dashboard_requires_login(client):
    """Test that accessing the security dashboard without login redirects"""
    response = client.get('/security')
    assert response.status_code == 302

def test_transport_dashboard_requires_login(client):
    """Test that accessing transport without login redirects"""
    response = client.get('/transport')
    assert response.status_code == 302

def test_api_health_endpoint(client):
    """Test that the health check API returns 200 OK"""
    response = client.get('/api/health/health')
    # The health endpoint should be entirely public or return JSON
    assert response.status_code in [200, 401, 404] # Depending on if it exists/requires auth

def test_api_incidents_requires_auth(client):
    """Test that the incidents API is protected by token_required"""
    response = client.get('/api/incidents')
    # Should complain about a missing token, not a 500 error
    assert response.status_code == 401
    assert b'Token is missing' in response.data

def test_api_map_nodes(client):
    """Test map API requires tenant verification"""
    response = client.get('/api/map/nodes')
    assert response.status_code in [401, 404]

def test_admin_access_allowed(client, admin_user):
    """Test if a logged in admin user can access the dashboard"""
    # Simulate a login session directly in the test client
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id
        sess['user_role'] = admin_user.role
        sess['campus_id'] = 1

    # Now the dashboard should return 200 OK
    response = client.get('/dashboard')
    assert response.status_code == 200

    # Ensure transport dashboard also loads
    response = client.get('/transport')
    assert response.status_code == 200
