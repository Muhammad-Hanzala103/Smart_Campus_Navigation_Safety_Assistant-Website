import csv
import io
from app import db
from app.models import User, University
from app.encryption import encryption_manager

class DataImporter:
    @staticmethod
    def import_users_from_csv(file_stream, university_id):
        """
        Parses CSV and creates users.
        Expected CSV headers: name, email, password, role, phone, department_code (optional)
        """
        stream = io.StringIO(file_stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        success_count = 0
        errors = []
        
        uni = University.query.get(university_id)
        if not uni:
            return {'success': False, 'message': 'University not found'}

        for row_num, row in enumerate(csv_input, start=2):
            try:
                email = row.get('email')
                password = row.get('password')
                name = row.get('name')
                
                if not email or not password or not name:
                    errors.append(f"Row {row_num}: Missing required fields")
                    continue
                    
                # Check if user exists
                if User.query.filter_by(email=email).first():
                    errors.append(f"Row {row_num}: Email {email} already exists")
                    continue
                
                new_user = User(
                    university_id=university_id,
                    name=name,
                    email=email,
                    role=row.get('role', 'student'),
                    phone=row.get('phone')
                )
                new_user.set_password(password)
                
                db.session.add(new_user)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'Database error: {str(e)}'}
            
        return {
            'success': True,
            'imported': success_count,
            'errors': errors
        }

    @staticmethod
    def import_courses_from_csv(file_stream, university_id):
        # Placeholder for course import logic
        return {'success': True, 'imported': 0, 'errors': []}

importer = DataImporter()
