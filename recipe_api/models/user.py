from recipe_api import db

class User:
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.username)

    def to_dict(self, include_email=False):
        ...
    
    @classmethod
    def static_to_dict(cls):
        data = {
            "this": "is",
            "only": "static",
            "test": "data"
        }

        return data