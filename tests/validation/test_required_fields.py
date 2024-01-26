from flask import jsonify
from unittest.mock import patch
from app.api.errors import bad_request
from app.validators import required_fields


patch("app.api.errors.bad_request", return_value=("mock error", 400))


def test_required_fields_fails(basic_app):
    @required_fields(["field1", "field2"])
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with missing required field
    with basic_app.test_request_context(method="POST", json={"field1": "value1"}):
        response = dummy_route()
        assert response.status_code == 400

    # Test with empty required field
    with basic_app.test_request_context(
        method="POST", json={"field1": "value1", "field2": ""}
    ):
        response = dummy_route()
        assert response.status_code == 400


def test_required_fields_passes(basic_app):
    @required_fields(["field1", "field2"])
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with all required fields
    with basic_app.test_request_context(
        method="POST", json={"field1": "value1", "field2": "value2"}
    ):
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"
