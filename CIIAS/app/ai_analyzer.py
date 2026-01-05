import os
import json
import random
import requests
from datetime import datetime

class AIAnalyzer:
    """AI-powered image analysis for incident categorization"""
    
    # Category mappings for detected objects
    CATEGORY_MAPPING = {
        'fire': 'fire',
        'smoke': 'fire',
        'flame': 'fire',
        'person': 'security',
        'people': 'security',
        'crowd': 'security',
        'car': 'accident',
        'vehicle': 'accident',
        'truck': 'accident',
        'blood': 'medical',
        'injury': 'medical',
        'ambulance': 'medical',
        'broken': 'infrastructure',
        'damage': 'infrastructure',
        'crack': 'infrastructure'
    }
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.environ.get('HUGGINGFACE_API_KEY')
        self.model = model or os.environ.get('HUGGINGFACE_MODEL', 'hustvl/yolos-tiny')
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def analyze_image(self, image_bytes):
        """Analyze image and return category, severity, and confidence"""
        mode = os.environ.get('AI_MODE', 'mock').lower()
        
        if mode == 'mock':
            return self.mock_analyze(image_bytes)
        
        return self.analyze_with_hf(image_bytes)

    def analyze_with_hf(self, image_bytes):
        """Analyze image using HuggingFace API"""
        if not self.api_key:
            return self.mock_analyze(image_bytes)
        
        try:
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                data=image_bytes, 
                timeout=30
            )
            
            if response.status_code == 200:
                detections = response.json()
                return self.process_detections(detections)
        except Exception as e:
            print(f"HuggingFace API Exception: {e}")
        
        return self.mock_analyze(image_bytes)

    def mock_analyze(self, image_bytes):
        """Mock analysis for testing without API"""
        # Use image size as pseudo-random seed for consistent testing
        size = len(image_bytes) if image_bytes else 0
        random.seed(size)
        
        # Generate mock detections based on image characteristics
        categories = ['security', 'fire', 'medical', 'accident', 'infrastructure']
        severities = ['low', 'medium', 'high']
        
        # Pseudo-random selection
        category = categories[size % len(categories)]
        severity = severities[size % len(severities)]
        confidence = 0.65 + (size % 35) / 100  # 0.65 to 0.99
        
        # Create mock detections for processing
        if category == 'fire':
            detections = [
                {"label": "fire", "score": confidence},
                {"label": "smoke", "score": confidence - 0.1}
            ]
        elif category == 'security':
            detections = [
                {"label": "person", "score": confidence},
                {"label": "person", "score": confidence - 0.05},
                {"label": "person", "score": confidence - 0.1}
            ]
        else:
            detections = [
                {"label": category, "score": confidence}
            ]
        
        return self.process_detections(detections)

    def process_detections(self, detections):
        """Process detections and determine category, severity, and confidence"""
        labels = []
        max_score = 0
        person_count = 0
        fire_detected = False
        main_category = 'security'
        
        if isinstance(detections, list):
            for d in detections:
                label = d.get('label', 'unknown').lower()
                score = d.get('score', 0)
                labels.append({"label": label, "score": score})
                
                if score > max_score:
                    max_score = score
                    # Determine category from label
                    for keyword, cat in self.CATEGORY_MAPPING.items():
                        if keyword in label:
                            main_category = cat
                            break
                
                if label == 'person':
                    person_count += 1
                
                if label in ['fire', 'smoke', 'flame'] and score > 0.6:
                    fire_detected = True

        # Determine severity
        severity = self._determine_severity(person_count, fire_detected, max_score)
        recommendation = self._get_recommendation(main_category, severity)

        return {
            "category": main_category,
            "severity": severity,
            "confidence": round(max_score, 2),
            "labels": json.dumps(labels),
            "recommendation": recommendation,
            "analyzed_at": datetime.utcnow()
        }

    def _determine_severity(self, person_count, fire_detected, confidence):
        """Determine severity based on detections"""
        if fire_detected:
            return "high"
        elif person_count >= 5:
            return "high"
        elif person_count >= 3:
            return "medium"
        elif confidence > 0.9:
            return "high"
        elif confidence > 0.7:
            return "medium"
        return "low"

    def _get_recommendation(self, category, severity):
        """Get recommendation based on category and severity"""
        recommendations = {
            'fire': {
                'high': 'EVACUATE IMMEDIATELY. Contact fire department. Do not use elevators.',
                'medium': 'Alert security. Prepare for possible evacuation. Monitor situation.',
                'low': 'Investigate source. Have fire extinguisher ready.'
            },
            'security': {
                'high': 'Contact security immediately. Avoid the area if possible.',
                'medium': 'Monitor situation. Alert security if behavior is suspicious.',
                'low': 'Normal activity detected. No immediate action required.'
            },
            'medical': {
                'high': 'Call emergency services immediately. Do not move injured person.',
                'medium': 'Contact campus medical services. Provide first aid if trained.',
                'low': 'Minor incident. Medical kit may be sufficient.'
            },
            'accident': {
                'high': 'Call emergency services. Secure the area. Do not move vehicles.',
                'medium': 'Contact security. Document the incident. Check for injuries.',
                'low': 'Minor incident. Exchange information if applicable.'
            },
            'infrastructure': {
                'high': 'Evacuate area immediately. Contact maintenance and security.',
                'medium': 'Report to maintenance. Avoid the affected area.',
                'low': 'Schedule repair. Mark area for attention.'
            }
        }
        
        return recommendations.get(category, {}).get(severity, 'Review incident and take appropriate action.')


# Global analyzer instance
analyzer = AIAnalyzer()
