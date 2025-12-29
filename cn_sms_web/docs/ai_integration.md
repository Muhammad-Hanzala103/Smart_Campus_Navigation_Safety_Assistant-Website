# AI Integration Guide

## Overview

CNSMS uses AI-powered image analysis to detect security threats and assess incident severity. The system supports two modes:

1. **Hugging Face API** - Production mode using real object detection
2. **Mock Analyzer** - Development/testing mode with deterministic results

## Configuration

Set environment variables in `.env`:

```env
# Mode: 'hf' for Hugging Face, 'mock' for testing
AI_MODE=mock

# Hugging Face API (required if AI_MODE=hf)
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx
HUGGINGFACE_MODEL=hustvl/yolos-tiny
```

## Getting Hugging Face API Key

1. Create account at [huggingface.co](https://huggingface.co)
2. Go to Settings → Access Tokens
3. Create new token with "read" permission
4. Copy token to `HUGGINGFACE_API_KEY`

## Supported Models

| Model | Description | Speed |
|-------|-------------|-------|
| `hustvl/yolos-tiny` | Fast object detection (default) | ~1s |
| `facebook/detr-resnet-50` | Higher accuracy | ~3s |

## Risk Assessment Rules

The AI service uses these rules to determine severity:

| Condition | Severity | Risk Score |
|-----------|----------|------------|
| Fire, smoke, weapon detected (>60% confidence) | CRITICAL | 90-100 |
| Crowd + suspicious object (backpack, suitcase) | HIGH | 70-89 |
| Crowd alone OR 4+ persons | MEDIUM | 40-69 |
| Normal objects only | LOW | 0-39 |

## API Response Format

```json
{
  "labels": [
    {"name": "person", "confidence": 0.92},
    {"name": "backpack", "confidence": 0.85}
  ],
  "severity": "MEDIUM",
  "risk_score": 55,
  "recommendation": "Caution: Elevated activity detected..."
}
```

## Privacy & Data Retention

- Images are stored locally on the server
- AI analysis is performed via API (no local model)
- No data is shared with third parties beyond HF API
- Consider implementing data retention policies for production

## Error Handling

The service handles these HF API errors gracefully:

- **429 Rate Limited**: Falls back to mock mode
- **503 Model Loading**: Retries or falls back
- **Timeout**: 30-second limit, then fallback

## Testing

Run mock mode for testing:

```bash
AI_MODE=mock python app.py
```

Mock analyzer uses image size as seed for deterministic results.
