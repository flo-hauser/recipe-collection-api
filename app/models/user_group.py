from app.extensions import db
from flask import url_for
from datetime import datetime


class UserGroup(db.Model):
    __tablename__ = "user_group"

    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(64), index=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = db.relationship(
        "User", back_populates="user_group", foreign_keys="User.user_group_id"
    )
    group_admin_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    group_admin = db.relationship(
        "User", back_populates="group_admin_of", foreign_keys=[group_admin_user_id]
    )

    def __repr__(self):
        return "<UserGroup {}>".format(self.name)

    def to_dict(self):
        data = {
            "id": self.id,
            "group_name": self.group_name,
            "group_admin": self.group_admin.username,
            "users": [user.to_dict() for user in self.users],
            "_links": {
                "self": url_for("api.get_user_group", id=self.id),
                "users": [url_for("api.get_user", id=user.id) for user in self.users],
            },
        }

        return data
