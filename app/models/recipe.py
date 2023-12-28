from flask import url_for
from app.extensions import db


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    page = db.Column(db.Integer)
    image = db.Column(db.String())

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)

    book = db.relationship("Book", back_populates="recipes")
    user = db.relationship("User", back_populates="recipes")

    def from_dict(self, data):
        for field in ["title", "page", "image_path"]:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            "id": self.id,
            "title": self.title,
            "page": self.page,
            "image": self.image,
            "_links": {
                "self": url_for("api.get_recipe", recipe_id=self.id),
                "user": url_for("api.get_user", id=self.user_id),
                "book": url_for("api.get_book", book_id=self.book_id),
                "image": "/images/{}/{}".format(self.id, self.image),
                "thumbnail": "/images/{}/{}.thumbnail".format(self.id, self.image)
            },
        }
        return data
