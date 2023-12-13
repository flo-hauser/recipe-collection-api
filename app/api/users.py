from . import bp
from app.api.errors import bad_request
from app.models.user import User
from app.extensions import db
from flask import jsonify, request, url_for, abort
from app.api.auth import token_auth


@bp.route("/users/<int:id>", methods=["GET"])
@token_auth.login_required
def get_user(id):
    requesting_user = token_auth.current_user()
    include_email = False
    if requesting_user.id == id:
        include_email = True
    elif "admin" in requesting_user.get_roles():
        include_email = True

    return jsonify(User.query.get_or_404(id).to_dict(include_email=include_email))

@bp.route("/users/search/match", methods=["GET"])
@token_auth.login_required
def search_user():
    username = request.args.get("username")
    email = request.args.get("email")

    if (username):
        user = User.query.filter_by(username=username).first_or_404()
    elif (email):
        user = User.query.filter_by(email=email).first_or_404()
    else:
        user = User.query.filter_by(id=-1).first_or_404()
    return jsonify(user.to_dict(include_email=False))

@bp.route("/users/exists", methods=["GET"])
def search_user_exists():
    username = request.args.get("username")
    email = request.args.get("email")

    if (username):
        user = User.query.filter_by(username=username).first()
    elif (email):
        user = User.query.filter_by(email=email).first()
    else:
        user = User.query.filter_by(id=-1).first()
    if user:
        return jsonify(True)
    return jsonify(False)

@bp.route("/users/me", methods=["GET"])
@token_auth.login_required
def get_self():
    requesting_user = token_auth.current_user()
    include_email = True

    return jsonify(requesting_user.to_dict(include_email=include_email))


@bp.route("/users", methods=["GET"])
@token_auth.login_required(role="admin")
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict(include_email=True) for user in users])


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
    response.content_location = url_for("api.get_user", id=user.id)

    return response


@bp.route("/users/<int:id>", methods=["PUT"])
@token_auth.login_required
def update_user(id):
    if not (
        token_auth.current_user().id == id
        or "admin" in token_auth.current_user().get_roles()
    ):
        abort(403)

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

    if password:
        user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict(include_email=True))
