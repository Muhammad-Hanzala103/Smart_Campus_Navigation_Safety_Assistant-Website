import csv
import io
from app.models import Attendance, Course, Enrollment, User
from sqlalchemy.orm import joinedload

class ReportGenerator:
    @staticmethod
    def generate_attendance_report(user_id):
        """
        Generate a CSV report of attendance for a student.
        """
        # Optimized query with eager loading for 'course' relationship
        records = Attendance.query.filter_by(student_id=user_id).options(joinedload(Attendance.course)).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Date', 'Course Code', 'Course Name', 'Status'])
        
        # Data
        for r in records:
            writer.writerow([
                r.date.strftime('%Y-%m-%d'),
                r.course.code,
                r.course.name,
                r.status
            ])
            
        output.seek(0)
        return output

    @staticmethod
    def generate_grades_report(user_id):
        """
        Generate a CSV report of grades/results.
        """
        # Optimized query with eager loading for 'course' relationship
        enrollments = Enrollment.query.filter_by(user_id=user_id).options(joinedload(Enrollment.course)).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Semester', 'Course Code', 'Course Name', 'Credits', 'Grade'])
        
        # Data
        for e in enrollments:
            writer.writerow([
                e.semester,
                e.course.code,
                e.course.name,
                e.course.credit_hours,
                e.grade
            ])
            
        output.seek(0)
        return output

report_generator = ReportGenerator()
