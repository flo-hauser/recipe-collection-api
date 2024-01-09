from . import bp
from flask import abort, current_app, send_file
import re
import os


@bp.route("/images/<int:recipe_id>/<string:image_file>", methods=["GET"])
def get_image(recipe_id, image_file):
    # validate image_file path
    expr = re.compile(r"[a-z0-9]{32}.[a-z]{3,4}(.thumbnail)?")
    if not expr.match(image_file):
        abort(400)

    path = os.path.join("../", current_app.config["UPLOAD_FOLDER"], image_file)

    try:
        return send_file(path)
    except FileNotFoundError:
        abort(404)
