from app.extensions import db


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(128), unique=True)

    def __repr__(self):
        return "<Role {}>".format(self.role_name)

    @classmethod
    def get_default_user_role(cls):
        return cls.query.filter_by(role_name="user").first()
