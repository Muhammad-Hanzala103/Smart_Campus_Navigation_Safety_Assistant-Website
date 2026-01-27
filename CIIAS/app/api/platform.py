from flask import Blueprint, request, jsonify
from app import db
from app.models import University, UniversityConfig, User
from app.utils import token_required, tenant_required
from app.services.importer import importer
import secrets
import string
import uuid

platform_bp = Blueprint('platform', __name__)

def generate_api_key(length=32):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@platform_bp.route('/register', methods=['POST'])
def register_university():
    """Register a new university on the SaaS platform"""
    data = request.get_json()
    name = data.get('name')
    slug = data.get('slug')
    domain = data.get('domain')
    
    if not name or not slug:
        return jsonify({'error': 'Name and slug are required'}), 400
        
    if University.query.filter((University.slug == slug) | (University.domain == domain)).first():
        return jsonify({'error': 'University with this slug or domain already exists'}), 409
        
    api_key = generate_api_key()
    
    uni = University(
        name=name,
        slug=slug,
        domain=domain,
        api_key=api_key
    )
    
    db.session.add(uni)
    db.session.flush() # Get the ID
    
    config = UniversityConfig(
        university_id=uni.id,
        primary_color=data.get('primary_color', '#007BFF'),
        secondary_color=data.get('secondary_color', '#6C757D'),
        logo_url=data.get('logo_url'),
        map_lat=data.get('map_lat'),
        map_lng=data.get('map_lng')
    )
    
    db.session.add(config)
    db.session.commit()
    
    return jsonify({
        'message': 'University registered successfully',
        'university': uni.to_dict(),
        'api_key': api_key, # Return once
        'config': config.to_dict()
    }), 201

@platform_bp.route('/config/<slug>', methods=['GET'])
def get_university_config(slug):
    """Retrieve configuration for a specific university (SaaS Customization)"""
    uni = University.query.filter_by(slug=slug, is_active=True).first_or_404()
    return jsonify({
        'name': uni.name,
        'config': uni.config.to_dict()
    }), 200


@platform_bp.route('/import/users', methods=['POST'])
@tenant_required
def import_users(uni):
    """Bulk import users from CSV"""
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    if file:
        result = importer.import_users_from_csv(file, uni.id)
        status = 200 if result['success'] else 400
        return jsonify(result), status
