from flask import Blueprint, make_response, request, jsonify
from app.utils import token_required
from app.services.report_generator import report_generator

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/attendance/download', methods=['GET'])
@token_required
def download_attendance(current_user):
    """Download attendance report as CSV"""
    # Assuming user can download their own report
    # If admin, query param user_id might be needed
    target_user_id = current_user.id
    if current_user.role in ['admin', 'staff']:
        target_user_id = request.args.get('user_id', current_user.id)
    
    csv_output = report_generator.generate_attendance_report(target_user_id)
    
    response = make_response(csv_output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=attendance_report.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

@reports_bp.route('/grades/download', methods=['GET'])
@token_required
def download_grades(current_user):
    """Download grades report as CSV"""
    target_user_id = current_user.id
    if current_user.role in ['admin', 'staff']:
        target_user_id = request.args.get('user_id', current_user.id)
        
    csv_output = report_generator.generate_grades_report(target_user_id)
    
    response = make_response(csv_output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=grades_report.csv"
    response.headers["Content-Type"] = "text/csv"
    return response
