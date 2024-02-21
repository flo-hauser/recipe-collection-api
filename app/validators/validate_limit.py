from functools import wraps
from flask import request
from app.api.errors import bad_request

INVALID_LIMIT_MSG = "limit must be an integer greater than 0 and less than 100"


def validate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # rating in query string
        if request.args.get("limit"):
            limit = request.args.get("limit")
            try:
                limit = int(limit)
            except ValueError:
                return bad_request(INVALID_LIMIT_MSG)
            if not 1 <= limit <= 100:
                return bad_request(INVALID_LIMIT_MSG)

        return f(*args, **kwargs)

    return decorated_function
