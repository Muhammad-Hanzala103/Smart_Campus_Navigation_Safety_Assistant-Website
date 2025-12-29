import os
import io
import json
import random
import requests
from datetime import datetime

# Configuration
AI_MODE = os.environ.get("AI_MODE", "mock").lower()
HF_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
HF_MODEL = os.environ.get("HUGGINGFACE_MODEL", "hustvl/yolos-tiny")

HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

def analyze_image(image_bytes):
    """
    Main entry point for image analysis.
    Dispatches to HF or Mock based on configuration.
    Returns:
        dict: {
            "labels": [{"name": str, "confidence": float}, ...],
            "severity": "HIGH" | "MEDIUM" | "LOW",
            "recommendation": str,
            "analyzed_at": str (ISO 8601)
        }
    """
    if AI_MODE == "hf" and HF_API_KEY:
        results = analyze_with_hf(image_bytes)
    else:
        results = mock_analyze(image_bytes)
    
    # Enrich with severity and recommendation if not already present (handled by sub-functions, but safety check)
    if "severity" not in results:
        results["severity"] = decide_severity(results.get("labels", []))
    if "recommendation" not in results:
        results["recommendation"] = generate_recommendation(results["severity"], results.get("labels", []))
    
    results["analyzed_at"] = datetime.utcnow().isoformat() + "Z"
    return results

def analyze_with_hf(image_bytes):
    """
    Calls Hugging Face Inference API for Object Detection.
    """
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    try:
        response = requests.post(HF_API_URL, headers=headers, data=image_bytes)
        response.raise_for_status()
        predictions = response.json()
        
        # Normalize predictions to simple labels list
        # Standard HF Object Detection output: [{'score': 0.9, 'label': 'cat', 'box': {...}}, ...]
        labels = []
        for pred in predictions:
            if isinstance(pred, dict) and 'label' in pred and 'score' in pred:
                labels.append({
                    "name": pred['label'],
                    "confidence": round(pred['score'], 2)
                })
        
        # Sort by confidence desc
        labels = sorted(labels, key=lambda x: x['confidence'], reverse=True)
        
        severity = decide_severity(labels)
        recommendation = generate_recommendation(severity, labels)

        return {
            "labels": labels,
            "severity": severity,
            "recommendation": recommendation
        }

    except Exception as e:
        print(f"HF Analysis Failed: {e}")
        # Fallback to mock if HF fails? Or return error? 
        # Requirement says "fallback behavior: when no API key present". 
        # If key IS present but fails, currently we'll return an error or empty. 
        # Let's return error structure so user knows.
        return {
            "labels": [],
            "severity": "LOW",
            "recommendation": f"Analysis failed: {str(e)}. Please try again or switch to Mock mode."
        }

def mock_analyze(image_bytes):
    """
    Deterministic mock analyzer.
    Returns plausible labels based on simple rules or random-seeded generation.
    Since we don't have filename in bytes, we'll use bytes length to seed randomness 
    so it's deterministic for the same file.
    """
    # Seed based on image size to be deterministic per image
    seed_val = len(image_bytes)
    random.seed(seed_val)
    
    possible_labels = ["person", "backpack", "car", "bicycle", "smoke", "fire", "crowd", "dog", "umbrella"]
    
    # Pick 1-4 random labels
    num_labels = random.randint(1, 4)
    selected = random.sample(possible_labels, num_labels)
    
    labels = []
    for name in selected:
        conf = round(random.uniform(0.70, 0.99), 2)
        labels.append({"name": name, "confidence": conf})
    
    # Special case: very small images might mean "icon" or "test" -> empty? 
    # Let's keep it simple.

    severity = decide_severity(labels)
    recommendation = generate_recommendation(severity, labels)
    
    return {
        "labels": labels,
        "severity": severity,
        "recommendation": recommendation
    }

def decide_severity(labels):
    """
    Rule-based severity determination.
    """
    # flatten label names
    label_names = [l['name'].lower() for l in labels]
    
    # CRITICAL RULES
    if 'fire' in label_names or 'smoke' in label_names or 'weapon' in label_names:
        return "HIGH"
    
    # MEDIUM RULES
    person_count = sum(1 for l in label_names if l == 'person')
    if person_count >= 4 or 'crowd' in label_names:
        return "MEDIUM"
        
    if 'knife' in label_names or 'bat' in label_names: # some suspicious objects
        return "HIGH"

    # DEFAULT
    return "LOW"

def generate_recommendation(severity, labels):
    label_str = ", ".join([l['name'] for l in labels])
    
    if severity == "HIGH":
        return f"Urgent: Dangerous elements detected ({label_str}). Dispatch security detail immediately."
    elif severity == "MEDIUM":
        return f"Caution: Unusual activity or crowd detected ({label_str}). Monitor via CCTV."
    else:
        return f"No significant threats detected. Routine logging only."
