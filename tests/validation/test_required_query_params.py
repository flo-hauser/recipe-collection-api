from flask import jsonify
from unittest.mock import patch
from app.api.errors import bad_request
from app.validators import required_query_params

patch("app.api.errors.bad_request", return_value=("mock error", 400))

def test_required_query_params_fails(basic_app):
    @required_query_params(["param1", "param2"])
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with missing required query param, param1 is present, param2 is missing
    with basic_app.test_request_context(
        method="GET", query_string={"param1": "value1"}
    ):
        response = dummy_route()
        assert response.status_code == 400


def test_required_query_params_passes(basic_app):
    @required_query_params(["param1", "param2"])
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with all required query params
    with basic_app.test_request_context(
        method="GET", query_string={"param1": "value1", "param2": "value2"}
    ):
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"
