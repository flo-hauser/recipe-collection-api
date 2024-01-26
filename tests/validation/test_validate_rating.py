from flask import jsonify
from unittest.mock import patch
from app.api.errors import bad_request
from app.validators import validate_rating
from app.validators.validate_rating import INVALID_RATING_MSG


patch("app.api.errors.bad_request", return_value=("mock error", 400))


def test_validate_rating_fails(basic_app):
    @validate_rating
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with invalid rating
    with basic_app.test_request_context(
        method="POST", json={"rating": "not an integer"}
    ):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_RATING_MSG

    # Test with rating out of range
    with basic_app.test_request_context(method="POST", json={"rating": 6}):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_RATING_MSG


def test_validate_rating_passes_json_body(basic_app):
    @validate_rating
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with valid rating
    for rating in range(1, 6):
        with basic_app.test_request_context(method="POST", json={"rating": rating}):
            response = dummy_route()
            assert response.status_code == 200
            assert response.json["message"] == "success"


def test_validate_rating_passes_query_string(basic_app):
    @validate_rating
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with valid rating
    for rating in range(1, 6):
        with basic_app.test_request_context(
            method="PUT", query_string={"rating": rating}
        ):
            response = dummy_route()
            assert response.status_code == 200
            assert response.json["message"] == "success"


def test_validate_rating_no_rating_modifies_request_json(basic_app):
    @validate_rating
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with no rating
    # the request object should be modified to include a rating of 0
    with basic_app.test_request_context(method="POST", json={}) as ctx:
        response = dummy_route()
        assert response.status_code == 200
        assert ctx.request.get_json()["rating"] == 0
