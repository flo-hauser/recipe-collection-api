from .user import filter_by_user
from app.models.book import Book
from app.extensions import db


def get_user_books_query(user):
    return filter_by_user(db.select(Book), user)


def get_user_books_by_id_query(user, book_id):
    return get_user_books_query(user).where(Book.id == book_id)
