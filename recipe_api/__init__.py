import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app(test_config=None):
    db = SQLAlchemy()
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(SECRET_KEY="toBeChanged")
    app.config.from_mapping(SQLALCHEMY_DATABASE_URI="sqlite:///memory")


    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)

    app.config.from_mapping(test_config)

    db.init_app(app)

       # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/api/1/healthy")
    def hello():
        return {"status": "The app runs!"}

    return app