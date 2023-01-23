from . import bp
from app.api.errors import bad_request
from app.models.user import User
from app.models.role import Role
from app import db
from flask import jsonify, request, url_for, abort
from app.api.auth import token_auth


@bp.route("/users/<int:id>", methods=["GET"])
@token_auth.login_required
def get_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route("/users", methods=["GET"])
@token_auth.login_required(role="admin")
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json() or {}

    if "username" not in data or "email" not in data or "password" not in data:
        return bad_request("must include username, email and password fields")
    if User.query.filter_by(username=data["username"]).first():
        return bad_request("please use a different username")
    if User.query.filter_by(email=data["email"]).first():
        return bad_request("please use a different email address")

    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()

    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers["Location"] = url_for("api.get_user", id=user.id)

    return response


@bp.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    user: User = User.query.get_or_404(id)
    data = request.get_json() or {}

    if "username" not in data or "email" not in data or "password" not in data:
        return bad_request("must include username, email and password fields")

    username = data["username"]
    email = data["email"]
    password = data["password"]

    if (
        not username == user.username
        and User.query.filter_by(username=username).first()
    ):
        return bad_request("please use a different username")
    if not email == user.email and User.query.filter_by(email=email).first():
        return bad_request("please use a different email address")

    user.from_dict(data, new_user=False)

    return jsonify(user.to_dict())
