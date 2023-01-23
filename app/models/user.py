from app.extensions import db
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

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

    def to_dict(self, include_email=False):
        data = {
            "id": self.id,
            "username": self.username,
            # "last_seen": self.last_seen.isoformat() + "Z",
            "_links": {
                "self": url_for("api.get_user", id=self.id),
            },
        }
        if include_email:
            data["email"] = self.email
        return data

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token

        self.token = secrets.token_hex(64)
        self.token_expiration = now + timedelta(seconds=expires_in)

        db.session.add(self)
        db.session.commit()

        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=120)

    @staticmethod
    def check_token(token):
        user: User = User.query.filter_by(token=token).first()

        if user is None or user.token_expiration < datetime.utcnow():
            return None
        else:
            return user
