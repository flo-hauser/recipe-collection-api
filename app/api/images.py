from . import bp
from app.models.user import User
from app.models.recipe import Recipe
from app.extensions import db
from flask import jsonify, request, abort, current_app
from app.api.auth import token_auth
from app.queries.recipe import get_user_recipes_by_id_query
from uuid import uuid4
from PIL import Image, ImageOps
import os

THUMBNAIL = "{}.thumbnail"


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@bp.route("recipes/<int:recipe_id>/image", methods=["PUT"])
@token_auth.login_required
def put_image(recipe_id):
    user: User = token_auth.current_user()

    result = db.session.execute(get_user_recipes_by_id_query(user, recipe_id))
    recipe: Recipe = result.scalars().one_or_none()
    if not recipe:
        abort(404)

    # File Handling
    if "image" not in request.files:
        abort(400)
    file = request.files["image"]
    if not allowed_file(file.filename):
        abort(400)

    # Image Validation
    with Image.open(file) as image:
        if image.format not in current_app.config["ALLOWED_EXTENSIONS"]:
            abort(400)
        image_format = image.format

    extension = image_format.lower().replace("jpeg", "jpg")
    unique_filename = str(uuid4()).replace("-", "") + "." + extension
    full_filename = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)

    # Resizing and save
    with Image.open(file) as image:
        ImageOps.fit(image, (1200, 800)).save(full_filename)

    # Create thumbnail
    with Image.open(full_filename) as image:
        image.thumbnail((128, 128))
        image.save(THUMBNAIL.format(full_filename), image_format)

    # Delete old Files
    if recipe.image:
        old_file = recipe.image
        try:
            os.unlink(os.path.join(current_app.config["UPLOAD_FOLDER"], old_file))
            os.unlink(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"], THUMBNAIL.format(old_file)
                )
            )
        except Exception:
            pass

    # Update DB
    recipe.image = unique_filename
    db.session.add(recipe)
    db.session.commit()

    return jsonify(recipe.to_dict())


@bp.route("recipes/<int:recipe_id>/image", methods=["DELETE"])
@token_auth.login_required
def delete_image(recipe_id):
    user: User = token_auth.current_user()

    result = db.session.execute(get_user_recipes_by_id_query(user, recipe_id))
    recipe: Recipe = result.scalars().one_or_none()
    if not recipe:
        abort(404)

    # Try deleting old Files
    if recipe.image:
        old_file = recipe.image
        try:
            os.unlink(os.path.join(current_app.config["UPLOAD_FOLDER"], old_file))
            os.unlink(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"], THUMBNAIL.format(old_file)
                )
            )
        except Exception:
            pass

    # Always update DB
    recipe.image = None
    db.session.add(recipe)
    db.session.commit()

    return jsonify(recipe.to_dict())
