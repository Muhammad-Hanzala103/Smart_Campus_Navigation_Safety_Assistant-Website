from flask import Blueprint, request, jsonify
from app import db
from app.models import Course, Attendance, Grade, User
from datetime import datetime

academic_bp = Blueprint('academic', __name__)

# ==================== COURSES ====================

@academic_bp.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([c.to_dict() for c in courses]), 200

@academic_bp.route('/my_courses', methods=['GET'])
def get_my_courses():
    # In a real app, get user_id from JWT token e.g. g.user_id
    # For now, we accept a query param ?user_id=1
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if user.role == 'student':
        # Find courses where student has attendance records (mock logic for enrollment)
        # In a real DB, we'd have a Enrollments table. 
        # For this demo, we assume all students see all courses or specific logic
        courses = Course.query.all() 
    elif user.role in ['staff', 'admin', 'faculty']:
        courses = Course.query.filter_by(instructor_id=user_id).all()
    else:
        courses = []
        
    return jsonify([c.to_dict() for c in courses]), 200

# ==================== ATTENDANCE ====================

@academic_bp.route('/attendance/mark', methods=['POST'])
def mark_attendance():
    data = request.json
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    status = data.get('status', 'Present')
    date_str = data.get('date') # YYYY-MM-DD
    
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = datetime.today().date()
        
    record = Attendance(
        student_id=student_id, 
        course_id=course_id, 
        date=date, 
        status=status
    )
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'message': 'Attendance marked successfully'}), 201

@academic_bp.route('/attendance/<int:course_id>', methods=['GET'])
def get_course_attendance(course_id):
    records = Attendance.query.filter_by(course_id=course_id).all()
    # Group by date? Or just return raw
    return jsonify([{
        'student_id': r.student_id,
        'student_name': r.student.name,
        'date': r.date.isoformat(),
        'status': r.status
    } for r in records]), 200

# ==================== GRADES ====================

@academic_bp.route('/grades/upload', methods=['POST'])
def upload_grade():
    data = request.json
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    exam_type = data.get('exam_type')
    score = data.get('score')
    total = data.get('total')
    
    grade = Grade(
        student_id=student_id,
        course_id=course_id,
        exam_type=exam_type,
        score=score,
        total_marks=total
    )
    db.session.add(grade)
    db.session.commit()
    return jsonify({'message': 'Grade uploaded'}), 201
