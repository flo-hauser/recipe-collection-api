from . import bp
from app.api.errors import bad_request
from app.models.user import User
from app.models.book import Cookbook, Magazine, Book
from app.extensions import db
from flask import jsonify, request, url_for, abort
from app.api.auth import token_auth


@bp.route("/books/types", methods=["GET"])
def get_book_types():
    book_types = [cls.get_type() for cls in [Cookbook, Magazine]]

    return jsonify(book_types)


@bp.route("/books", methods=["POST"])
@token_auth.login_required
def create_book():
    user: User = token_auth.current_user()
    data = request.get_json() or {}

    if "type" not in data or "title" not in data:
        return bad_request("must include type and title fields")

    if data["type"] == "cookbook":
        book: Cookbook | Magazine = Cookbook()
    elif data["type"] == "magazine":
        book: Cookbook | Magazine = Magazine()
    else:
        return bad_request(
            "type must be one of {}".format(url_for("api.get_book_types"))
        )
    book.from_dict(data)
    user.books.append(book)

    db.session.add(user)
    db.session.add(book)

    db.session.commit()

    response = jsonify(book.to_dict())
    response.status_code = 201
    response.content_location = url_for("api.get_book", book_id=book.id)

    return response


@bp.route("/books", methods=["GET"])
@token_auth.login_required
def get_all_books():
    user: User = token_auth.current_user()

    result = db.session.execute(
        db.select(Book).join(User.books).where(User.id == user.id)
    )
    books = result.scalars().all()

    return jsonify([book.to_dict() for book in books])


@bp.route("/books/<int:book_id>", methods=["GET"])
@token_auth.login_required
def get_book(book_id):
    user: User = token_auth.current_user()

    result = db.session.execute(
        db.select(Book)
        .join(User.books)
        .where(Book.id == book_id)
        .where(User.id == user.id)
    )
    book = result.scalars().one_or_none()
    if not book:
        abort(404)

    return jsonify(book.to_dict())


@bp.route("/books/<int:book_id>", methods=["PUT"])
@token_auth.login_required
def update_book(book_id):
    user: User = token_auth.current_user()

    result = db.session.execute(
        db.select(Book)
        .join(User.books)
        .where(Book.id == book_id)
        .where(User.id == user.id)
    )
    book = result.scalars().one_or_none()
    if not book:
        abort(404)

    data = request.get_json() or {}

    if "type" not in data or "title" not in data:
        return bad_request("must include type and title fields")
    if data["type"] != book.type:
        return bad_request("type must match existing type: {}".format(book.type))

    book.title = data.get("title")
    book.year = data.get("year")

    if data["type"] == "cookbook":
        book.author = data.get("author")
    elif data["type"] == "magazine":
        book.issue = data.get("issue")

    db.session.add(book)
    db.session.commit()

    return jsonify(book.to_dict())


@bp.route("/books/<int:book_id>", methods=["DELETE"])
@token_auth.login_required
def delete_book(book_id):
    user: User = token_auth.current_user()

    result = db.session.execute(
        db.select(Book)
        .join(User.books)
        .where(Book.id == book_id)
        .where(User.id == user.id)
    )
    book = result.scalars().one_or_none()
    if not book:
        abort(404)

    result = db.session.execute(db.delete(Book).where(Book.id == book_id))
    if result.rowcount != 1:
        abort(500)
    db.session.commit()

    return "", 204
