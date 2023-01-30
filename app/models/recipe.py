from app.extensions import db


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    page = db.Column(db.Integer)
    image_path = db.Column(db.String())

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)

    book = db.relationship("Book", back_populates="recipes")
