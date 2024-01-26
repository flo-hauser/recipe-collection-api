from functools import wraps
from flask import request
from app.api.errors import bad_request

INVALID_RATING_MSG = "rating must be an integer between 1 and 5"

def _validate_rating(rating):
    try:
        rating = int(rating)
    except ValueError:
        return 0
    if not 1 <= rating <= 5:
        return 0
    return rating

def validate_rating(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # rating in query string
        if request.args.get("rating"):
            rating = _validate_rating(request.args.get("rating"))
            if not rating:
                return bad_request(INVALID_RATING_MSG)
            
        # if not additonal rating in json body, return
        if request.get_json(silent=True) is None:
            return f(*args, **kwargs)

        # rating in json body
        data = request.get_json()
        if "rating" in data:
            if not _validate_rating(data["rating"]):
                return bad_request(INVALID_RATING_MSG)
        else:
            request.json["rating"] = 0

        return f(*args, **kwargs)

    return decorated_function
