from .user import filter_by_user_and_group
from app.models.recipe import Recipe
from app.extensions import db


def get_user_recipes_query(user):
    return filter_by_user_and_group(db.select(Recipe), user)


def get_user_recipes_by_id_query(user, recipe_id):
    return get_user_recipes_query(user).where(Recipe.id == recipe_id)
