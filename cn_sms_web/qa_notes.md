# QA & DevOps Notes
**Lead**: [Third Member]

- Created `pytest` fixtures to mock database sessions using in-memory SQLite.
- CI Pipeline: GitHub Actions runs `pip install` and `pytest` on every push.
- **Coverage**: Critical paths (Map creation, Incident reporting) covered.
- **Docker**: Optimized `python:3.9-slim` image to keep size low.
