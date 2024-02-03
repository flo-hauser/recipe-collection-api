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
    CORS(app, origins=["*"], supports_credentials=True)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Custom CLI commands
    register_cli(app)

    # Register Blueprints
    from app.api import bp as api_bp
    from app.image_server import bp as image_bp

    app.register_blueprint(api_bp, url_prefix="/api/1")
    if app.config["DEBUG"] or app.config["TESTING"]:
        app.register_blueprint(image_bp)

    return app


from app.models.user import User
from app.models.user_group import UserGroup
from app.models.role import Role
from app.models.recipe import Recipe
from app.models.book import Book
from app.models.book import Magazine
from app.models.book import Cookbook
from app.models.rating import Rating
from app.models.tag import Tag
