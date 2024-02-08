from .user import filter_by_user
from app.models.rating import Rating
from app.extensions import db


def get_rating_by_recipe_and_user_query(user, recipe):

    return db.select(Rating).where(
        db.and_(Rating.recipe_id == recipe.id, Rating.user_id == user.id)
    )
