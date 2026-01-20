import math
import heapq
from flask import Blueprint, request, jsonify
from app import db
from app.models import MapNode, MapEdge, MapPOI, Campus
from app.utils import token_required, has_permission, ROLE_ADMIN, ROLE_SECURITY
from flask import session

map_bp = Blueprint('map', __name__)


@map_bp.route('', methods=['GET'])
def get_map():
    """Get map data with nodes and image URL"""
    nodes = MapNode.query.all()
    edges = MapEdge.query.all()
    
    return jsonify({
        'map_image_url': '/static/img/campus_map.png',
        'nodes': [n.to_dict() for n in nodes],
        'edges': [e.to_dict() for e in edges]
    }), 200


@map_bp.route('/nodes', methods=['GET'])
def get_nodes():
    """Get all map nodes"""
    nodes = MapNode.query.all()
    return jsonify([n.to_dict() for n in nodes]), 200


@map_bp.route('/nodes/<int:id>', methods=['GET'])
def get_node_detail(id):
    """Get single node details"""
    node = MapNode.query.get_or_404(id)
    return jsonify(node.to_dict()), 200


@map_bp.route('/search', methods=['GET'])
def search_nodes():
    """Search nodes by name"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([]), 200
    
    nodes = MapNode.query.filter(
        MapNode.name.ilike(f'%{query}%')
    ).all()
    
    return jsonify([n.to_dict() for n in nodes]), 200


@map_bp.route('/nearby', methods=['GET'])
def get_nearby_nodes():
    """Get nodes near a location"""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    node_type = request.args.get('type')
    radius = request.args.get('radius', default=500, type=float)  # meters
    
    if lat is None or lng is None:
        return jsonify({'message': 'lat and lng are required'}), 400
    
    query = MapNode.query
    
    if node_type:
        query = query.filter_by(node_type=node_type)
    
    nodes = query.all()
    
    # Calculate distances and filter
    nearby = []
    for node in nodes:
        if node.latitude and node.longitude:
            distance = _calculate_distance(lat, lng, node.latitude, node.longitude)
            if distance <= radius:
                node_dict = node.to_dict()
                node_dict['distance'] = round(distance, 2)
                nearby.append(node_dict)
    
    # Sort by distance
    nearby.sort(key=lambda x: x['distance'])
    
    return jsonify(nearby), 200


def _calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters (Haversine formula)"""
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


@map_bp.route('/route', methods=['GET'])
def get_route():
    """Get route between two nodes using A* algorithm"""
    from_id = request.args.get('from', type=int)
    to_id = request.args.get('to', type=int)
    
    if not from_id or not to_id:
        return jsonify({'message': 'from and to node IDs are required'}), 400
    
    from_node = MapNode.query.get(from_id)
    to_node = MapNode.query.get(to_id)
    
    if not from_node or not to_node:
        return jsonify({'message': 'Invalid node IDs'}), 404
    
    # Run A* pathfinding
    path, distance = _find_path(from_id, to_id)
    
    if not path:
        return jsonify({'message': 'No route found'}), 404
    
    # Convert node IDs to coordinates
    path_coords = []
    for node_id in path:
        node = MapNode.query.get(node_id)
        if node and node.latitude and node.longitude:
            path_coords.append({
                'lat': node.latitude,
                'lng': node.longitude,
                'node_id': node.id,
                'name': node.name
            })
    
    # Estimate walking time (~5 km/h = ~83 m/min)
    estimated_minutes = max(1, int(distance / 83))
    
    return jsonify({
        'path': path_coords,
        'distance': round(distance, 2),
        'estimated_time': f'{estimated_minutes} min'
    }), 200


