from flask import Blueprint, request, jsonify
from app import db
from app.models import CafeteriaItem, CafeteriaOrder
from app.utils import token_required
from datetime import datetime

cafeteria_bp = Blueprint('cafeteria', __name__)

@cafeteria_bp.route('/menu', methods=['GET'])
def get_menu():
    """Get all available cafeteria items"""
    category = request.args.get('category')
    query = CafeteriaItem.query.filter_by(is_available=True)
    
    if category:
        query = query.filter_by(category=category)
        
    items = query.all()
    return jsonify([item.to_dict() for item in items]), 200

@cafeteria_bp.route('/order', methods=['POST'])
@token_required
def place_order(current_user):
    """Place a new cafeteria order"""
    data = request.get_json()
    items = data.get('items', []) # List of {id, quantity}
    
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
