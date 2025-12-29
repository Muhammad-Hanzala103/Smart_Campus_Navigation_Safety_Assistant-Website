"""
Test Incident Upload and AI Analysis
Tests incident creation and AI analysis endpoints.
"""
import pytest
import io


class TestIncidentUpload:
    """Test incident creation endpoint."""
    
    def test_create_incident_success(self, client, auth_headers, sample_image):
        """Test successful incident creation with image."""
        data = {
            'description': 'Suspicious person near building',
            'category': 'Suspicious',
            'location': 'Building A',
            'lat': '37.8715',
            'lng': '-122.2595'
        }
        data['image'] = (io.BytesIO(sample_image), 'test.png')
        
        response = client.post(
            '/api/incidents',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        result = response.get_json()
        assert 'incident_id' in result
        assert 'ai_result' in result
        assert result['ai_result']['severity'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    def test_create_incident_no_image(self, client, auth_headers):
        """Test incident creation fails without image."""
        response = client.post(
            '/api/incidents',
            data={'description': 'Test incident'},
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        assert 'Image file is required' in response.get_json()['error']
    
    def test_create_incident_no_auth(self, client, sample_image):
        """Test incident creation fails without authentication."""
        data = {
            'description': 'Test incident',
            'image': (io.BytesIO(sample_image), 'test.png')
        }
        
        response = client.post(
            '/api/incidents',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 401


class TestIncidentList:
    """Test incident listing endpoint."""
    
    def test_list_incidents_empty(self, client, auth_headers):
        """Test listing incidents returns empty list initially."""
        response = client.get('/api/incidents', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['incidents'] == []
        assert data['total'] == 0
    
    def test_list_incidents_with_data(self, client, auth_headers, sample_image):
        """Test listing incidents after creation."""
        # Create an incident first
        data = {
            'description': 'Test incident for listing',
            'category': 'Test',
            'location': 'Test Location',
            'image': (io.BytesIO(sample_image), 'test.png')
        }
        client.post(
            '/api/incidents',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        # List incidents
        response = client.get('/api/incidents', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1
        assert len(data['incidents']) == 1
        assert data['incidents'][0]['category'] == 'Test'


class TestAIAnalysis:
    """Test AI analysis endpoint."""
    
    def test_analyze_incident_success(self, client, auth_headers, sample_image):
        """Test AI analysis on created incident."""
        # Create incident
        create_data = {
            'description': 'Incident to analyze',
            'category': 'Analysis Test',
            'image': (io.BytesIO(sample_image), 'test.png')
        }
        create_response = client.post(
            '/api/incidents',
            data=create_data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        incident_id = create_response.get_json()['incident_id']
        
        # Analyze incident
        analyze_response = client.post(
            '/api/incidents/analyze',
            data={'incident_id': incident_id},
            headers=auth_headers
        )
        
        assert analyze_response.status_code == 200
        result = analyze_response.get_json()
        assert 'labels' in result
        assert 'severity' in result
        assert 'risk_score' in result
        assert 'recommendation' in result
    
    def test_analyze_with_image_upload(self, client, auth_headers, sample_image):
        """Test AI analysis with direct image upload."""
        data = {
            'image': (io.BytesIO(sample_image), 'analyze.png')
        }
        
        response = client.post(
            '/api/incidents/analyze',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert 'labels' in result
        assert 'severity' in result
    
    def test_analyze_nonexistent_incident(self, client, auth_headers):
        """Test analyzing non-existent incident fails."""
        response = client.post(
            '/api/incidents/analyze',
            json={'incident_id': 99999},
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestIncidentStatus:
    """Test incident status update."""
    
    def test_update_status(self, client, auth_headers, sample_image):
        """Test updating incident status."""
        # Create incident
        create_data = {
            'description': 'Status update test',
            'image': (io.BytesIO(sample_image), 'test.png')
        }
        create_response = client.post(
            '/api/incidents',
            data=create_data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        incident_id = create_response.get_json()['incident_id']
        
        # Update status
        update_response = client.patch(
            f'/api/incidents/{incident_id}/status',
            json={'status': 'resolved', 'resolution_notes': 'Issue handled.'},
            headers=auth_headers
        )
        
        assert update_response.status_code == 200
        assert update_response.get_json()['status'] == 'resolved'
    
    def test_update_invalid_status(self, client, auth_headers, sample_image):
        """Test updating with invalid status fails."""
        # Create incident
        create_data = {
            'description': 'Invalid status test',
            'image': (io.BytesIO(sample_image), 'test.png')
        }
        create_response = client.post(
            '/api/incidents',
            data=create_data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        incident_id = create_response.get_json()['incident_id']
        
        # Try invalid status
        update_response = client.patch(
            f'/api/incidents/{incident_id}/status',
            json={'status': 'invalid_status'},
            headers=auth_headers
        )
        
        assert update_response.status_code == 400
        assert 'Invalid status' in update_response.get_json()['error']
