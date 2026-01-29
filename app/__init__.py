import os
from flask import Flask, render_template
from app.services.cache import cache
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config
from flasgger import Swagger

from flask_socketio import SocketIO
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
socketio = SocketIO()
compress = Compress()
limiter = Limiter(key_func=get_remote_address)
oauth = OAuth()
mail = Mail()
swagger = Swagger()
migrate = Migrate()

def create_app(config_name='default', init_blueprints=True):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])
    
    # Enable CORS for all routes (required for Android app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    # Vercel Serverless requires threading mode
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    compress.init_app(app)
    limiter.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)
    swagger.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)

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
    
    if init_blueprints:
        # Register Socket Events
        with app.app_context():
            from app import socket_events
        
        # Register Blueprints
        from app.api.auth import auth_bp
        from app.api.profile import profile_bp
        from app.api.map import map_bp
        from app.api.bookings import booking_bp
        from app.api.incidents import incident_bp
        from app.api.emergency import emergency_bp
        from app.api.reports import reports_bp
        from app.api.health import health_bp
        from app.api.notifications import notifications_bp
        from app.api.rooms import rooms_bp
        from app.api.analytics import analytics_bp
        from app.api.academic import academic_bp
        from app.api.transport import transport_bp
        from app.api.library import library_bp
        from app.api.engagement import engagement_bp
        from app.api.cafeteria import cafeteria_bp
        from app.api.chat import chat_bp
        from app.api.financial import financial_bp
        from app.api.platform import platform_bp
        from app.api.data import data_bp
        from app.web.routes import web_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(profile_bp, url_prefix='/api/profile')
        app.register_blueprint(map_bp, url_prefix='/api/map')
        app.register_blueprint(booking_bp, url_prefix='/api/bookings')
        app.register_blueprint(incident_bp, url_prefix='/api/incidents')
        app.register_blueprint(emergency_bp, url_prefix='/api/emergency')
        app.register_blueprint(reports_bp, url_prefix='/api/reports')
        app.register_blueprint(health_bp, url_prefix='/api/health')
        app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
        app.register_blueprint(rooms_bp, url_prefix='/api/rooms')
        app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
        app.register_blueprint(academic_bp, url_prefix='/api/academic')
        app.register_blueprint(transport_bp, url_prefix='/api/transport')
        app.register_blueprint(library_bp, url_prefix='/api/library')
        app.register_blueprint(engagement_bp, url_prefix='/api/engagement')
        app.register_blueprint(cafeteria_bp, url_prefix='/api/cafeteria')
        app.register_blueprint(chat_bp, url_prefix='/api/chat')
        app.register_blueprint(financial_bp, url_prefix='/api/financial')
        app.register_blueprint(platform_bp, url_prefix='/api/platform')
        app.register_blueprint(data_bp, url_prefix='/api/data')
        app.register_blueprint(web_bp)

    @app.context_processor
    def inject_permissions():
        """Make permissions available in all templates globally"""
        from flask import session
        from app.utils import has_permission
        def check_permission(permission):
            return has_permission(session.get('user_role', 'student'), permission)
        return dict(has_permission=check_permission)

    # Industrial Security Headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com https://cdn.socket.io; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://unpkg.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' https:;"
        return response

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app
