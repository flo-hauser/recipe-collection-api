from . import bp
from flask import jsonify
from app import db


@bp.route("/healthy", methods=["GET"])
def heathy_status():
    healthy = True

    try:
        result = db.session.execute(db.select(db.text("1"))).fetchone()
        assert result == (1,)
    except Exception:
        healthy = False

    return jsonify({"healthy": healthy})
