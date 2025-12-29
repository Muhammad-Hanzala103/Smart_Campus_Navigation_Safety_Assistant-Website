"""
AI Service - Hugging Face Integration with Mock Fallback
Provides image analysis for incident detection and risk assessment.
"""
import os
import random
import requests
from datetime import datetime
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class AIService:
    """
    AI Service for image analysis.
    
    Modes:
        - 'hf': Use Hugging Face Inference API (requires HUGGINGFACE_API_KEY)
        - 'mock': Use deterministic mock analyzer (default)
    
    The service analyzes images and returns:
        - labels: List of detected objects with confidence scores
        - severity: CRITICAL, HIGH, MEDIUM, or LOW
        - risk_score: 0-100 numeric score
        - recommendation: Action recommendation based on findings
    """
    
    def __init__(self):
        """Initialize AI service with configuration from environment."""
        self.mode = os.environ.get('AI_MODE', 'mock').lower()
        self.api_key = os.environ.get('HUGGINGFACE_API_KEY')
        self.model = os.environ.get('HUGGINGFACE_MODEL', 'hustvl/yolos-tiny')
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.timeout = 30  # seconds
    
    def analyze_image(self, image_bytes: bytes) -> dict:
        """
        Main entry point for image analysis.
        
        Args:
            image_bytes: Raw image file bytes
        
        Returns:
            dict: {
                "labels": [{"name": str, "confidence": float}, ...],
                "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
                "risk_score": int (0-100),
                "recommendation": str,
                "analyzed_at": datetime
            }
        """
        if self.mode == 'hf' and self.api_key:
            try:
                raw_labels = self._call_hf_api(image_bytes)
                logger.info(f"HF API analysis complete: {len(raw_labels)} labels detected")
            except Exception as e:
                logger.warning(f"HF API failed: {e}. Falling back to mock.")
                raw_labels = self._mock_analyze(image_bytes)
        else:
            raw_labels = self._mock_analyze(image_bytes)
        
        risk_score, severity = self._calculate_risk(raw_labels)
        recommendation = self._generate_recommendation(severity, raw_labels)
        
        return {
            "labels": raw_labels,
            "risk_score": risk_score,
            "severity": severity,
            "recommendation": recommendation,
            "analyzed_at": datetime.utcnow()
        }
    
    def _call_hf_api(self, image_bytes: bytes) -> list:
        """
        Call Hugging Face Inference API for object detection.
        
        Args:
            image_bytes: Raw image bytes
        
        Returns:
            List of label dicts: [{"name": str, "confidence": float}, ...]
        
        Raises:
            Various exceptions on API failure
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=image_bytes,
                timeout=self.timeout
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                logger.warning("HF API rate limited (429)")
                raise Exception("Rate limited by Hugging Face API")
            
            # Handle model loading
            if response.status_code == 503:
                logger.warning("HF model loading (503)")
                raise Exception("Model is loading, try again shortly")
            
            response.raise_for_status()
            predictions = response.json()
            
            # Normalize predictions to simple labels list
            # Standard HF Object Detection output format:
            # [{'score': 0.9, 'label': 'cat', 'box': {...}}, ...]
            labels = []
            for pred in predictions:
                if isinstance(pred, dict) and 'label' in pred and 'score' in pred:
                    labels.append({
                        "name": pred['label'],
                        "confidence": round(pred['score'], 2)
                    })
            
            return sorted(labels, key=lambda x: x['confidence'], reverse=True)
            
        except requests.exceptions.Timeout:
            logger.error("HF API timeout")
            raise Exception("API request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"HF API request failed: {e}")
            raise
    
    def _mock_analyze(self, image_bytes: bytes) -> list:
        """
        Deterministic mock analyzer for testing.
        
        Uses image size as seed for reproducible results.
        
        Args:
            image_bytes: Raw image bytes
        
        Returns:
            List of mock labels
        """
        # Seed based on image size for deterministic output
        seed_val = len(image_bytes)
        random.seed(seed_val)
        
        # Possible detection labels (security-relevant)
        possible_labels = [
            "person", "backpack", "bicycle", "car", 
            "smoke", "fire", "knife", "crowd",
            "dog", "umbrella", "suitcase", "cell phone"
        ]
        
        # Pick 1-4 random labels
        num_labels = random.randint(1, 4)
        selected = random.sample(possible_labels, num_labels)
        
        labels = []
        for name in selected:
            labels.append({
                "name": name,
                "confidence": round(random.uniform(0.70, 0.99), 2)
            })
        
        logger.info(f"Mock analysis: {len(labels)} labels generated")
        return labels
    
    def _calculate_risk(self, labels: list) -> tuple:
        """
        Calculate risk score and severity based on detected labels.
        
        Risk Rules:
            - CRITICAL (90-100): fire, smoke, weapon, gun, knife with conf > 0.6
            - HIGH (70-89): crowd + suspicious object
            - MEDIUM (40-69): crowd alone, multiple persons
            - LOW (0-39): Normal objects only
        
        Args:
            labels: List of detected labels with confidence
        
        Returns:
            Tuple of (risk_score: int, severity: str)
        """
        label_names = [l['name'].lower() for l in labels]
        confidences = {l['name'].lower(): l['confidence'] for l in labels}
        
        # CRITICAL: Immediate threats
        critical_items = ['fire', 'smoke', 'weapon', 'gun', 'knife']
        for item in critical_items:
            if item in label_names and confidences.get(item, 0) > 0.6:
                return 95, "CRITICAL"
        
        # HIGH: Crowd with suspicious objects
        has_crowd = 'crowd' in label_names
        suspicious = ['backpack', 'suitcase', 'knife']
        has_suspicious = any(s in label_names for s in suspicious)
        
        if has_crowd and has_suspicious:
            return 78, "HIGH"
        
        # MEDIUM: Crowd or many persons
        person_count = sum(1 for l in label_names if l == 'person')
        if has_crowd or person_count >= 4:
            return 55, "MEDIUM"
        
        # LOW: Normal activity
        if len(labels) > 3:
            return 35, "LOW"
        
        return 15, "LOW"
    
    def _generate_recommendation(self, severity: str, labels: list) -> str:
        """
        Generate action recommendation based on severity and findings.
        
        Args:
            severity: Calculated severity level
            labels: List of detected labels
        
        Returns:
            Human-readable recommendation string
        """
        names = ", ".join([l['name'] for l in labels[:5]])  # Limit to 5 for readability
        
        recommendations = {
            "CRITICAL": f"URGENT: Immediate threat detected ({names}). "
                       f"Dispatch security team immediately. Evacuate if necessary.",
            "HIGH": f"High Risk: Potential hazard detected ({names}). "
                   f"Increase monitoring and prepare response team.",
            "MEDIUM": f"Caution: Elevated activity detected ({names}). "
                     f"Monitor via CCTV and log for analysis.",
            "LOW": f"Routine: No significant threats detected. "
                  f"Objects identified: {names if names else 'none'}."
        }
        
        return recommendations.get(severity, "Unable to generate recommendation.")


# Global instance
ai_service = AIService()
