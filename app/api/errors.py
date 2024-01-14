from flask import jsonify, current_app
from werkzeug.http import HTTP_STATUS_CODES
from app import db
from app.api import bp


def error_response(status_code: int, message: str = None):
    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}
    if message:
        payload["message"] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(msg: str):
    return error_response(400, msg)


@bp.app_errorhandler(404)
def not_found_error(error):
    return error_response(404, "Resource not found")


@bp.app_errorhandler(403)
def forbidden_error(status):
    return error_response(403, "Access Frobidden")


@bp.app_errorhandler(500)
def internal_error(error):
    if current_app.config["DEBUG"] or current_app.config["TESTING"]:
        db.session.rollback()
        return error_response(500, error)
    else:
        db.session.rollback()
        return error_response(500, "Internal Server Error")

