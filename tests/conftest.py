import pytest
from os import getenv
from app import create_app
from config import TestConfig
from tests.auth_actions import AuthActions
from tests.book_fixtures import BookFixtures
from tests.recipe_fixtures import RecipeFixtures
from app.extensions import db
from app.models.role import Role
from app.models.user import User
from app.models.user_group import UserGroup


@pytest.fixture
def basic_app():
    yield create_app(TestConfig)


@pytest.fixture
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
        admin = User()
        admin.username = getenv("ADMIN_USER", "admin")
        admin.set_password(getenv("ADMIN_PASSWORD", "admin"))
        admin.email = getenv("ADMIN_EMAIL", "admin@example.com")
        admin.roles.append(admin_role)
        admin.roles.append(user_role)
        db.session.add(admin)

        # 4 test users - user_n+1:pass_n+1 user_n+1@example.com
        for i in range(4):
            u = User()
            user_data = {
                "username": "user_{:d}".format(i + 1),
                "email": "user_{:d}@example.com".format(i + 1),
                "password": "pass_{:d}".format(i + 1),
            }
            u.from_dict(user_data, new_user=True)
            db.session.add(u)

        # 2 users belonging to one group
        # for testing the user_group features
        u_g_1 = User()
        user_data = {
            "username": "user_5",
            "email": "user_5@example.com",
            "password": "pass_5",
        }
        u_g_1.from_dict(user_data, new_user=True)
        db.session.add(u_g_1)
        db.session.commit()

        user_group = UserGroup()
        user_group.group_name = "group_name"
        user_group.group_admin = u_g_1
        db.session.add(user_group)
        db.session.commit()

        u_g_1.user_group = user_group
        db.session.add(u_g_1)

        u_g_2 = User()
        user_data = {
            "username": "user_6",
            "email": "user_6@example.com",
            "password": "pass_6",
        }
        u_g_2.from_dict(user_data, new_user=True)
        u_g_2.user_group = user_group

        db.session.add(u_g_2)
        db.session.commit()

        print("Database setup complete")

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth(app, client):
    return AuthActions(app, client)


@pytest.fixture
def books(app):
    return BookFixtures(app)


@pytest.fixture
def recipes(app):
    return RecipeFixtures(app)
