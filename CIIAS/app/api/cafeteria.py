from flask import Blueprint, request, jsonify
from app import db
from app.models import CafeteriaItem, CafeteriaOrder, User, University
from app.utils import token_required, ROLE_CAFETERIA, ROLE_ADMIN, tenant_required
from datetime import datetime

cafeteria_bp = Blueprint('cafeteria', __name__)

@cafeteria_bp.route('/menu', methods=['GET'])
@tenant_required
def get_menu(uni):
    """Get all available cafeteria items for a specific university"""
    campus_id = request.args.get('campus_id')
    category = request.args.get('category')
    
    query = CafeteriaItem.query.filter_by(university_id=uni.id, is_available=True)
    
    if campus_id:
        query = query.filter_by(campus_id=campus_id)
    if category:
        query = query.filter_by(category=category)
        
    items = query.all()
    return jsonify([item.to_dict() for item in items]), 200

@cafeteria_bp.route('/item/update', methods=['POST'])
@token_required
def update_item(current_user):
    """Update item prices or availability (For Cafeteria Managers)"""
    if current_user.role not in [ROLE_CAFETERIA, ROLE_ADMIN]:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    item_id = data.get('id')
    item = CafeteriaItem.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
        
    if 'price' in data: item.price = data['price']
    if 'is_available' in data: item.is_available = data['is_available']
    if 'name' in data: item.name = data['name']
    
    db.session.commit()
    return jsonify({
        'message': 'Menu updated successfully',
        'item': item.to_dict()
    }), 200

@cafeteria_bp.route('/order', methods=['POST'])
@token_required
def place_order(current_user):
    """Place a new cafeteria order"""
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({'error': 'No items in order'}), 400
        
    total_price = 0
    final_items = []
    
    for item_order in items:
        item = CafeteriaItem.query.get(item_order['id'])
        if item and item.is_available:
            price = item.price * item_order['quantity']
            total_price += price
            final_items.append({
                'id': item.id,
                'name': item.name,
                'quantity': item_order['quantity'],
                'price': item.price,
                'subtotal': price
            })
            
    if not final_items:
        return jsonify({'error': 'No valid items found'}), 400
        
    order = CafeteriaOrder(
        university_id=current_user.university_id,
        user_id=current_user.id,
        items=final_items,
        total_price=total_price,
        status='pending'
    )
    
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'message': 'Order placed successfully',
        'order': order.to_dict()
    }), 201
