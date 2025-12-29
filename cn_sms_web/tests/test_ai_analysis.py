import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
import json
import io
from app import create_app
from models import db, Incident, User
from ai_analyzer import mock_analyze, decide_severity

class TestAIAnalysis(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        # Create dummy test image
        self.test_img_path = os.path.join(self.app.root_path, 'static', 'test_ai.jpg')
        os.makedirs(os.path.dirname(self.test_img_path), exist_ok=True)
        with open(self.test_img_path, 'wb') as f:
            f.write(b'fakeimagebytes')
        
        with self.app.app_context():
            db.create_all()
            # Create user
            self.user = User(email='test@test.com', role='admin')
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        if os.path.exists(self.test_img_path):
            os.remove(self.test_img_path)
            
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_mock_analyzer_structure(self):
        """Test that mock analyzer returns correct keys"""
        img_bytes = b'fakeimagebytes'
        result = mock_analyze(img_bytes)
        self.assertIn('labels', result)
        self.assertIn('severity', result)
        self.assertIn('recommendation', result)
        self.assertTrue(len(result['labels']) > 0)

    def test_severity_logic(self):
        """Test severity rules"""
        # High
        self.assertEqual(decide_severity([{'name': 'fire', 'confidence': 0.9}]), 'HIGH')
        self.assertEqual(decide_severity([{'name': 'weapon', 'confidence': 0.8}]), 'HIGH')
        
        # Medium
        self.assertEqual(decide_severity([{'name': 'crowd', 'confidence': 0.8}]), 'MEDIUM')
        
        # Low
        self.assertEqual(decide_severity([{'name': 'cat', 'confidence': 0.9}]), 'LOW')

    @patch('ai_analyzer.analyze_image')
    def test_analyze_endpoint(self, mock_analyze_func):
        """Test API endpoint"""
        # Login
        with self.client.session_transaction() as sess:
            sess['_user_id'] = 1

        # Create incident
        with self.app.app_context():
            inc = Incident(user_id=1, description="Test", image_path="/static/test_ai.jpg")
            db.session.add(inc)
            db.session.commit()
            inc_id = inc.id

        # Mock result
        mock_res = {
            "labels": [{"name": "test", "confidence": 0.9}],
            "severity": "LOW",
            "recommendation": "None",
            "analyzed_at": "2025-01-01T12:00:00Z"
        }
        mock_analyze_func.return_value = mock_res
        
        # Test request
        res = self.client.post('/api/incidents/analyze', json={'incident_id': inc_id})
                
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['severity'], 'LOW')
        
        # Verify DB update
        with self.app.app_context():
            inc = Incident.query.get(inc_id)
            self.assertEqual(inc.ai_severity, 'LOW')

if __name__ == '__main__':
    unittest.main()
