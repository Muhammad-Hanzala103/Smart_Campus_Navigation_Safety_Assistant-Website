# API Specification

Base URL: `/api`

## Authentication

### POST /api/login
**Request**:
```json
{ "username": "admin", "password": "pass" }
```
**Response**:
```json
{ "status": "ok", "token": "..." }
```

### POST /api/logout
**Response**: `{"status": "logged out"}`

## Map

### GET /api/map
Returns map image path, nodes, and edges.

### POST /api/map/nodes
**Request**:
```json
{ "name": "Lab 1", "x": 100, "y": 200, "description": "..." }
```

### PUT /api/map/nodes/{id}
Update node position or details.

### DELETE /api/map/nodes/{id}
Remove a node.

## Incidents

### GET /api/incidents
Returns list of all incidents.

### POST /api/incidents
**Content-Type**: `multipart/form-data`
**Fields**: `category`, `description`, `x`, `y`, `image` (file)

## Bookings

### GET /api/bookings
Returns list of all bookings.

### POST /api/bookings
**Request**:
```json
{ "room_id": 1, "start_time": "2023-01-01T10:00:00", "end_time": "2023-01-01T12:00:00" }
```

### PUT /api/bookings/{id}/status
**Request**: `{ "status": "approved" }` (or "rejected")
