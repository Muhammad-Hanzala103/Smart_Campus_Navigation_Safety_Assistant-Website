from flask import Blueprint, request, jsonify
from app import db
from app.models import MapNode, MapEdge

map_bp = Blueprint('map', __name__)

@map_bp.route('/', methods=['GET'])
def get_map():
    nodes = MapNode.query.all()
    edges = MapEdge.query.all()
    
    return jsonify({
        'nodes': [n.to_dict() for n in nodes],
        'edges': [e.to_dict() for e in edges],
        'map_image_url': '/static/img/campus_map.png' # Placeholder
    })

@map_bp.route('/nodes', methods=['POST'])
def create_node():
    data = request.get_json()
    node = MapNode(
        name=data.get('name'),
        x=data.get('x'),
        y=data.get('y'),
        description=data.get('description'),
        node_type=data.get('node_type')
    )
    db.session.add(node)
    db.session.commit()
    return jsonify(node.to_dict()), 201

@map_bp.route('/nodes/<int:id>', methods=['PUT'])
def update_node(id):
    node = MapNode.query.get_or_404(id)
    data = request.get_json()
    
    node.name = data.get('name', node.name)
    node.x = data.get('x', node.x)
    node.y = data.get('y', node.y)
    node.description = data.get('description', node.description)
    node.node_type = data.get('node_type', node.node_type)
    
    db.session.commit()
    return jsonify(node.to_dict())

@map_bp.route('/nodes/<int:id>', methods=['DELETE'])
def delete_node(id):
    node = MapNode.query.get_or_404(id)
    # Cascade delete edges? For now just node.
    db.session.delete(node)
    db.session.commit()
    return jsonify({'message': 'Node deleted'})
