import pytest
from app.ai_analyzer import analyzer
import os

def test_mock_analyzer_structure():
    # Force mock mode
    os.environ['AI_MODE'] = 'mock'
    
    # 10 bytes -> even length -> expects people
    dummy_data = b'1234567890' 
    result = analyzer.analyze_image(dummy_data)
    
    assert 'severity' in result
    assert 'recommendation' in result
    assert result['severity'] in ['LOW', 'MEDIUM', 'HIGH']
    
def test_mock_analyzer_fire():
    # 9 bytes -> odd length -> expects fire in mock logic
    dummy_data = b'123456789'
    result = analyzer.analyze_image(dummy_data)
    
    assert result['severity'] == 'HIGH'
    assert "Fire" in result['recommendation']
