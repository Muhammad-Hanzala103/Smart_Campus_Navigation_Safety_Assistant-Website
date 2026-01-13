from flask import Blueprint, request, jsonify
from app import db
from app.models import Course, Attendance, Grade, User, Enrollment, ExamSeat
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
        # Default to user 1 for demo if not provided
        user_id = 1
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    if user.role == 'student':
        # Use Enrollments table
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        courses = [e.course for e in enrollments]
    elif user.role in ['staff', 'admin', 'faculty']:
        courses = Course.query.filter_by(instructor_id=user_id).all()
    else:
        courses = []
        
    return jsonify([c.to_dict() for c in courses]), 200

# ==================== RESULTS (ANDROID) ====================

@academic_bp.route('/results', methods=['GET'])
def get_results():
    # Helper to calculate GPA
    def calculate_gpa(marks):
        if marks >= 85: return 4.0
        if marks >= 80: return 3.7
        if marks >= 75: return 3.3
        if marks >= 70: return 3.0
        if marks >= 65: return 2.7
        if marks >= 60: return 2.3
        return 0.0

    # Mock user for demo if not logged in
    user_id = 1 # Force user 1 for demo or get from session
    
    # In real app, query Enrollments/Grades
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    
    results = []
    total_gpa = 0
    count = 0
    
    for enroll in enrollments:
        # Mock grade calculation logic based on letter grade
        grade_point = 0.0
        if enroll.grade == 'A': grade_point = 4.0
        elif enroll.grade == 'A-': grade_point = 3.7
        elif enroll.grade == 'B+': grade_point = 3.3
        elif enroll.grade == 'B': grade_point = 3.0
        elif enroll.grade == 'B-': grade_point = 2.7
        
        results.append({
            "course_code": enroll.course.code,
            "course_name": enroll.course.name,
            "grade": enroll.grade, # 'A', 'B', 'In Progress'
            "semester": enroll.semester
        })
        
        if enroll.grade != 'In Progress':
            total_gpa += grade_point
            count += 1
            
    cgpa = round(total_gpa / count, 2) if count > 0 else 3.5 # Default mock
    
    return jsonify({
        "cgpa": cgpa,
        "semester": "Fall 2023",
        "results": results
    })

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

@academic_bp.route('/attendance', methods=['GET'])
def get_my_attendance():
    """Get attendance for the logged in user (Android)"""
    user_id = 1 # Demo
    records = Attendance.query.filter_by(student_id=user_id).all()
    
    # Calculate stats per course
    course_stats = {}
    for r in records:
        if r.course.code not in course_stats:
            course_stats[r.course.code] = {'total': 0, 'present': 0, 'name': r.course.name}
        course_stats[r.course.code]['total'] += 1
        if r.status == 'Present':
            course_stats[r.course.code]['present'] += 1
            
    response_data = []
    total_percent_sum = 0
    
    for code, stats in course_stats.items():
        percentage = (stats['present'] / stats['total']) * 100 if stats['total'] > 0 else 0
        total_percent_sum += percentage
        response_data.append({
            "course_code": code,
            "course_name": stats['name'],
            "percentage": round(percentage, 1),
            "total_classes": stats['total'],
            "attended": stats['present']
        })
    
    avg_percent = round(total_percent_sum / len(course_stats), 1) if course_stats else 0.0
        
    return jsonify({
        "overall_percentage": avg_percent, 
        "details": response_data
    })

# ==================== EXAM SEATS ====================

@academic_bp.route('/seat', methods=['GET'])
def get_exam_seats():
    user_id = 1 # Demo
    seats = ExamSeat.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        "course_name": s.course.name,
        "room": s.room,
        "row": "R-1", # Mock
        "seat": s.seat_number,
        "time": s.exam_time.strftime("%I:%M %p"),
        "date": s.exam_time.strftime("%d %b, %Y")
    } for s in seats])

# ==================== GRADES (Admin Upload) ====================

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
