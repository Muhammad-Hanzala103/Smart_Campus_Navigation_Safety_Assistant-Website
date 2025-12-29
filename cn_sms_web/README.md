# CNSMS - Campus Notification & Safety Management System

A production-ready Flask backend for campus security incident management with AI-powered threat detection.

## Features

- 🔐 **JWT Authentication** - Secure API authentication with token refresh
- 🔄 **Password Reset** - Email-based or dev-mode token reset
- 📸 **Incident Reporting** - Image upload with automatic AI analysis
- 🤖 **AI Analysis** - Hugging Face integration or mock mode
- 🗺️ **Map Intelligence** - Location-based incident visualization
- 📊 **Dashboard** - Real-time statistics and alerts
- 📱 **Android Ready** - Full REST API for mobile integration

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Initialize Database

```bash
python seed.py
```

### 4. Run Server

```bash
# Development
python app.py

# Production
gunicorn --bind 0.0.0.0:5000 app:app
```

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/register` | POST | No | Create account |
| `/api/login` | POST | No | Get JWT token |
| `/api/password-reset-request` | POST | No | Request reset |
| `/api/password-reset-confirm` | POST | No | Reset password |
| `/api/me` | GET | JWT | Current user |
| `/api/incidents` | GET/POST | JWT | List/Create |
| `/api/incidents/analyze` | POST | JWT | AI analysis |
| `/api/status` | GET | No | Health check |

See [api_spec.md](api_spec.md) for full documentation.

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@university.edu | admin123 |
| Officer | officer@university.edu | officer123 |
| User | user@university.edu | user123 |

## Android Integration

See [docs/android_integration.md](docs/android_integration.md)

## AI Configuration

See [docs/ai_integration.md](docs/ai_integration.md)

## Testing

```bash
pytest tests/ -v
```

## Docker

```bash
docker build -t cnsms .
docker run -p 5000:5000 --env-file .env cnsms
```

## License

MIT
