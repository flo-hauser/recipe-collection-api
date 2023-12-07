from flask import jsonify, request, abort
from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.models.user import User
from datetime import datetime

REFRESH_TOKEN = "refresh_token"


@bp.route("/tokens", methods=["GET"])
@basic_auth.login_required
def get_token():
    user: User = basic_auth.current_user()

    token_data = {
        "token": user.get_token(),
        "token_expiration": user.token_expiration,
        "token_lifetime": user.get_token_lifetime(),
    }
    
    refresh_token = user.get_refresh_token()

    response = jsonify(token_data)
    response.set_cookie(REFRESH_TOKEN, refresh_token, None, user.refresh_token_expiration, samesite="Lax", domain=None, httponly=True, secure=True)
    return response


@bp.route("/tokens", methods=["DELETE"])
@token_auth.login_required
def revoke_token():
    user: User = token_auth.current_user()
    user.revoke_token()

    return "", 204

@bp.route("/tokens/refresh", methods=["GET"])
def refresh_token():
    refresh_token = request.cookies.get(REFRESH_TOKEN)
    if not refresh_token:
        abort(400)


    result = db.session.execute(
        db.select(User).where(User.refresh_token == refresh_token)
    )
    user: User = result.scalars().first()

    if not user:
        abort(400)

    if user.refresh_token_expiration < datetime.utcnow():
        abort(404)

    token_data = {
        "token": user.get_token(forceNew=True),
        "token_expiration": user.token_expiration,
        "token_lifetime": user.get_token_lifetime(),
    }

    refresh_token = user.get_refresh_token()

    response = jsonify(token_data)
    response.set_cookie(REFRESH_TOKEN, refresh_token, None, user.refresh_token_expiration, httponly=True)
    return response
