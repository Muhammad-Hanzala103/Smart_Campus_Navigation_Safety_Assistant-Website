"""
CNSMS Application Factory
Creates and configures the Flask application with all extensions and blueprints.
"""
from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db, login_manager
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """
    Application factory function.
    
    Args:
        config_class: Configuration class to use (default: Config)
    
    Returns:
        Configured Flask application instance
    """
    # Point to templates and static in project root
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'incidents'), exist_ok=True)

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Configure CORS for Android clients
    cors_origins = app.config.get('CORS_ORIGINS', '*')
    if cors_origins == '*':
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    else:
        CORS(app, resources={r"/api/*": {"origins": cors_origins.split(',')}})
    
    logger.info(f"CORS enabled for origins: {cors_origins}")

    # User loader for Flask-Login (web sessions)
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Web Blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.dashboard import dashboard_bp
    from .blueprints.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Register API Blueprints
    from .blueprints.auth_api import auth_api_bp
    from .blueprints.api import api_bp
    
    app.register_blueprint(auth_api_bp, url_prefix='/api')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create Database Tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")

    logger.info(f"CNSMS Application initialized (AI Mode: {app.config.get('AI_MODE', 'mock')})")
    
    return app
