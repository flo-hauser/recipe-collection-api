from . import bp
from app.api.errors import bad_request
from app.models.user import User
from app.models.book import Cookbook, Magazine
from app.extensions import db
from flask import jsonify, request, url_for, abort
from app.api.auth import token_auth


@bp.route("/users/<int:user_id>/books", methods=["POST"])
@token_auth.login_required
def create_book(user_id):
    requesting_user: User = token_auth.current_user()
    if not requesting_user.id == user_id:
        abort(403)

    data = request.get_json() or {}

    if "type" not in data or "title" not in data:
        return bad_request("must include type and title fields")

    if data["type"] == "cookbook":
        book: Cookbook | Magazine = Cookbook()
    elif data["type"] == "magazine":
        book: Cookbook | Magazine = Magazine()
    else:
        return bad_request("type must be one of [cookbook, magazine]")
    book.from_dict(data)

    requesting_user.books.append(book)

    db.session.add(requesting_user)
    db.session.add(book)

    db.session.commit()

    return jsonify("yes")
