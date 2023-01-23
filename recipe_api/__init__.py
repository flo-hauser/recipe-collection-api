import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    # Create App and Config
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Register App to extensions
    db.init_app(app)
    migrate.init_app(app)

    # Register Blueprints
    from recipe_api.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api/1")

    return app

from recipe_api import models