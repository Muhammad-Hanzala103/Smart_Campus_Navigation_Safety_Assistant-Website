# CN_SMS Backend

Campus Navigation and Safety Management System Backend Server.

## Features
- **Authentication**: JWT-based auth with Role-Based Access Control.
- **Map System**: Graph-based node/edge management for A* navigation.
- **Incident Reporting**: AI-powered analysis of incident images (HuggingFace Integration).
- **Bookings**: Room reservation with conflict detection.
- **Admin Dashboard**: Web interface for management and analytics.

## Quickstart

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   Copy `.env.example` to `.env` and configure keys.
   ```bash
   cp .env.example .env
   ```

3. **Initialize Database**
   ```bash
   python db_init.py
   ```

4. **Run Server**
   ```bash
   python wsgi.py
   ```
   Server runs at `http://localhost:5000`.

## API Documentation
See [api_spec.md](api_spec.md) for endpoint details. Requires Authorization header `Bearer <token>` for protected routes.

## Admin Dashboard
- URL: `http://localhost:5000/admin/login`
- Default Admin: `admin@cn.sms` / `password`

## Testing
Run `pytest` to execute the test suite.
