# SSNS Admin Dashboard

A lightweight, Flask-based Admin Dashboard for the Smart Security & Navigation System (SSNS).

## Features
- **Map Management**: Interactive map editor to place nodes (Rooms, Gates, Labs) on an SVG map.
- **Incident Tracking**: View and update status of reported incidents (with images).
- **Room Booking**: Approve or reject room booking requests with conflict detection.
- **User Management**: View registered users (Admin, Security, Staff).
- **Analytics**: Basic charts for incidents and bookings.

## Tech Stack
- **Backend**: Flask + SQLAlchemy (SQLite)
- **Frontend**: Jinja2 + Vanilla JS + CSS
- **Libs**: Chart.js (CDN), Axios (CDN)

## Quick Start

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Initialize Database**:
    ```bash
    export FLASK_APP=app.py
    flask init-db
    ```
    *(This creates `ssns.db` and fills it with demo data)*

3.  **Run Application**:
    ```bash
    flask run
    ```

4.  **Login**:
    - **Admin**: `admin` / `pass`
    - **Security**: `security1` / `pass`

## Project Structure
- `app.py`: Main Flask application and API.
- `models.py`: Database models.
- `templates/`: HTML files.
- `static/`: CSS, JS, Images.

## Deployment
For production (e.g., Render/Heroku):
- Set `SECRET_KEY` and `DATABASE_URL` env vars.
- Run with Gunicorn: `gunicorn app:app`.
