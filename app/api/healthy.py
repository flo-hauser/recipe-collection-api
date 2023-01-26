from . import bp
from flask import jsonify


@bp.route("/healthy", methods=["GET"])
def heathy_status():
    return jsonify({"healthy": True})
