from flask import Blueprint, request, jsonify
import datetime
from app import db
from app.models import Wallet, MapNode, User

engagement_bp = Blueprint('engagement', __name__)

# ==================== GAMIFICATION ====================

@engagement_bp.route('/wallet/balance/<int:user_id>', methods=['GET'])
def get_balance(user_id):
    wallet = Wallet.query.get(user_id)
    if not wallet:
        return jsonify({'balance': 0}), 200
    return jsonify({'balance': wallet.balance}), 200

@engagement_bp.route('/wallet/transaction', methods=['POST'])
def add_transaction():
    # Mock transaction
    return jsonify({'message': 'Transaction successful', 'new_balance': 500}), 200

# ==================== AR NAVIGATION ====================

@engagement_bp.route('/ar/nodes', methods=['GET'])
def get_ar_nodes():
    user_lat = float(request.args.get('lat', 0))
    user_lng = float(request.args.get('lng', 0))
    
    # Return nodes within x meters. For now, return all relevant nodes
    nodes = MapNode.query.filter(MapNode.altitude.isnot(None)).all()
    # Or just all nodes if we didn't migrate old ones
    if not nodes:
        nodes = MapNode.query.all()
        
    return jsonify([{
        'id': n.id,
        'lat': n.lat,
        'lng': n.lng,
        'altitude': getattr(n, 'altitude', 0.0),
        'type': getattr(n, 'type', 'waypoint'),
        'name': getattr(n, 'name', f'Node {n.id}')
    } for n in nodes]), 200

# ==================== AI CHATBOT ====================
from app.ai_chat import chatbot

@engagement_bp.route('/chat/ask', methods=['POST'])
def ask_chatbot():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'response': "Please ask a question."}), 400
        
    result = chatbot.get_response(query)
    
    return jsonify({
        'response': result['reply'],
        'source': result['source'],
        'confidence': result['confidence'],
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'suggestions': ['Bus Timings', 'Exam Dates', 'Library Hours']
    }), 200
