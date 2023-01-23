import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="toBeChanged")

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
        DATABASE=os.path.join(app.instance_path, 'recipe_api.sqlite'),

    app.config.from_mapping(test_config)

       # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/api/1/healthy')
    def hello():
        return 'The app runs!'

    return app