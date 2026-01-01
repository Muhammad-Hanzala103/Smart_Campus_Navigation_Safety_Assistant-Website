import os
import json
import requests
from datetime import datetime

class AIAnalyzer:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.environ.get('HUGGINGFACE_API_KEY')
        self.model = model or os.environ.get('HUGGINGFACE_MODEL', 'hustvl/yolos-tiny')
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def analyze_image(self, image_bytes):
        mode = os.environ.get('AI_MODE', 'mock').lower()
        if mode == 'mock':
            return self.mock_analyze(image_bytes)
        return self.analyze_with_hf(image_bytes)

    def analyze_with_hf(self, image_bytes):
        if not self.api_key:
            return self.mock_analyze(image_bytes)
        try:
            response = requests.post(self.api_url, headers=self.headers, data=image_bytes, timeout=30)
            if response.status_code == 200:
                return self.process_detections(response.json())
        except Exception as e:
            print(f"HF Exception: {e}")
        return self.mock_analyze(image_bytes)

    def mock_analyze(self, image_bytes):
        l = len(image_bytes)
        detections = []
        if l % 2 == 0:
            detections = [{"label": "person", "score": 0.95}, {"label": "person", "score": 0.88}]
        else:
            detections = [{"label": "fire", "score": 0.99}]
        return self.process_detections(detections)

    def process_detections(self, detections):
        labels = []
        person_count = 0
        fire_detected = False
        normalized = []
        
        if isinstance(detections, list):
            for d in detections:
                label = d.get('label', 'unknown').lower()
                score = d.get('score', 0)
                normalized.append({"label": label, "score": score})
                labels.append(label)
                if label == 'person':
                    person_count += 1
                if label in ['fire', 'smoke', 'flame'] and score > 0.6:
                    fire_detected = True

        severity, recommendation = self.decide_severity(person_count, fire_detected)
        return {"labels": json.dumps(normalized), "severity": severity, "recommendation": recommendation, "analyzed_at": datetime.utcnow()}

    def decide_severity(self, person_count, fire_detected):
        if fire_detected:
            return "HIGH", "Evacuate immediately. Fire detected."
        elif person_count >= 4:
            return "MEDIUM", "Crowd detected. Monitor situation."
        return "LOW", "No immediate threat detected."

analyzer = AIAnalyzer()
