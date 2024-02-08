from flask import app
from app.models.user_group import UserGroup
from tests.test_api_user import USER_ENDPOINT_WITH_ID

USER_GROUP_ENDPOINT = "api/1/user_groups"
USER_GROUP_ENDPOINT_ID = "{}/{}".format(USER_GROUP_ENDPOINT, "{}")
USER_GROUP_ENDPOINT_USER_ID = "{}/users/{}".format(USER_GROUP_ENDPOINT_ID, "{}")
USER_GROUP_ENDPOINT_USER_EMAIL = "{}/users/email".format(USER_GROUP_ENDPOINT_ID)

USER_2_EMAIL = "user_2@example.com"


def test_create_new_user_group(client, auth):
    auth.login()

    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201
    data = response.json
    assert data["group_name"] == "test_group"
    assert data["group_admin"] == auth.user.username
    assert len(data["users"]) == 1
    assert data["users"][0]["username"] == auth.user.username
    assert "self" in data["_links"]
    assert "users" in data["_links"]
    assert response.content_location == data["_links"]["self"]
    assert data["_links"]["users"][0] == USER_ENDPOINT_WITH_ID.format(auth.user.id)


def test_create_group_as_anonymous(client):
    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
    )

    assert response.status_code == 401


def test_delete_user_group(client, auth):
    auth.login()

    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201
    data = response.json
    user_group_id = data["id"]

    # delete the user group
    response = client.delete(
        USER_GROUP_ENDPOINT_ID.format(user_group_id), headers=auth.token_auth_header
    )

    assert response.status_code == 204

    # check if the user group is deleted
    response = client.get(
        USER_GROUP_ENDPOINT_ID.format(user_group_id), headers=auth.token_auth_header
    )
    assert response.status_code == 404


def test_delete_group_as_anonymous(client):
    # delete the user group
    response = client.delete(
        USER_GROUP_ENDPOINT_ID.format(1),
    )

    assert response.status_code == 401


def test_add_user_to_group_by_email_requires_email(client, auth):
    auth.login()

    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201
    data = response.json
    user_group_id = data["id"]

    # add user by email
    response = client.put(
        USER_GROUP_ENDPOINT_USER_EMAIL.format(user_group_id),
        json={"no-email": "any string"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 400


def test_add_user_to_group(client, auth):
    auth.login()

    user_to_add = {"username": "user_2", "email": USER_2_EMAIL}

    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201
    data = response.json
    user_group_id = data["id"]

    # add user by email
    response = client.put(
        USER_GROUP_ENDPOINT_USER_EMAIL.format(user_group_id),
        json={"email": user_to_add["email"]},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    data = response.json
    assert len(data["users"]) == 2
    assert data["users"][0]["username"] == auth.user.username
    assert data["users"][1]["username"] == user_to_add["username"]


def test_add_user_to_group_as_anonymous(client):
    response = client.put(
        USER_GROUP_ENDPOINT_ID.format(42) + "/users/email",
        json={"email": "valid@email.com"},
    )

    assert response.status_code == 401


def test_add_user_to_group_fails_if_user_in_group(client, auth):
    auth.login()

    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201

    # add user again
    response = client.put(
        USER_GROUP_ENDPOINT_ID.format(1) + "/users",
        json={"user_id": auth.user.id},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 400


def test_remove_user_from_group(client, auth):
    auth.login()

    auth.login()

    user_to_add = {"username": "user_2", "email": USER_2_EMAIL}

    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201
    data = response.json
    user_group_id = data["id"]

    # add user by email
    response = client.put(
        USER_GROUP_ENDPOINT_USER_EMAIL.format(user_group_id),
        json={"email": user_to_add["email"]},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    added_user_id = response.json["users"][1]["id"]

    # remove user
    response = client.delete(
        USER_GROUP_ENDPOINT_USER_ID.format(user_group_id, added_user_id),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    assert response.json["users"][0]["username"] == auth.user.username
    assert len(response.json["users"]) == 1


def test_remove_user_from_group_fails_if_user_not_in_group(client, auth):
    auth.login()

    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201

    # remove user
    response = client.delete(
        USER_GROUP_ENDPOINT_USER_ID.format(1, 99),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 404


def test_remove_user_fails_if_is_admin(client, auth):
    auth.login()

    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201

    # remove user
    response = client.delete(
        USER_GROUP_ENDPOINT_USER_ID.format(response.json["id"], auth.user.id),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 400
    assert (
        response.json["message"]
        == "group admin may not remove themselves from the group"
    )


def test_remove_user_as_anonymous(client):
    response = client.delete(
        USER_GROUP_ENDPOINT_USER_ID.format(1, 1),
    )

    assert response.status_code == 401


def test_remove_user_as_non_group_member_fails(client, auth):
    auth.login()

    # remove user
    response = client.delete(
        USER_GROUP_ENDPOINT_USER_ID.format(1, 3),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 403


def test_get_user_group(auth, client):
    auth.login()

    # create a new user group
    response = client.post(
        USER_GROUP_ENDPOINT,
        json={"group_name": "test_group"},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201
    data = response.json
    user_group_id = data["id"]

    # add second user to group
    response = client.put(
        USER_GROUP_ENDPOINT_USER_EMAIL.format(user_group_id),
        json={"email": USER_2_EMAIL},
        headers=auth.token_auth_header,
    )
    assert response.status_code == 200

    # get the user group
    response = client.get(
        USER_GROUP_ENDPOINT_ID.format(user_group_id), headers=auth.token_auth_header
    )

    assert response.status_code == 200
    data = response.json
    assert data["group_name"] == "test_group"
    assert data["group_admin"] == auth.user.username
    assert len(data["users"]) == 2
    assert data["users"][0]["username"] == auth.user.username
    assert data["users"][1]["username"] == "user_2"
    assert "self" in data["_links"]
    assert "users" in data["_links"]
    assert len(data["_links"]["users"]) == 2
    assert data["_links"]["users"][0] == USER_ENDPOINT_WITH_ID.format(auth.user.id)
    assert data["_links"]["users"][1] == USER_ENDPOINT_WITH_ID.format(3)


def test_get_group_as_anonymous(client):
    response = client.get(
        USER_GROUP_ENDPOINT_ID.format(1),
    )

    assert response.status_code == 401
