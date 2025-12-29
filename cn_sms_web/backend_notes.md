# Backend Developer Notes
**Lead**: Muhammad Hanzala

- Implemented Flask Blueprints to separate Auth and API logic.
- Used `werkzeug.security` for standard PBKDF2 hashing.
- Database schema normalized to 3NF where possible; `AuditLog` added for traceability.
- **Challenge**: Handling circular imports between `app.py` and blueprints. **Solution**: Deferred imports inside `create_app`.
