from flask import Blueprint, jsonify
from app import db
from app.services.cache import cache
import shutil

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Standard health check endpoint for uptime monitoring.
    ---
    tags:
      - System
    responses:
      200:
        description: System is healthy
      503:
        description: System is unhealthy
    """
    status = {
        'database': 'unknown',
        'cache': 'unknown',
        'disk_space': 'unknown'
    }
    
    # Check Database
    try:
        db.session.execute('SELECT 1')
        status['database'] = 'connected'
    except Exception as e:
        status['database'] = f'error: {str(e)}'
        
    # Check Cache
    try:
        cache.set('health_check', 'ok', timeout=10)
        if cache.get('health_check') == 'ok':
            status['cache'] = 'operational'
        else:
            status['cache'] = 'failed'
    except Exception:
        status['cache'] = 'error'
        
    # Check Disk Space
    total, used, free = shutil.disk_usage("/")
    status['disk_space'] = {
        'total_gb': total // (2**30),
        'free_gb': free // (2**30)
    }
    
    overall_status = 200
    if status['database'] != 'connected':
        overall_status = 503
        
    return jsonify(status), overall_status
