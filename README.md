# Recipe Server

This is the RESTful backend service used by the recipe collection web app.

## Description

This Service is suppoed to be used as a REST Api for my recipe collection web app.
It features it's own user and session managment as well as the domains techincal data.
Most ressources impement a basic CRUD interface.

The Service is build upon Flask using ideas from [The Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).

The User Authentication via basic-auth and tokens ist based upon [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/)

## Setup in local development

1. Create a Python virtual Enviroment

    ```sh
    python3 -m venv ./venv
    ```

2. Enviroment File `.env` in project root containing

    ```txt
    SECRET_KEY=a-very-sercret-string
    SECURITY_PASSWORD_SALT=random-string-for-salt
    ```

3. Export additional enviroment variables or use a `.flaskenv` file

    ```txt
    FLASK_APP=recipe_server.py
    FLASK_DEBUG=true
    ```

4. Activate venv and install requirements

    ```sh
    source venv/bin/activate

    pip3 install -r reqirements.txt
    ```

5. Start Flask app

    ```sh
    flask run
    ```

### Testing

TODO

## OpenAPI documentation

TODO

The REST API ist documented with the OpenAPI document.
