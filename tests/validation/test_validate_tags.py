from flask import jsonify
from app.api.errors import bad_request
from app.validators import validate_tags
from app.validators.validate_tags import INVALID_TAGS_MSG


def test_validate_tags_fails_on_missing_tags_not_list(basic_app):
    @validate_tags
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with invalid tags
    with basic_app.test_request_context(method="POST", json={"tags": "not a list"}):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_TAGS_MSG

    with basic_app.test_request_context(
        method="POST", json={"tags": {"not": "a list"}}
    ):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_TAGS_MSG


def test_validate_tags_fails_on_invalid_tag_content(basic_app):
    @validate_tags
    def dummy_route():
        return jsonify({"message": "success"})

    # no id or tag_name
    with basic_app.test_request_context(
        method="POST", json={"tags": [{"not": "a tag"}]}
    ):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_TAGS_MSG

    # tag name empty
    with basic_app.test_request_context(
        method="POST", json={"tags": [{"tag_name": ""}]}
    ):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_TAGS_MSG

    # tag_name too long
    with basic_app.test_request_context(
        method="POST", json={"tags": [{"tag_name": "a" * 26}]}
    ):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_TAGS_MSG

    # tag_id not int
    with basic_app.test_request_context(
        method="POST", json={"tags": [{"id": "not an int"}]}
    ):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_TAGS_MSG

    # color too long
    with basic_app.test_request_context(
        method="POST", json={"tags": [{"id": 1, "color": "a" * 26}]}
    ):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_TAGS_MSG

    # tag_type too long
    with basic_app.test_request_context(
        method="POST", json={"tags": [{"id": 1, "tag_type": "a" * 26}]}
    ):
        response = dummy_route()
        assert response.status_code == 400
        assert response.json["message"] == INVALID_TAGS_MSG


def test_validate_tags_passes(basic_app):
    @validate_tags
    def dummy_route():
        return jsonify({"message": "success"})

    # Test with full tag
    with basic_app.test_request_context(
        method="POST",
        json={
            "tags": [{"id": 1, "tag_name": "tag", "color": "color", "tag_type": "type"}]
        },
    ):
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"

    # test with only id
    with basic_app.test_request_context(method="POST", json={"tags": [{"id": 1}]}):
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"

    # test with only tag_name
    with basic_app.test_request_context(
        method="POST", json={"tags": [{"tag_name": "tag"}]}
    ):
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"

    # test with empty color
    with basic_app.test_request_context(
        method="POST", json={"tags": [{"tag_name": "tag", "color": None}]}
    ):
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"

    # test with empty tag_type
    with basic_app.test_request_context(
        method="POST", json={"tags": [{"tag_name": "tag", "tag_type": None}]}
    ):
        response = dummy_route()
        assert response.status_code == 200
        assert response.json["message"] == "success"
