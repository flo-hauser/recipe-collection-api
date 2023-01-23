from flask import Flask
from config import Config

# Extensions
from app.extensions import db, migrate


def create_app(config_class=Config):
    # Create App and Config
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api/1")

    return app
