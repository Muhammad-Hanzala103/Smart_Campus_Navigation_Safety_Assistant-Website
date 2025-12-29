"""
Test Authentication Flow
Tests registration, login, and protected endpoints.
"""
import pytest


class TestRegistration:
    """Test user registration endpoint."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/register', json={
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert 'user_id' in data
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails."""
        response = client.post('/api/register', json={
            'name': 'Another User',
            'email': test_user['email'],
            'password': 'anotherpass123'
        })
        
        assert response.status_code == 409
        assert 'already registered' in response.get_json()['error']
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post('/api/register', json={
            'name': 'Bad Email User',
            'email': 'notanemail',
            'password': 'securepass123'
        })
        
        assert response.status_code == 400
        assert 'Validation error' in response.get_json()['error']
    
    def test_register_short_password(self, client):
        """Test registration with password too short."""
        response = client.post('/api/register', json={
            'name': 'Short Pass User',
            'email': 'short@example.com',
            'password': '123'
        })
        
        assert response.status_code == 400
        assert 'at least 6 characters' in response.get_json()['message']


class TestLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client, test_user):
        """Test successful login returns token."""
        response = client.post('/api/login', json={
            'email': test_user['email'],
            'password': test_user['password']
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == test_user['email']
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post('/api/login', json={
            'email': test_user['email'],
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert 'Invalid credentials' in response.get_json()['error']
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email fails."""
        response = client.post('/api/login', json={
            'email': 'nobody@example.com',
            'password': 'anypassword'
        })
        
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client):
        """Test login without required fields."""
        response = client.post('/api/login', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400


class TestProtectedEndpoints:
    """Test JWT-protected endpoints."""
    
    def test_get_user_with_token(self, client, test_user, auth_headers):
        """Test accessing user info with valid token."""
        response = client.get(f'/api/users/{test_user["id"]}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == test_user['email']
    
    def test_get_user_without_token(self, client, test_user):
        """Test accessing protected endpoint without token fails."""
        response = client.get(f'/api/users/{test_user["id"]}')
        
        assert response.status_code == 401
        assert 'Authorization required' in response.get_json()['error']
    
    def test_get_user_invalid_token(self, client, test_user):
        """Test accessing with invalid token fails."""
        response = client.get(
            f'/api/users/{test_user["id"]}',
            headers={'Authorization': 'Bearer invalid.token.here'}
        )
        
        assert response.status_code == 401
    
    def test_get_me_endpoint(self, client, test_user, auth_headers):
        """Test /api/me returns current user."""
        response = client.get('/api/me', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.get_json()['email'] == test_user['email']


class TestPasswordReset:
    """Test password reset flow."""
    
    def test_password_reset_request(self, client, test_user):
        """Test requesting password reset returns token in dev mode."""
        response = client.post('/api/password-reset-request', json={
            'email': test_user['email']
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['dev_mode'] == True
        assert 'token' in data
    
    def test_password_reset_nonexistent_email(self, client):
        """Test reset request for non-existent email returns 404."""
        response = client.post('/api/password-reset-request', json={
            'email': 'nobody@example.com'
        })
        
        assert response.status_code == 404
    
    def test_password_reset_confirm(self, client, test_user):
        """Test full password reset flow."""
        # Request reset token
        reset_response = client.post('/api/password-reset-request', json={
            'email': test_user['email']
        })
        token = reset_response.get_json()['token']
        
        # Confirm reset with new password
        confirm_response = client.post('/api/password-reset-confirm', json={
            'email': test_user['email'],
            'token': token,
            'new_password': 'newSecurePass456'
        })
        
        assert confirm_response.status_code == 200
        
        # Verify new password works
        login_response = client.post('/api/login', json={
            'email': test_user['email'],
            'password': 'newSecurePass456'
        })
        
        assert login_response.status_code == 200
