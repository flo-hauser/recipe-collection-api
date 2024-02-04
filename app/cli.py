import os
from os import getenv
from dotenv import load_dotenv
from app.extensions import db
from app.models.user import User
from app.models.role import Role

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

def register_cli(app):
    @app.cli.command("init_db")
    def init_db():
        db.create_all()

    @app.cli.command("populate")
    def populate():
        # Create basic roles
        admin_role = Role(id=1, role_name="admin")
        user_role = Role(id=2, role_name="user")

        db.session.add(admin_role)
        db.session.add(user_role)

        db.session.commit()

        # Create user admin
        admin = User()
        admin.username = getenv("ADMIN_USER", "admin")
        admin.set_password(getenv("ADMIN_PASSWORD", "admin"))
        admin.email = getenv("ADMIN_EMAIL", "admin@example.com")
        admin.roles.append(admin_role)
        admin.roles.append(user_role)

        db.session.add(admin)
        db.session.commit()

    @app.cli.command("drop_db")
    def drop_db():
        db.drop_all()
