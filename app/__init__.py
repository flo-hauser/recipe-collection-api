from flask import Flask
from flask_cors import CORS
from config import Config
from app.cli import register_cli

# Extensions
from app.extensions import db, migrate


def create_app(config_class=Config):
    # Create App and Config
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    CORS(app)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.api import bp as api_bp

    # Custom CLI commands
    register_cli(app)

    app.register_blueprint(api_bp, url_prefix="/api/1")

    return app


from app.models.user import User
from app.models.role import Role
from app.models.recipe import Recipe
from app.models.book import Book
from app.models.book import Magazine
from app.models.book import Cookbook
