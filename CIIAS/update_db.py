from app import create_app, db
from app.models import (
    Course, Shuttle, Book, MapNode, User, 
    Organization, Campus, Department, Program, StaffDetail,
    CafeteriaItem, CafeteriaOrder
)
from datetime import datetime
from sqlalchemy import text

app = create_app(init_blueprints=False)

with app.app_context():
    print("Checking database schema for Nexus 2.0...")
    
    # 0. MIGRATE EXISTING TABLES MANUALLY
    try:
        with db.engine.connect() as conn:
            # Fix User Columns
            user_columns = [
                ("totp_secret", "VARCHAR(32)"),
                ("is_2fa_enabled", "BOOLEAN DEFAULT 0"),
                ("twofactor_method", "VARCHAR(20) DEFAULT 'email'"),
                ("otp_code", "VARCHAR(6)"),
                ("otp_expiry", "DATETIME"),
                ("backup_codes", "TEXT"),
                ("campus_id", "INTEGER"),
                ("dept_id", "INTEGER")
            ]
            
            for col_name, col_type in user_columns:
                try:
                    conn.execute(text(f"SELECT {col_name} FROM users LIMIT 1"))
                except Exception:
                    print(f"Column '{col_name}' missing in users. Adding it...")
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
            
            # Fix Course Columns
            try:
                conn.execute(text("SELECT credit_hours FROM courses LIMIT 1"))
            except Exception:
                print("Column 'credit_hours' missing in courses. Adding it...")
                conn.execute(text("ALTER TABLE courses ADD COLUMN credit_hours INTEGER DEFAULT 3"))

            # Fix Shuttle Columns
            shuttle_columns = [
                ("driver_id", "INTEGER"),
                ("capacity", "INTEGER"),
                ("model", "VARCHAR(50)"),
                ("campus_id", "INTEGER")
            ]
            for col_name, col_type in shuttle_columns:
                try:
                    conn.execute(text(f"SELECT {col_name} FROM shuttles LIMIT 1"))
                except Exception:
                    print(f"Column '{col_name}' missing in shuttles. Adding it...")
                    conn.execute(text(f"ALTER TABLE shuttles ADD COLUMN {col_name} {col_type}"))

            # Fix MapNodes
            try:
                conn.execute(text("SELECT altitude FROM map_nodes LIMIT 1"))
            except Exception:
                conn.execute(text("ALTER TABLE map_nodes ADD COLUMN altitude FLOAT DEFAULT 0.0"))
            
            # Fix Cafeteria Columns
            try:
                conn.execute(text("SELECT campus_id FROM cafeteria_items LIMIT 1"))
            except Exception:
                print("Columns missing in cafeteria_items. Adding them...")
                conn.execute(text("ALTER TABLE cafeteria_items ADD COLUMN campus_id INTEGER"))
                conn.execute(text("ALTER TABLE cafeteria_items ADD COLUMN cafeteria_name VARCHAR(100) DEFAULT 'Main Cafe'"))

            # Add Indexes
            print("Optimizing indexes for scale...")
            try:
                conn.execute(text("CREATE INDEX idx_incidents_ai_severity ON incidents(ai_severity)"))
            except Exception: pass
            
            try:
                conn.execute(text("CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp)"))
            except Exception: pass
            
            conn.commit()
    except Exception as e:
        print(f"Schema check error: {e}")

    print("Creating new tables...")
    db.create_all()
    print("Tables created.")
    
    # --- SEED DATA ---
    print("Seeding Industrial Hierarchy...")
    
    # 1. Organization
    org = Organization.query.filter_by(code="CGU").first()
    if not org:
        org = Organization(name="CIIAS Global University", code="CGU", website="https://ciias.edu")
        db.session.add(org)
        db.session.commit()
        print("Organization created.")

    # 2. Campus
    campus = Campus.query.filter_by(name="Islamabad Main Campus").first()
    if not campus:
        campus = Campus(org_id=org.id, name="Islamabad Main Campus", location="Sector H-12, Islamabad")
        db.session.add(campus)
        db.session.commit()
        print("Main Campus created.")

    # 3. 40 Departments
    if Department.query.count() < 10:
        depts = [
            ("Computer Science", "CS"), ("Software Engineering", "SE"), ("Artificial Intelligence", "AI"),
            ("Cyber Security", "CYS"), ("Data Science", "DS"), ("Electrical Engineering", "EE"),
            ("Mechanical Engineering", "ME"), ("Civil Engineering", "CE"), ("Business Administration", "BBA"),
            ("Accounting & Finance", "AF"), ("Social Sciences", "SS"), ("Physics", "PHY"),
            ("Mathematics", "MATH"), ("Chemistry", "CHEM"), ("Biosciences", "BIO"), ("Psychology", "PSY"),
            ("Economics", "ECO"), ("Law", "LAW"), ("Architecture", "ARCH"), ("Design", "DSGN"),
            ("Media Studies", "MS"), ("English", "ENG"), ("Urdu", "URD"), ("Islamic Studies", "IS"),
            ("HR", "HR", "administrative"), ("Finance", "FIN", "administrative"), ("IT Support", "IT", "support"),
            ("Library", "LIB", "support"), ("Transport", "TRA", "support"), ("Security", "SEC", "support"),
            ("Admissions", "ADM", "administrative"), ("Exam Cell", "EXAM", "administrative"),
            ("Student Affairs", "SA", "administrative"), ("Procurement", "PRO", "administrative"),
            ("Medical Center", "MED", "support"), ("Hostel Management", "HOS", "support"),
            ("Sports Dept", "SPD", "support"), ("Industrial Liason", "IL", "administrative"),
            ("Research & Dev", "RD", "administrative"), ("Quality Assurance", "QA", "administrative")
        ]
        
        for d in depts:
            name, code = d[0], d[1]
            dtype = d[2] if len(d) > 2 else 'academic'
            new_dept = Department(campus_id=campus.id, name=name, code=code, type=dtype)
            db.session.add(new_dept)
        
        db.session.commit()
        print(f"Seeded {len(depts)} departments.")

    # 4. COURSES & SHUTTLES (Existing seeding)
    if not Course.query.first():
        c1 = Course(code="CS-101", name="Intro to Computer Science", schedule="Mon,Wed 09:00-10:30")
        db.session.add(c1)
    
    if not Shuttle.query.first():
        s1 = Shuttle(plate_number="BUS-ALPHA", route_name="Campus Loop", status="Active", 
                     capacity=30, model="Toyota Coaster", current_lat=33.645, current_lng=72.990)
        db.session.add(s1)

    db.session.commit()
    print("Database update complete! 🚀")
