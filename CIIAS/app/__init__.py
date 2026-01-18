import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config

from flask_socketio import SocketIO
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
socketio = SocketIO()
compress = Compress()
limiter = Limiter(key_func=get_remote_address)
oauth = OAuth()

def create_app(config_name='default'):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])
    
    # Enable CORS for all routes (required for Android app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    compress.init_app(app)
    limiter.init_app(app)
    oauth.init_app(app)

    # Register Google OAuth
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    # Register Socket Events
    with app.app_context():
        from app import socket_events
    
    # Register API Blueprints
    from app.api.auth import auth_bp
    from app.api.profile import profile_bp
    from app.api.map import map_bp
    from app.api.bookings import booking_bp
    from app.api.incidents import incident_bp
    from app.api.emergency import emergency_bp
    from app.api.notifications import notifications_bp
    from app.api.rooms import rooms_bp
    from app.api.analytics import analytics_bp
    from app.api.analytics import analytics_bp
    # New Blueprints
    from app.api.academic import academic_bp
    from app.api.transport import transport_bp
    from app.api.library import library_bp
    from app.api.engagement import engagement_bp
    from app.api.cafeteria import cafeteria_bp
    from app.api.chat import chat_bp
    from app.api.financial import financial_bp
    from app.web.routes import web_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(map_bp, url_prefix='/api/map')
    app.register_blueprint(booking_bp, url_prefix='/api/bookings')
    app.register_blueprint(incident_bp, url_prefix='/api/incidents')
    app.register_blueprint(emergency_bp, url_prefix='/api/emergency')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Register New Blueprints
    app.register_blueprint(academic_bp, url_prefix='/api/academic')
    app.register_blueprint(transport_bp, url_prefix='/api/transport')
    app.register_blueprint(library_bp, url_prefix='/api/library')
    app.register_blueprint(engagement_bp, url_prefix='/api/engagement')
    app.register_blueprint(cafeteria_bp, url_prefix='/api/cafeteria')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(financial_bp, url_prefix='/api/financial')
    
    app.register_blueprint(web_bp)
    
    # Industrial Security Headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    return app
