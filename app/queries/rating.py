from .user import filter_by_user
from app.models.rating import Rating
from app.extensions import db


def get_rating_by_recipe_query(user, recipe):
    return filter_by_user(db.select(Rating), user).where(Rating.recipe_id == recipe.id)