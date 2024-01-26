from . import bp
from app.api.errors import bad_request
from app.models.user import User
from app.models.recipe import Recipe
from app.models.book import Book
from app.models.rating import Rating
from app.models.recipe_tag import recipe_tags
from app.extensions import db
from app.validators import (
    required_fields,
    required_query_params,
    validate_rating,
    validate_tags,
)
from flask import jsonify, request, url_for, abort
from app.api.auth import token_auth


@bp.route("/recipes", methods=["GET"])
@token_auth.login_required
def get_all_recipes():
    user: User = token_auth.current_user()

    result = db.session.execute(
        db.select(Recipe).join(User.recipes).where(User.id == user.id)
    )
    recipes = result.scalars().all()

    return jsonify([recipe.to_dict() for recipe in recipes])


@bp.route("/recipes", methods=["POST"])
@token_auth.login_required
@required_fields(["book_id", "title"])
@validate_rating
@validate_tags
def create_recipe():
    user: User = token_auth.current_user()
    data = request.get_json() or {}

    # Get referenced Book
    select_book = db.select(Book).where(Book.id == data["book_id"])
    book = db.session.execute(select_book).scalars().one_or_none()
    if not book:
        abort(404)

    recipe = Recipe()

    recipe.from_dict(data)
    recipe.book = book
    recipe.user = user

    db.session.add(recipe)
    db.session.commit()

    rating = data["rating"]
    if rating:
        r = Rating()
        r.rating = rating
        r.user = user
        r.recipe = recipe

        db.session.add(r)
        db.session.commit()

    response = jsonify(recipe.to_dict())
    response.status_code = 201
    response.content_location = url_for("api.get_recipe", recipe_id=recipe.id)

    return response


@bp.route("recipes/<int:recipe_id>", methods=["GET"])
@token_auth.login_required
def get_recipe(recipe_id):
    user: User = token_auth.current_user()

    result = db.session.execute(
        db.select(Recipe)
        .join(User.recipes)
        .where(Recipe.id == recipe_id)
        .where(User.id == user.id)
    )

    recipe = result.scalars().one_or_none()
    if not recipe:
        abort(404)

    return jsonify(recipe.to_dict())


@bp.route("recipes/search", methods=["GET"])
@token_auth.login_required
def search_recipe():
    user: User = token_auth.current_user()
    search_term = request.args.get("q")
    book = request.args.get("book")

    if not (search_term or book):
        query = db.select(Recipe).join(User.recipes).where(User.id == user.id)
    elif search_term and not book:
        query = (
            db.select(Recipe)
            .join(User.recipes)
            .where(User.id == user.id)
            .where(Recipe.title.contains(search_term))
        )
    elif book and not search_term:
        query = (
            db.select(Recipe)
            .join(User.recipes)
            .where(User.id == user.id)
            .where(Recipe.book_id == book)
        )
    recipes = db.session.execute(query).scalars().all()

    return jsonify([recipe.to_dict() for recipe in recipes])


@bp.route("/recipes/<int:recipe_id>", methods=["PUT"])
@token_auth.login_required
@required_fields(["book_id", "title"])
@validate_rating
@validate_tags
def update_recipe(recipe_id):
    user: User = token_auth.current_user()
    data = request.get_json() or {}

    # Get referenced Book
    select_book = db.select(Book).where(Book.id == data["book_id"])
    book = db.session.execute(select_book).scalars().one_or_none()
    if not book:
        abort(404)

    # Get existing Recipe
    result = db.session.execute(
        db.select(Recipe)
        .join(User.recipes)
        .where(Recipe.id == recipe_id)
        .where(User.id == user.id)
    )
    recipe: Recipe = result.scalars().one_or_none()
    if not recipe:
        abort(404)

    # remove old tags
    if "tags" in data:
        db.session.execute(
            db.delete(recipe_tags).where(recipe_tags.c.recipe_id == recipe_id)
        )
        recipe.tags = []

    recipe.from_dict(data)
    recipe.book = book

    db.session.add(recipe)
    db.session.commit()

    # Update Rating
    rating = data["rating"]
    if rating:
        r: Rating = (
            db.session.execute(
                db.select(Rating)
                .where(Rating.recipe_id == recipe_id)
                .where(Rating.user_id == user.id)
            )
            .scalars()
            .one_or_none()
        )
        if r:
            r.rating = rating
        else:
            r = Rating()
            r.rating = rating
            r.user = user
            r.recipe = recipe

        db.session.add(r)
        db.session.commit()

    return jsonify(recipe.to_dict())


@bp.route("/recipes/<int:recipe_id>", methods=["DELETE"])
@token_auth.login_required
def delete_recipe(recipe_id):
    user: User = token_auth.current_user()

    # Get existing Recipe
    result = db.session.execute(
        db.select(Recipe)
        .join(User.recipes)
        .where(Recipe.id == recipe_id)
        .where(User.id == user.id)
    )
    recipe: Recipe = result.scalars().one_or_none()
    if not recipe:
        abort(404)

    # dereference tags
    db.session.execute(
        db.delete(recipe_tags).where(recipe_tags.c.recipe_id == recipe_id)
    )
    recipe.tags = []

    result = db.session.execute(db.delete(Recipe).where(Recipe.id == recipe_id))
    if result.rowcount != 1:
        abort(500)
    db.session.commit()

    return "", 204


@bp.route("/recipes/<int:recipe_id>/rating", methods=["PUT"])
@token_auth.login_required
@validate_rating
@required_query_params(["rating"])
def rate_recipe(recipe_id):
    user: User = token_auth.current_user()
    rating = request.args.get("rating")

    # Get existing Recipe
    result = db.session.execute(
        db.select(Recipe)
        .join(User.recipes)
        .where(Recipe.id == recipe_id)
        .where(User.id == user.id)
    )
    recipe: Recipe = result.scalars().one_or_none()
    if not recipe:
        abort(404)

    # Get existing Rating
    r: Rating = (
        db.session.execute(
            db.select(Rating)
            .where(Rating.recipe_id == recipe_id)
            .where(Rating.user_id == user.id)
        )
        .scalars()
        .one_or_none()
    )

    if r:
        r.rating = rating
    # Create new Rating
    else:
        r = Rating()
        r.rating = rating
        r.user = user
        r.recipe = recipe

    db.session.add(r)
    db.session.commit()

    return jsonify(recipe.to_dict())
