from flask import Blueprint, request, jsonify
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
        
    return jsonify([n.to_dict() for n in nodes]), 200

# ==================== AI CHATBOT ====================

@engagement_bp.route('/chat/ask', methods=['POST'])
def ask_chatbot():
    data = request.json
    query = data.get('query')
    
    # Mock AI response logic (would connect to Gemini/OpenAI here)
    response_text = "I am the Smart Campus AI. I can help you with schedules, locations, and safety."
    
    if "library" in query.lower():
        response_text = "The library is open from 8 AM to 8 PM. It is located in Block B."
    elif "cafe" in query.lower():
        response_text = "The cafeteria serves lunch from 12 PM to 2 PM."
        
    return jsonify({
        'response': response_text,
        'timestamp': '2025-01-09T10:00:00Z',
        'suggestions': ['Show map', 'Bus timings']
    }), 200
