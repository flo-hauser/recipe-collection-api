from flask import jsonify
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.models.user import User


@bp.route("/tokens", methods=["GET"])
@basic_auth.login_required
def get_token():
    user: User = basic_auth.current_user()

    token_data = {
        "token": user.get_token(),
        "token_expiration": user.token_expiration,
        "token_lifetime": user.get_token_lifetime(),
    }

    return jsonify(token_data)


@bp.route("/tokens", methods=["DELETE"])
@token_auth.login_required
def revoke_token():
    user: User = token_auth.current_user()
    user.revoke_token()

    return "", 204
