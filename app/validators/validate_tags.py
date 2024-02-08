from functools import wraps
from flask import request
from app.api.errors import bad_request

INVALID_TAGS_MSG = "invalid tags, must be a list of tag objects"

max_tag_name_length = 25
max_tag_color_length = 25
max_tag_type_length = 25


def validate_tags(f):
    """Validate tags in json body at data["tags"]

    tags must be a list \n
    tag must have id or tag_name \n
    tag_name must be a string with length < 25 \n
    tag_name cannot be empty \n
    tag_id must be parsable to int
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # tags in json body
        data = request.get_json()
        if "tags" in data:
            tags = data["tags"]
            if not _validate_tags(tags):
                return bad_request(INVALID_TAGS_MSG)
        else:
            request.json["tags"] = []

        return f(*args, **kwargs)

    return decorated_function


def _validate_tags(tags):
    if not isinstance(tags, list):
        return False
    for tag in tags:
        if not _validate_tag(tag):
            return False
        if not _validate_tag_color(tag):
            return False
        if not _validate_tag_type(tag):
            return False
    return True


def _validate_tag(tag):
    if not ("id" in tag or "tag_name" in tag):
        return False
    if "tag_name" in tag and (
        not isinstance(tag["tag_name"], str)
        or len(tag["tag_name"]) > max_tag_name_length
        or len(tag["tag_name"]) == 0
    ):
        return False
    if "id" in tag:
        try:
            tag["id"] = int(tag["id"])
        except ValueError:
            return False
    return True


def _validate_tag_color(tag):
    if "color" in tag:
        if tag["color"] is None:  # may be empty
            return True
        if not isinstance(tag["color"], str):
            return False
        if len(tag["color"]) > max_tag_color_length:
            return False
    return True


def _validate_tag_type(tag):
    if "tag_type" in tag:
        if tag["tag_type"] is None:  # may be empty
            return True
        if not isinstance(tag["tag_type"], str):
            return False
        if len(tag["tag_type"]) > max_tag_type_length:
            return False
    return True
