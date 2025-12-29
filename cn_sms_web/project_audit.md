# CNSMS Project Audit & Analysis Report

**Project Type:** Flask (Python) Web Application + Android Backend API
**Role:** Campus Navigation and Safety Management System (CNSMS)
**Auditor**: AI Analysis Assistant
**Date**: December 29, 2025

---

## 1. Project Overview

### What is this project?
This is a **Safety & Navigation Management System** built with **Flask (Python)**.
It serves two main purposes:
1.  **Web Dashboard**: For administrators/officers to view incidents, see a heatmap of dangers, and manage the system.
2.  **Android Backend API**: Provides data (incidents, authentication, map logic) to a mobile app (Android).

**Core Problem Solved**:  
Helping campus security track incidents (theft, fire, medical questions) in real-time and providing students with a way to report them.

**Users**:
- **Students (Mobile)**: Report incidents, view map.
- **Security Officers (Web)**: view dashboard, update incident status.
- **Admins (Web)**: Manage users and system health.

**System Flow**:
1.  User (Mobile/Web) **Reports Incident** (Description + Photo).
2.  Backend **Analyzes Image** (AI Service) -> Assigns Severity (High/Low).
3.  Admin **Reviews** on Dashboard -> Updates Status (Resolved).
4.  User sees **Update** on their device.

---

## 2. Folder & File Explanation

### Root Directory `cn_sms_web/`
| File / Folder | Purpose |
|:---|:---|
| `app.py` | **Entry Point**. Starts the Flask server. Binds to `0.0.0.0:5000`. |
| `config.py` | **Settings**. Database URL, Secret Keys, Upload folder paths. |
| `models.py` | **Database Schema**. Defines Tables: `User`, `Incident`, `AuditLog`. |
| `db_init.py` | **Setup Script**. Creates the SQLite database file (`instance/cnsms.db`). |
| `seed.py` | **Demo Data**. Fills the database with fake users and incidents for testing. |
| `requirements.txt` | **Dependencies**. Lists Python libraries needed (Flask, SQLAlchemy, PyJWT). |

### App Logic `app/`
| File / Folder | Purpose |
|:---|:---|
| `__init__.py` | **App Factory**. Initializes Flask, DB, LoginManager, and CORS. |
| `blueprints/` | **Routes**. Groups code by feature: `auth` (web login), `api` (mobile data), `dashboard` (web UI). |
| `services/` | **Business Logic**. `ai_service.py` handles image analysis logic. `email_service.py` handles reset emails. |
| `utils/` | **Helpers**. `jwt_auth.py` (API security), `validators.py` (data checking). |

