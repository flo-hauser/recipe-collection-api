from functools import wraps
from flask import request
from app.models.book import Cookbook, Magazine
from app.api.errors import bad_request


book_types = [cls.get_type().lower() for cls in [Cookbook, Magazine]]
INVALID_BOOK_TYPE_MSG = "type must be one of {}".format("cookbook, magazine")


def validate_book_type(f):
    """Validate book type in json body at data["type"]

    type must be one of cookbook, magazine\n
    defaults to cookbook if not present
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # type in json body
        data = request.get_json()
        if "type" in data:
            is_valid = data["type"] in book_types
            if not is_valid:
                return bad_request(INVALID_BOOK_TYPE_MSG)
        else:
            request.json["type"] = "cookbook"
        return f(*args, **kwargs)
    return decorated_function
