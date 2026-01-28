from app import create_app, db
from app.models import (
    Course, Shuttle, Book, MapNode, User, 
    Organization, Campus, Department, Program, StaffDetail,
    CafeteriaItem, CafeteriaOrder, AuditLog, Incident, University
)
from datetime import datetime
from sqlalchemy import text

app = create_app(init_blueprints=False)

def add_column_if_missing(conn, table, column, col_type):
    try:
        conn.execute(text(f"SELECT {column} FROM {table} LIMIT 1"))
    except Exception:
        print(f"Adding column '{column}' to table '{table}'...")
        try:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
            conn.commit()
        except Exception as e:
            print(f"Error adding column {column}: {e}")

with app.app_context():
    print("Step 1: Creating any missing tables...")
    db.create_all()
    
    print("Step 2: Patching existing tables for Industrial Sync...")
    with db.engine.connect() as conn:
        # Patch User
        user_cols = [
            ("university_id", "INTEGER"),
            ("totp_secret", "VARCHAR(32)"),
            ("is_2fa_enabled", "BOOLEAN DEFAULT 0"),
            ("twofactor_method", "VARCHAR(20) DEFAULT 'email'"),
            ("otp_code", "VARCHAR(6)"),
            ("otp_expiry", "DATETIME"),
            ("backup_codes", "TEXT"),
            ("campus_id", "INTEGER"),
            ("dept_id", "INTEGER"),
            ("fcm_token", "VARCHAR(256)")
        ]
        for col, ctype in user_cols:
            add_column_if_missing(conn, "users", col, ctype)

        # Patch AuditLog
        audit_cols = [
            ("university_id", "INTEGER"),
            ("resource", "VARCHAR(100)"),
            ("ip_address", "VARCHAR(45)"),
            ("status", "VARCHAR(20) DEFAULT 'success'")
        ]
        for col, ctype in audit_cols:
            add_column_if_missing(conn, "audit_logs", col, ctype)

        # Patch Incident
        add_column_if_missing(conn, "incidents", "university_id", "INTEGER")
        
        # Patch Courses (legacy check)
        add_column_if_missing(conn, "courses", "credit_hours", "INTEGER DEFAULT 3")
        
        # Patch Shuttles
        shuttle_cols = [
            ("driver_id", "INTEGER"),
            ("capacity", "INTEGER"),
            ("model", "VARCHAR(50)"),
            ("campus_id", "INTEGER")
        ]
        for col, ctype in shuttle_cols:
            add_column_if_missing(conn, "shuttles", col, ctype)

        # Patch MapNodes
        add_column_if_missing(conn, "map_nodes", "altitude", "FLOAT DEFAULT 0.0")

        # Patch Campuses
        add_column_if_missing(conn, "campuses", "latitude", "FLOAT")
        add_column_if_missing(conn, "campuses", "longitude", "FLOAT")

    print("Step 3: Seeding basic industrial data...")
    # Organization
    org = Organization.query.filter_by(code="CGU").first()
    if not org:
        org = Organization(name="CIIAS Global University", code="CGU", website="https://ciias.edu")
        db.session.add(org)
        db.session.commit()
        print("Organization created.")

    # University (SaaS Multi-tenant root)
    uni = University.query.filter_by(slug="ciias").first()
    if not uni:
        uni = University(name="CIIAS Home University", slug="ciias", 
                         domain="university.edu", api_key="dev-pk-123456789")
        db.session.add(uni)
        db.session.commit()
        print("Default University Link created.")

    # Campus
    campus = Campus.query.filter_by(name="Islamabad Main Campus").first()
    if not campus:
        campus = Campus(
            org_id=org.id, 
            name="Islamabad Main Campus", 
            location="Sector H-12, Islamabad",
            latitude=33.6518,
            longitude=73.1566
        )
        db.session.add(campus)
        db.session.commit()
        print("Main Campus created.")

    # Ensure all users have university_id and campus_id
    if uni and campus:
        for user in User.query.filter_by(university_id=None).all():
            user.university_id = uni.id
        for user in User.query.filter_by(campus_id=None).all():
            user.campus_id = campus.id
        db.session.commit()
        print("Users synchronized with default tenant.")

    print("Database sync complete! 🚀")
