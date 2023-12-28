from . import bp
from app.api.errors import bad_request
from app.models.user import User
from app.models.recipe import Recipe
from app.extensions import db
from flask import jsonify, request, abort, current_app
from app.api.auth import token_auth
from werkzeug.utils import secure_filename
from uuid import uuid4
import os


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

@bp.route("recipes/<int:recipe_id>/image", methods=["PUT"])
@token_auth.login_required
def put_image(recipe_id):
    user: User = token_auth.current_user()

    result = db.session.execute(
        db.select(Recipe)
        .join(User.recipes)
        .where(Recipe.id == recipe_id)
        .where(User.id == user.id)
    )
    recipe: Recipe = result.scalars().one_or_none()
    if not recipe:
        abort(404)

    # File Handling
    if "file" not in request.files:
        abort(400)
    file = request.files["file"]
    if not allowed_file(file.filename):
        abort(400)
    unique_filename = str(uuid4()).replace("-", "") + "." + file.filename.rsplit(".", 1)[1]
    full_filename = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(full_filename)

    # Delete old File
    if recipe.image:
        old_file = recipe.image
        try:
            os.unlink(os.path.join(current_app.config['UPLOAD_FOLDER'], old_file))
        except:
            pass
            
    # Update DB
    recipe.image = unique_filename
    db.session.add(recipe)
    db.session.commit()

    return jsonify(recipe.to_dict())
