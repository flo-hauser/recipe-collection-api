from app.extensions import db


user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("role_id", db.ForeignKey("role.id"), primary_key=True),
)