def _find_path(start_id, end_id):
    """A* pathfinding algorithm"""
    # Get all nodes and edges
    nodes = {n.id: n for n in MapNode.query.all()}
    edges = MapEdge.query.all()
    
    if start_id not in nodes or end_id not in nodes:
        return None, 0
    
    # Build adjacency list
    graph = {}
    for node_id in nodes:
        graph[node_id] = []
    
    for edge in edges:
        # Bidirectional edges
        graph[edge.from_node_id].append((edge.to_node_id, edge.weight))
        graph[edge.to_node_id].append((edge.from_node_id, edge.weight))
    
    # Heuristic function (Euclidean distance)
    def heuristic(node_id):
        node = nodes[node_id]
        target = nodes[end_id]
        if node.latitude and node.longitude and target.latitude and target.longitude:
            return _calculate_distance(node.latitude, node.longitude, target.latitude, target.longitude)
        # Fall back to x, y if available
        if node.x is not None and node.y is not None and target.x is not None and target.y is not None:
            return math.sqrt((node.x - target.x)**2 + (node.y - target.y)**2)
        return 0
    
    # A* algorithm
    open_set = [(0, start_id)]
    came_from = {}
    g_score = {start_id: 0}
    f_score = {start_id: heuristic(start_id)}
    
    while open_set:
        current_f, current = heapq.heappop(open_set)
        
        if current == end_id:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path, g_score[end_id]
        
        for neighbor, weight in graph.get(current, []):
            tentative_g = g_score.get(current, float('inf')) + weight
            
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return None, 0


# Admin routes for node management
@map_bp.route('/nodes', methods=['POST'])
def create_node():
    """Create a new map node"""
    data = request.get_json()
    
    node = MapNode(
        name=data.get('name'),
        node_type=data.get('node_type'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        x=data.get('x'),
        y=data.get('y'),
        building=data.get('building'),
        floor=data.get('floor'),
        description=data.get('description'),
        is_accessible=data.get('is_accessible', True),
        is_emergency_exit=data.get('is_emergency_exit', False)
    )
    
    db.session.add(node)
    db.session.commit()
    
    return jsonify(node.to_dict()), 201


@map_bp.route('/nodes/<int:id>', methods=['PUT'])
def update_node(id):
    """Update a map node"""
    node = MapNode.query.get_or_404(id)
    data = request.get_json()
    
    for field in ['name', 'node_type', 'latitude', 'longitude', 'x', 'y', 
                  'building', 'floor', 'description', 'is_accessible', 'is_emergency_exit']:
        if field in data:
            setattr(node, field, data[field])
    
    db.session.commit()
    return jsonify(node.to_dict()), 200


@map_bp.route('/nodes/<int:id>', methods=['DELETE'])
def delete_node(id):
    """Delete a map node"""
    node = MapNode.query.get_or_404(id)
    db.session.delete(node)
    db.session.commit()
    return jsonify({'message': 'Node deleted'}), 200

# ==================== GEO-NEXUS 2.0: POI & CAMPUS MGMT ====================

@map_bp.route('/pois', methods=['GET'])
def get_pois():
    """Retrieve all POIs for the user's campus"""
    campus_id = request.args.get('campus_id', type=int)
    if not campus_id and 'user_id' in session:
        # Get from session if not provided (Web usage)
        from app.models import User
        user = User.query.get(session['user_id'])
        campus_id = user.campus_id if user else None
    
    if not campus_id:
        return jsonify({'message': 'campus_id required'}), 400
        
    pois = MapPOI.query.filter_by(campus_id=campus_id).all()
    return jsonify([p.to_dict() for p in pois]), 200

@map_bp.route('/pois', methods=['POST'])
def save_poi():
    """Allows Admins and Security to mark new POIs"""
    # In a real scenario, use @token_required or @login_required
    # For this transition, we'll check session or token
    data = request.get_json()
    
    campus_id = data.get('campus_id')
    if not campus_id:
        return jsonify({'message': 'campus_id required'}), 400
        
    poi = MapPOI(
        campus_id=campus_id,
        name=data.get('name'),
        type=data.get('type', 'room'),
        lat=data.get('lat'),
        lng=data.get('lng'),
        description=data.get('description'),
        is_public=data.get('is_public', True)
    )
    
    db.session.add(poi)
    db.session.commit()
    return jsonify(poi.to_dict()), 201

@map_bp.route('/campus/center', methods=['POST'])
def update_campus_center():
    """Allows Admins to set the default map view for their campus"""
    data = request.get_json()
    campus_id = data.get('campus_id')
    lat = data.get('lat')
    lng = data.get('lng')
    
    if not all([campus_id, lat, lng]):
        return jsonify({'message': 'Missing data'}), 400
        
    campus = Campus.query.get(campus_id)
    if not campus:
        return jsonify({'message': 'Campus not found'}), 404
        
    campus.latitude = lat
    campus.longitude = lng
    db.session.commit()
    
    # Update session if applicable
    if session.get('campus_id') == campus_id:
        session['campus_lat'] = lat
        session['campus_lng'] = lng
        
    return jsonify({'message': 'Campus center updated', 'lat': lat, 'lng': lng}), 200
