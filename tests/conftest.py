import pytest
from app import create_app
from config import TestConfig
from app.extensions import db
from app.models.role import Role
from app.models.user import User


@pytest.fixture()
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        # Role Setup
        admin_role = Role(id=1, role_name="admin")
        user_role = Role(id=2, role_name="user")

        db.session.add(admin_role)
        db.session.add(user_role)

        # Create user admin
        # TODO get admin credentials and data from enviroment vars
        admin = User()
        admin.username = "admin"
        admin.set_password("admin")
        admin.email = "admin@example.com"
        admin.roles.append(admin_role)
        admin.roles.append(user_role)

        db.session.add(admin)
        db.session.commit()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
