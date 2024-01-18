from flask import url_for
from app.extensions import db
from app.models.rating import Rating
from app.models.tag import Tag
from app.models.recipe_tag import recipe_tags


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

    ratings = db.relationship("Rating", cascade="all, delete-orphan")
    tags = db.relationship("Tag", secondary=recipe_tags)

    def from_dict(self, data):
        for field in ["title", "page", "image_path"]:
            if field in data:
                setattr(self, field, data[field])
        if "tags" in data:
            for tag in data["tags"]:
                # check if tag aleady exists
                if "id" in tag:
                    stmt = db.select(Tag).where(Tag.id == tag["id"])
                else:
                    stmt = db.select(Tag).where(Tag.tag_name == tag["tag_name"])
                tag_obj = db.session.scalar(stmt)

                if tag_obj:
                    self.tags.append(tag_obj)
                else:
                    new_tag = Tag()
                    new_tag.from_dict(tag)
                    self.tags.append(new_tag)

    def to_dict(self):
        # Calculate average rating
        average_rating = (
            db.session.execute(
                db.select(db.func.avg(Rating.rating)).where(Rating.recipe_id == self.id)
            ).scalar()
            or 0
        )

        data = {
            "id": self.id,
            "title": self.title,
            "page": self.page,
            "image": self.image,
            "rating": average_rating,
            "tags": [tag.to_dict() for tag in self.tags],
            "_links": {
                "self": url_for("api.get_recipe", recipe_id=self.id),
                "user": url_for("api.get_user", id=self.user_id),
                "book": url_for("api.get_book", book_id=self.book_id),
                "image": "/images/{}/{}".format(self.id, self.image)
                if self.image
                else None,
                "thumbnail": "/images/{}/{}.thumbnail".format(self.id, self.image)
                if self.image
                else None,
            },
        }
        return data
