from flask import jsonify
from app.api.errors import bad_request
from app.validators import validate_book_type
from app.validators.validate_book_type import INVALID_BOOK_TYPE_MSG

def test_validate_book_type_fails_on_invalid_type(basic_app):
    @validate_book_type
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with invalid type
    with basic_app.test_request_context(method="POST", json={"type": "not a type"}):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_BOOK_TYPE_MSG

def test_validate_bookt_type_default(basic_app):
    @validate_book_type
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with invalid type
    with basic_app.test_request_context(method="POST", json={}) as ctx:
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"

        assert ctx.request.json["type"] == "cookbook"

def test_validate_book_type_passes_on_valid_type(basic_app):
    @validate_book_type
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with valid type
    with basic_app.test_request_context(method="POST", json={"type": "cookbook"}):
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"

    with basic_app.test_request_context(method="POST", json={"type": "magazine"}):
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"
