# CNSMS API Specification

**Base URL**: `/api`
**Version**: 1.0.0
**Auth**: Bearer Token (JWT) or Session Cookie

---

## 1. Authentication (`/auth`)

### Register User
- **Endpoint**: `POST /api/register`
- **Description**: Create a new user account.
- **Body**:
  ```json
  {
    "name": "John Doe",
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response (201)**:
  ```json
  {
    "message": "User registered successfully",
    "user_id": 1
  }
  ```

### Login
- **Endpoint**: `POST /api/login`
- **Description**: Authenticate and receive JWT token.
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response (200)**:
  ```json
  {
    "message": "Login successful",
    "token": "eyJhbGciOiJIUzI1Ni...",
    "user": { "id": 1, "name": "John Doe", "role": "user" }
  }
  ```

### Password Reset Request
- **Endpoint**: `POST /api/password-reset-request`
- **Body**: `{"email": "user@example.com"}`

### Password Reset Confirm
- **Endpoint**: `POST /api/password-reset-confirm`
- **Body**: `{"email": "...", "token": "...", "new_password": "..."}`

---

## 2. Incidents (`/incidents`)

### List Incidents
- **Endpoint**: `GET /api/incidents`
- **Params**:
  - `status`: (optional) new, resolved
  - `limit`: (optional) default 50
- **Response (200)**:
  ```json
  {
    "incidents": [
      {
        "id": 1,
        "description": "Fire in lab",
        "lat": 34.01,
        "lng": 71.54,
        "ai_severity": "HIGH"
      }
    ],
    "total": 1
  }
  ```

### Create Incident
- **Endpoint**: `POST /api/incidents`
- **Type**: `multipart/form-data`
- **Params**:
  - `description`: Text
  - `lat`, `lng`: Float
  - `image`: File (required)
- **Response (201)**:
  ```json
  {
    "message": "Incident created",
    "incident_id": 5,
    "ai_result": { "severity": "HIGH", "confidence": 0.98 }
  }
  ```

### Analyze Incident (AI)
- **Endpoint**: `POST /api/incidents/analyze`
- **Body**: `{"incident_id": 1}` OR Multipart `image` upload.
- **Response (200)**: returns AI analysis results.

---

## 3. System Status (`/status`)

### Health Check
- **Endpoint**: `GET /api/status`
- **Response (200)**:
  ```json
  {
    "status": "online",
    "ai_mode": "mock",
    "timestamp": "2025-12-29T..."
  }
  ```
