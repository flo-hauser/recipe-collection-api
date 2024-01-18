from app.extensions import db


recipe_tags = db.Table(
    "recipe_tags",
    db.Column("recipe_id", db.ForeignKey("recipe.id"), primary_key=True),
    db.Column("tag_id", db.ForeignKey("tag.id"), primary_key=True),
)
