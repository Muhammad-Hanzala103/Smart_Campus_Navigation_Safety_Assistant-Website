from flask import Blueprint, request, jsonify
from app import db
from app.models import FeeChallan, University
from app.utils import token_required

financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/challans', methods=['GET'])
@token_required
def get_challans(current_user):
    """Get all fee challans for the current user and their university"""
    challans = FeeChallan.query.filter_by(
        user_id=current_user.id,
        university_id=current_user.university_id
    ).order_by(FeeChallan.due_date.desc()).all()
    return jsonify([c.to_dict() for c in challans]), 200

@financial_bp.route('/challans/<int:id>/pay', methods=['POST'])
@token_required
def pay_challan(current_user, id):
    """Mock payment for a challan"""
    challan = FeeChallan.query.filter_by(id=id, user_id=current_user.id).first()
    
    if not challan:
        return jsonify({'error': 'Challan not found'}), 404
        
    if challan.status == 'paid':
        return jsonify({'message': 'Challan already paid'}), 200
        
    # Mock payment processing
    challan.status = 'paid'
    db.session.commit()
    
    return jsonify({'message': 'Payment successful', 'challan': challan.to_dict()}), 200
