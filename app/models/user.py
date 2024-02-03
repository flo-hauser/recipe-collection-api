from app.extensions import db
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
from app.models.user_roles import user_roles
from app.models.role import Role


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    refresh_token = db.Column(db.String(32), index=True, unique=True)
    refresh_token_expiration = db.Column(db.DateTime)

    # Relationships
    CASCADE_OPTIONS = "all, delete-orphan"
    roles = db.relationship("Role", secondary=user_roles)
    recipes = db.relationship("Recipe", cascade=CASCADE_OPTIONS)
    books = db.relationship("Book", cascade=CASCADE_OPTIONS)
    ratings = db.relationship("Rating", cascade=CASCADE_OPTIONS)

    user_group_id = db.Column(db.Integer, db.ForeignKey("user_group.id", ondelete="SET NULL"))
    user_group = db.relationship(
        "UserGroup", back_populates="users", foreign_keys=[user_group_id]
    )
    group_admin_of = db.relationship(
        "UserGroup",
        back_populates="group_admin",
        uselist=False,
        foreign_keys="UserGroup.group_admin_user_id",
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User {}>".format(self.username)

    def from_dict(self, data, new_user=False):
        for field in ["username", "email"]:
            if field in data:
                setattr(self, field, data[field])
        if new_user and "password" in data:
            self.set_password(data["password"])
            self.roles.append(Role.get_default_user_role())

    def to_dict(self, include_email=False):
        data = {
            "id": self.id,
            "username": self.username,
            "roles": self.get_roles(),
            "_links": {
                "self": url_for("api.get_user", id=self.id),
                "user_group": (
                    url_for("api.get_user_group", id=self.user_group_id)
                    if self.user_group_id
                    else None
                ),
            },
        }
        if include_email:
            data["email"] = self.email
        return data

    def get_token(self, expires_in=3600, force_new=False):
        now = datetime.utcnow()

        if (
            self.token and self.token_expiration > now + timedelta(seconds=60)
        ) and not force_new:
            return self.token

        self.token = secrets.token_hex(64)
        self.token_expiration = now + timedelta(seconds=expires_in)

        db.session.add(self)
        db.session.commit()

        return self.token

    def get_token_lifetime(self):
        if self.token_expiration:
            liftetime = self.token_expiration - datetime.utcnow()
            return liftetime.seconds
        else:
            return 0

    def get_refresh_token(self, expires_in=100):
        now = datetime.utcnow()

        self.refresh_token = secrets.token_hex(64)
        self.refresh_token_expiration = now + timedelta(days=100)

        db.session.add(self)
        db.session.commit()

        return self.refresh_token

    def get_refresh_token_lifetime(self):
        if self.refresh_token_expiration:
            liftetime = self.token_expiration - datetime.utcnow()
            return liftetime.seconds
        else:
            return 0

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=120)
        self.refresh_token_expiration = datetime.utcnow() - timedelta(seconds=120)

        db.session.add(self)
        db.session.commit()

    def get_roles(self):
        return [role.role_name for role in self.roles]

    @staticmethod
    def check_token(token):
        user: User = User.query.filter_by(token=token).first()

        if user is None or user.token_expiration < datetime.utcnow():
            return None
        else:
            return user
