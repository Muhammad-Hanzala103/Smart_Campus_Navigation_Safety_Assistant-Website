from app import create_app, db
from app.models import Course, Shuttle, Book, MapNode, User
from datetime import datetime
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Checking database schema...")
    
    # 0. MIGRATE EXISTING TABLES MANUALLY (SQLite doesn't support easy ALTER ADD COLUMN if constrained, but simple fields work)
    try:
        # Check if column exists by trying to select it. If error, add it.
        with db.engine.connect() as conn:
            try:
                conn.execute(text("SELECT altitude FROM map_nodes LIMIT 1"))
            except Exception:
                print("Column 'altitude' missing in map_nodes. Adding it...")
                conn.execute(text("ALTER TABLE map_nodes ADD COLUMN altitude FLOAT DEFAULT 0.0"))
                conn.commit()
    except Exception as e:
        print(f"Schema check warning: {e}")

    print("Creating new tables...")
    db.create_all()
    print("Tables created.")
    
    # --- SEED DATA ---
    print("Seeding mock data...")
    
    # 1. COURSES
    if not Course.query.first():
        c1 = Course(code="CS-101", name="Intro to Computer Science", schedule="Mon,Wed 09:00-10:30")
        c2 = Course(code="SE-302", name="Software Architecture", schedule="Tue,Thu 11:00-12:30")
        c3 = Course(code="MATH-201", name="Linear Algebra", schedule="Fri 10:00-12:00")
        db.session.add_all([c1, c2, c3])
        print("Courses seeded.")

    # 2. SHUTTLE
    if not Shuttle.query.first():
        s1 = Shuttle(plate_number="BUS-ALPHA", route_name="Red Line (Campus Loop)", status="Active", current_lat=33.645, current_lng=72.990)
        s2 = Shuttle(plate_number="BUS-BETA", route_name="Blue Line (Hostel)", status="Active", current_lat=33.648, current_lng=72.992)
        db.session.add_all([s1, s2])
        print("Shuttles seeded.")

    # 3. BOOKS
    if not Book.query.first():
        b1 = Book(isbn="9780132350884", title="Clean Code", author="Robert C. Martin", category="Software", status="Available")
        b2 = Book(isbn="9780201633610", title="Design Patterns", author="Gamma et al.", category="Software", status="Issued")
        b3 = Book(isbn="9780134685991", title="Effective Java", author="Joshua Bloch", category="Programming", status="Available")
        db.session.add_all([b1, b2, b3])
        print("Books seeded.")
        
    # 4. MAP NODES AR
    if MapNode.query.filter(MapNode.altitude.isnot(None)).count() == 0:
        n1 = MapNode(name="Main Gate", node_type="gate", latitude=33.6515, longitude=73.1565, altitude=500.0, description="Main Entrance point")
        n2 = MapNode(name="Library Block", node_type="building", latitude=33.6520, longitude=73.1570, altitude=505.0)
        n3 = MapNode(name="Cafeteria", node_type="building", latitude=33.6525, longitude=73.1575, altitude=502.0)
        db.session.add_all([n1, n2, n3])
        print("AR Map Nodes seeded.")

    db.session.commit()
    print("Database update complete! 🚀")
