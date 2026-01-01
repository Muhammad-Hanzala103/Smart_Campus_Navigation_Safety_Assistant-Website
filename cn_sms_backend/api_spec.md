# CNSMS API Specification
Base URL: /api

## Authentication
### POST /auth/register
- JSON: {name, email, password, role}
- Returns: 201 Created

### POST /auth/login
- JSON: {email, password}
- Returns: 200 OK {token, user}

## Map
### GET /map
- Returns: {nodes: [], edges: [], map_image_url}

## Incidents
### POST /incidents
- Multipart: {category, description, x, y, image: File}
- Header: Authorization: Bearer <token>
- Returns: 201 Created {incident object}

### POST /incidents/analyze
- Multipart: {image: File} OR Form: {incident_id}
- Returns: {labels: string, severity: string, recommendation: string}

## Bookings
### POST /bookings
- JSON: {room_id, start_time (ISO), end_time (ISO)}
- Returns: 201 Created OR 409 Conflict
