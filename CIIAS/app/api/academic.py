from flask import Blueprint, request, jsonify
from app import db
from app.models import (
    Course, Attendance, Grade, User, Enrollment, 
    ExamSeat, Assignment, AssignmentSubmission, TeacherFeedback, DateSheet,
    GradingPolicy
)
from app.utils import tenant_required
from app.services.cache import cache, make_cache_key
from datetime import datetime



academic_bp = Blueprint('academic', __name__)

# ==================== COURSES ====================

@academic_bp.route('/courses', methods=['GET'])
@tenant_required
@cache.cached(timeout=300, key_prefix=make_cache_key)
def get_courses(uni):
    courses = Course.query.filter_by(university_id=uni.id).all()
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
@cache.cached(timeout=60, key_prefix=make_cache_key)
def get_results():
    user_id = request.args.get('user_id', 1)
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    
    results = []
    total_weighted_points = 0.0
    total_credits = 0.0
    
    # Industrial Standard Grade Point Mapping
    grade_points = {
        'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 
        'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0
    }
    
    for enroll in enrollments:
        gp = grade_points.get(enroll.grade, 0.0)
        credits = enroll.course.credit_hours or 3
        
        results.append({
            "course_code": enroll.course.code,
            "course_name": enroll.course.name,
            "grade": enroll.grade,
            "credits": credits,
            "semester": enroll.semester
        })
        
        if enroll.grade != 'In Progress':
            total_weighted_points += (gp * credits)
            total_credits += credits
            
    cgpa = round(total_weighted_points / total_credits, 2) if total_credits > 0 else 0.0
    
    return jsonify({
        "cgpa": cgpa,
        "total_credits_earned": total_credits,
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

# ==================== LMS: ASSIGNMENTS ====================

@academic_bp.route('/assignments', methods=['GET'])
def get_assignments():
    course_id = request.args.get('course_id')
    if course_id:
        assignments = Assignment.query.filter_by(course_id=course_id).all()
    else:
        # Get assignments for all courses the user is enrolled in
        user_id = request.args.get('user_id', 1)
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        course_ids = [e.course_id for e in enrollments]
        assignments = Assignment.query.filter(Assignment.course_id.in_(course_ids)).all()
        
    return jsonify([a.to_dict() for a in assignments]), 200

@academic_bp.route('/assignments/submit', methods=['POST'])
def submit_assignment():
    data = request.json
    submission = AssignmentSubmission(
        assignment_id=data.get('assignment_id'),
        student_id=data.get('student_id'),
        file_url=data.get('file_url')
    )
    db.session.add(submission)
    db.session.commit()
    return jsonify({'message': 'Assignment submitted successfully'}), 201

# ==================== LMS: FEEDBACK ====================

@academic_bp.route('/feedback/submit', methods=['POST'])
def submit_feedback():
    data = request.json
    feedback = TeacherFeedback(
        teacher_id=data.get('teacher_id'),
        student_id=data.get('student_id'),
        course_id=data.get('course_id'),
        rating=data.get('rating'),
        comments=data.get('comments'),
        semester=data.get('semester', 'Fall 2023')
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify({'message': 'Feedback submitted successfully'}), 201

# ==================== LMS: DATESHEETS ====================

@academic_bp.route('/datesheet', methods=['GET'])
def get_datesheet():
    campus_id = request.args.get('campus_id')
    if not campus_id:
        campus_id = 1
    
    datesheets = DateSheet.query.filter_by(campus_id=campus_id).order_by(DateSheet.created_at.desc()).all()
    return jsonify([
        {
            'id': d.id,
            'exam_type': d.exam_type,
            'semester': d.semester,
        } for d in datesheets
    ]), 200

# ==================== GRADING POLICIES (SaaS) ====================

@academic_bp.route('/grading-policies', methods=['GET'])
@tenant_required
def get_grading_policies(uni):
    policies = GradingPolicy.query.filter_by(university_id=uni.id).all()
    return jsonify([p.to_dict() for p in policies]), 200

@academic_bp.route('/grading-policies', methods=['POST'])
@tenant_required
def create_grading_policy(uni):
    data = request.json
    policy = GradingPolicy(
        university_id=uni.id,
        name=data.get('name'),
        config=data.get('config'), # JSON string
        is_active=True
    )
    db.session.add(policy)
    db.session.commit()
    return jsonify(policy.to_dict()), 201
