# CNSMS Project Audit

**Project**: Campus Navigation and Safety Management System (CNSMS)
**Team**: Muhammad Hanzala, Haseeb Nawaz, [Third Member]
**Date**: December 29, 2025

---

## 1. Executive Summary
The CNSMS web application is a Flask-based backend with a Jinja2 frontend, designed to manage campus safety incidents. It features a hybrid authentication system (JWT for Android, Sessions for Web), an AI-powered incident analyzer (currently stubbed), and a SQLite database. The project structure is modular (Blueprints) and follows good separation of concerns.

**Status**: Alpha/Beta. Core features work, but UI polish and AI integration are in early stages.
**Critical Issues**: None blocking.
**Next Steps**: Polish UI, integrate real AI model, and finalize deployment.

---

## 2. Architecture & Tech Stack
- **Backend Framework**: Flask 3.0.0
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: Flask-Login (Web) + PyJWT (Android API)
- **AI Engine**: Modular Service Pattern (`ai_service.py` -> `ai_analyzer.py`)
- **Frontend**: HTML5, Bootstrap 5 (CDN), Jinja2 Templating
- **API**: RESTful JSON API (`/api/*`)

### Key Components
- `app/blueprints/auth.py`: Web Authentication
- `app/blueprints/api.py`: Core REST API
- `app/models.py`: Database Schema
- `app/services/ai_service.py`: AI Logic

---

## 3. Database Schema
Verified via `app/models.py`.

| Table | key Columns | Purpose |
|-------|-------------|---------|
| `User` | id, email, password_hash, role | User management |
| `Incident` | id, user_id, status, ai_severity, image_path | Core incident tracking |
| `MapNode` | id, name, x, y, node_type | Navigation graph nodes |
| `AuditLog` | id, user_id, action, ip_address | Security tracking |

---

## 4. API Endpoints
See `api_spec.md` for full details.
- **Auth**: `/api/register`, `/api/login`
- **Incidents**: `/api/incidents` (GET/POST), `/api/incidents/analyze`
- **System**: `/api/status`

---

## 5. Test Coverage
- **Unit Tests**: Generic logic coverage in `tests/`.
- **Status**: [Use tests/results.txt content here]

---

## 6. Security & HCI Audit
### Security Findings
1.  **Secret Management**: `.env` is used, but ensure `.env.example` does not contain real secrets.
2.  **Input Validation**: Implemented via `app/utils/validators.py`.
3.  **CORS**: Configured for `*` (All origins). **Fix**: Restrict to specific app domains in production.
4.  **Passwords**: Hashed with Werkzeug (good).

### HCI Findings
1.  **Mobile**: Frontend is responsive (Bootstrap), but map interaction on mobile web needs testing.
2.  **Feedback**: "Toast" notifications used for actions (good).
3.  **Accessibility**: Color contrast on "System Status" page needs check.

---

## 7. Next Steps & TODO
See `todo_tasks.md` for team assignments.
1.  Verify Android App connection (Completed).
2.  Run `quick_run.sh` to ensure fresh install works.
3.  Deploy to staging (e.g., Render/Heroku) for final presentation.
