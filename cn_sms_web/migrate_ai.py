from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Migrating database...")
        # Check if column exists or just try to add it (SQLite ignores if exists usually, or errors).
        # Better to try/except.
        with db.engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE incident ADD COLUMN ai_labels TEXT"))
                print("Added ai_labels")
            except Exception as e:
                print(f"Skipped ai_labels: {e}")
            
            try:
                conn.execute(text("ALTER TABLE incident ADD COLUMN ai_severity VARCHAR(20)"))
                print("Added ai_severity")
            except Exception as e:
                print(f"Skipped ai_severity: {e}")
                
            try:
                conn.execute(text("ALTER TABLE incident ADD COLUMN ai_recommendation TEXT"))
                print("Added ai_recommendation")
            except Exception as e:
                print(f"Skipped ai_recommendation: {e}")
                
            try:
                conn.execute(text("ALTER TABLE incident ADD COLUMN ai_analyzed_at DATETIME"))
                print("Added ai_analyzed_at")
            except Exception as e:
                print(f"Skipped ai_analyzed_at: {e}")
                
            conn.commit() # Important for sqlite in some drivers

if __name__ == '__main__':
    migrate()
