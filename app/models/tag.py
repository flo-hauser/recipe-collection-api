from app.extensions import db

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(128), unique=True, nullable=False)
    color = db.Column(db.String(128))
    tag_type = db.Column(db.String(128))

    def __repr__(self):
        return "<Tag {}>".format(self.tag_name)

    def from_dict(self, data):
        for field in ["tag_name", "color", "tag_type"]:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            "id": self.id,
            "tag_name": self.tag_name,
            "color": self.color,
            "tag_type": self.tag_type,
        }
        return data