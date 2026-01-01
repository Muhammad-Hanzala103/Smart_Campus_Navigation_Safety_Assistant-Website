import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints (will be imported after creating blueprints)
    from app.api.auth import auth_bp
    from app.api.map import map_bp
    from app.api.bookings import booking_bp
    from app.api.incidents import incident_bp
    from app.api.analytics import analytics_bp
    from app.web.routes import web_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(map_bp, url_prefix='/api/map')
    app.register_blueprint(booking_bp, url_prefix='/api/bookings')
    app.register_blueprint(incident_bp, url_prefix='/api/incidents')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(web_bp) # Web routes usually at root or /admin

    return app