### Frontend `templates/` & `static/`
- **templates/**: HTML files (Jinja2). `base.html` (layout), `login.html`, `dashboard.html`.
- **static/**: CSS (Styles), JS (Scripts), Uploads (Images).

---

## 3. Backend Logic (Detailed)

### Authentication Flow
The system uses a **Hybrid Auth** approach:
1.  **Web Browsers**: Use **Sessions** (`Flask-Login`).
    - Login: `POST /login` -> Validates password -> Sets `session` cookie.
    - Access: Middleware checks `current_user.is_authenticated`.
2.  **Mobile Apps**: Use **JWT Tokens** (`PyJWT`).
    - Login: `POST /api/login` -> Returns `{ "token": "ey..." }`.
    - Access: Android sends header `Authorization: Bearer <token>`.
    - Middleware: `@auth_required` decodes token -> Sets `g.current_user`.

### Key API Endpoints
- **GET /api/incidents**: Returns list of incidents (JSON).
- **POST /api/incidents**: Upload incident (Multipart: text + image).
- **POST /api/login**: Get JWT Token.
- **GET /api/status**: Health check (online/offline).

### Data Flow Example (Incident Reporting)
1.  **Frontend**: Sends `POST /api/incidents` with image.
2.  **Backend**:
    - Validates file type.
    - Saves image to `static/uploads`.
    - Calls `ai_service.analyze_image()` -> Returns "High Risk".
    - Saves properties to `Incident` table (DB).
3.  **Response**: Returns `201 Created` with new Incident ID.

---

## 4. Database & Data Flow
**Database Engine**: **SQLite** (File-based).
**File Location**: `instance/cnsms.db`.

### Key Tables
1.  **User**: `id, email, password_hash, role`.
2.  **Incident**: `id, description, image_path, status, ai_severity`.
3.  **AuditLog**: `id, action ("LOGIN_FAILED"), timestamp`.

**Data Lifecycle**:
User Input -> API Validation -> ORM Object (Python) -> SQL INSERT -> SQLite File.

---

## 5. Frontend Behavior
- **Dashboard**: Shows charts (Chart.js) of incidents by category.
- **Map**: Uses Leaflet.js to show pins on a floorplan image.
- **Login/Register**: Standard HTML forms.
- **System Status**: Real-time fetch from `/api/status`.

**API Calls in Frontend**:
- Unlike typical "Single Page Apps", this app renders HTML on server.
- **But**, the Map and Status pages use `fetch('/api/...')` to get live data dynamically to avoid page reloads.

---

## 6. AI Implementation
**Status**: **Stubbed / Mock**.
- **File**: `app/services/ai_analyzer.py`
- **Current Logic**:
  - The code is set to **Mock Mode**.
  - It does **not** call HuggingFace or OpenAI.
  - It generates **random** severity (Low/High) for demo purposes.
- **Input**: Accepts image bytes.
- **Result**: Returns JSON `{ "severity": "HIGH", "confidence": 0.88 }`.
- **UI**: Shows "AI Analysis Result" badge on Incident details page.

**Honest Assessment**: The AI "plumbing" is there, but the "brain" is random for now (which is fine for a demo).

---

## 7. Complete vs Incomplete

### ✅ Working Features
- Login / Register / Forgot Password (Web + API).
- Dashboard with Charts.
- Incident Reporting (Upload + Save).
- System Status Page.
- Map Page (Markers load).
- Android Connection (CORS + Host 0.0.0.0).

### ⚠️ Incomplete / Missing
- **Real AI**: Currently using random mock data.
- **Detailed Map Editor**: `map_editor.html` exists but is basic.
- **User Profile Edit**: API exists (`GET /me`), but no Web UI to edit profile.
- **Email Sending**: Forgot Password generates token in logs (Dev mode), doesn't actually send SMTP email (Production).

---

## 8. Common Errors & Weak Points

1.  **Authentication Confusion**: (Fixed) Previously, Web UI tried to use API endpoints without JWTs. Fixed by "Hybrid Auth" update.
2.  **Security - CORS**: Currently allows `*` (All origins). Risky for production.
3.  **Security - Secrets**: Secret keys are in `config.py` default. Should be strictly env vars in production.
4.  **Performance - Images**: User can upload 10MB images. No resize logice logic. This will fill up disk space fast.
5.  **UI - Mobile Web**: The Dashboard tables might break layout on very small phone screens (needs `overflow-x: auto`).

---

## 9. Explanation for Team (5 Minutes)
*"Hey team, here is what we have:*
1.  *We built a **Python server** that stores all our data.*
2.  *It has a **Web Dashboard** for us (admins) to see charts and maps.*
3.  *It has an **API** for the Android App to talk to.*
4.  *The **AI Part** works like this: You upload a photo, the server pretends to scan it (demo mode), and saves the result.*
5.  *Everything runs on my laptop. The phone connects via **USB Tunnel** (ADB) so we don't have WiFi issues.*
6.  *The Login works for both web and phone because we implemented a special hybrid security system."*

---

## 10. Summary
This is a solid **MVP (Minimum Viable Product)**.
It demonstrates the full loop: **Mobile -> Cloud -> Web Admin**.

- **It is NOT**: A production-ready SaaS (needs HTTPS, real Email, real AI).
- **Easy Win**: Customize the Dashboard colors to look more "Security" themed.
- **Hard Part Done**: The Android-to-Server connection is stable.
