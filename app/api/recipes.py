from . import bp
from app.api.errors import bad_request
from app.models.user import User
from app.models.recipe import Recipe
from app.models.book import Book
from app.models.rating import Rating
from app.extensions import db
from flask import jsonify, request, url_for, abort
from app.api.auth import token_auth

INVALID_RATING_MSG = "rating must be an integer between 1 and 5"


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
def create_recipe():
    user: User = token_auth.current_user()
    data = request.get_json() or {}

    if "book_id" not in data:
        return bad_request("book_id must be set")
    if "title" not in data or not data["title"]:
        return bad_request("title must be set and a not empty string")
    if "rating" in data:
        try:
            rating: int = int(data["rating"])
        except ValueError:
            return bad_request(INVALID_RATING_MSG)
    else:
        rating = 0

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

    if 1 <= rating <= 5:
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

    if not search_term:
        query = db.select(Recipe).join(User.recipes).where(User.id == user.id)
    else:
        query = (
            db.select(Recipe)
            .join(User.recipes)
            .where(User.id == user.id)
            .where(Recipe.title.contains(search_term))
        )
    recipes = db.session.execute(query).scalars().all()

    return jsonify([recipe.to_dict() for recipe in recipes])


@bp.route("/recipes/<int:recipe_id>", methods=["PUT"])
@token_auth.login_required
def update_recipe(recipe_id):
    user: User = token_auth.current_user()
    data = request.get_json() or {}

    if "book_id" not in data:
        return bad_request("book_id must be set")
    if "title" not in data or not data["title"]:
        return bad_request("title must be set and a not empty string")
    if "rating" in data:
        try:
            rating: int = int(data["rating"])
        except ValueError:
            return bad_request(INVALID_RATING_MSG)
    else:
        rating = 0

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

    recipe.from_dict(data)
    recipe.book = book

    db.session.add(recipe)
    db.session.commit()

    # Update Rating
    if 1 <= rating <= 5:
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

    result = db.session.execute(db.delete(Recipe).where(Recipe.id == recipe_id))
    if result.rowcount != 1:
        abort(500)
    db.session.commit()

    return "", 204


@bp.route("/recipes/<int:recipe_id>/rating", methods=["PUT"])
@token_auth.login_required
def rate_recipe(recipe_id):
    user: User = token_auth.current_user()
    rating = request.args.get("rating")

    # Validate rating
    if not rating:
        return bad_request("rating must be set")
    try:
        rating = int(rating)
    except ValueError:
        return bad_request(INVALID_RATING_MSG)
    if not 1 <= rating <= 5:
        return bad_request(INVALID_RATING_MSG)

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
