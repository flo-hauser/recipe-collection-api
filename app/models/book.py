from flask import url_for
from app.extensions import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    type = db.Column(db.String(64))
    year = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Relationships
    recipes = db.relationship(
        "Recipe", back_populates="book", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": "book",
        "polymorphic_on": type,
    }

    def from_dict(self, data):
        for field in ["title", "type", "year"]:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "year": self.year,
            "_links": {
                "self": url_for("api.get_book", book_id=self.id),
                "recipes": [r.to_dict()["_links"]["self"] for r in self.recipes],
                "user": url_for("api.get_user", id=self.user_id),
            },
        }
        return data

    @classmethod
    def get_type(cls):
        return cls.__mapper_args__["polymorphic_identity"]


class Magazine(Book):
    id = db.Column(db.ForeignKey("book.id"), primary_key=True)
    issue = db.Column(db.String)

    __mapper_args__ = {"polymorphic_identity": "magazine"}

    def from_dict(self, data):
        super().from_dict(data)
        for field in ["issue"]:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {**super().to_dict(), "issue": self.issue}

        return data


class Cookbook(Book):
    id = db.Column(db.ForeignKey("book.id"), primary_key=True)
    author = db.Column(db.String)

    __mapper_args__ = {"polymorphic_identity": "cookbook"}

    def from_dict(self, data):
        super().from_dict(data)
        for field in ["author"]:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {**super().to_dict(), "author": self.author}

        return data
