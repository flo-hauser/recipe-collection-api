from app import db
from app.models.user import User

new_user_dict = {
    "username": "user1",
    "email": "mail@example.com",
    "password": "pass",
}

USER_ENDPOINT = "/api/1/users"
USER_ENDPOINT_MATCH = "{}/search/match".format(USER_ENDPOINT)
USER_ENDPOINT_EXISTS = "{}/exists".format(USER_ENDPOINT)
USER_ENDPOINT_ME = "{}/me".format(USER_ENDPOINT)
USER_ENDPOINT_WITH_ID = "{}/{}".format(USER_ENDPOINT, "{}")


def test_create_user(client):
    response = client.post(USER_ENDPOINT, json=new_user_dict)

    assert response.status_code == 201
    res_data = response.json

    assert "id" in res_data
    assert "password" not in res_data
    assert res_data["username"] == new_user_dict["username"]


def test_create_user_fails_on_missing_username(client):
    test_data = {k: new_user_dict[k] for k in ["password", "email"]}

    response = client.post(USER_ENDPOINT, json=test_data)

    assert response.status_code == 400


def test_create_user_fails_on_missing_password(client):
    test_data = {k: new_user_dict[k] for k in ["username", "email"]}

    response = client.post(USER_ENDPOINT, json=test_data)

    assert response.status_code == 400


def test_create_user_fails_on_missing_email(client):
    test_data = {k: new_user_dict[k] for k in ["password", "username"]}

    response = client.post(USER_ENDPOINT, json=test_data)

    assert response.status_code == 400


def test_create_user_fails_on_existing_email(client):
    test_data = {**new_user_dict, "email": "admin@example.com"}

    response = client.post(USER_ENDPOINT, json=test_data)

    assert response.status_code == 400


def test_create_user_fails_on_existing_username(client):
    test_data = {**new_user_dict, "username": "admin"}

    response = client.post(USER_ENDPOINT, json=test_data)

    assert response.status_code == 400


def test_get_user(client, auth):
    auth.login()

    user_id = auth.user.id
    response = client.get(
        USER_ENDPOINT_WITH_ID.format(user_id), headers=auth.token_auth_header
    )

    assert response.status_code == 200

    res_data = response.json
    assert res_data["username"] == auth.user.username
    assert res_data["id"] == auth.user.id
    assert res_data["email"] == auth.user.email
    assert "roles" in res_data
    assert "self" in res_data["_links"]

def test_get_self(client, auth):
    auth.login()

    response = client.get(
        USER_ENDPOINT_ME, headers=auth.token_auth_header
    )

    assert response.status_code == 200

    res_data = response.json
    assert res_data["username"] == auth.user.username
    assert res_data["id"] == auth.user.id
    assert res_data["email"] == auth.user.email
    assert "roles" in res_data
    assert "self" in res_data["_links"]

def test_search_user_match_by_name(client, auth):
    auth.login()

    response = client.get(
        USER_ENDPOINT_MATCH,
        headers=auth.token_auth_header,
        query_string = {"username": "user_1"}
    )

    assert response.status_code == 200

    res_data = response.json
    assert res_data["username"] == "user_1"
    assert "id" in res_data
    assert "email" not in res_data
    assert "roles" in res_data
    assert "self" in res_data["_links"]

def test_search_user_match_by_email(client, auth):
    auth.login()

    response = client.get(
        USER_ENDPOINT_MATCH,
        headers=auth.token_auth_header,
        query_string = {"email": "user_1@example.com"}
    )

    assert response.status_code == 200

    res_data = response.json
    assert res_data["username"] == "user_1"
    assert "id" in res_data
    assert "email" not in res_data
    assert "roles" in res_data
    assert "self" in res_data["_links"]

def test_search_user_match_by_name_404(client, auth):
    auth.login()

    response = client.get(
        USER_ENDPOINT_MATCH,
        headers=auth.token_auth_header,
        query_string = {"username": "no user"}
    )

    assert response.status_code == 404

def test_search_user_match_by_email_404(client, auth):
    auth.login()

    response = client.get(
        USER_ENDPOINT_MATCH,
        headers=auth.token_auth_header,
        query_string = {"email": "no@mail.com"}
    )

    assert response.status_code == 404

def test_search_user_match_not_logged_in(client, auth):
    response = client.get(
        USER_ENDPOINT_MATCH,
        query_string = {"username": "user_1"}
    )

    assert response.status_code == 401

def test_search_user_exists_by_name(client, auth):
    response = client.get(
        USER_ENDPOINT_EXISTS,
        headers=auth.token_auth_header,
        query_string = {"username": "user_1"}
    )

    assert response.status_code == 200

    res_data = response.json
    assert res_data == True

    response = client.get(
        USER_ENDPOINT_EXISTS,
        headers=auth.token_auth_header,
        query_string = {"username": "user_xx"}
    )

    assert response.status_code == 200

    res_data = response.json
    assert res_data == False

def test_search_user_exists_by_email(client, auth):
    response = client.get(
        USER_ENDPOINT_EXISTS,
        headers=auth.token_auth_header,
        query_string = {"email": "user_1@example.com"}
    )

    assert response.status_code == 200

    res_data = response.json
    assert res_data == True

    response = client.get(
        USER_ENDPOINT_EXISTS,
        headers=auth.token_auth_header,
        query_string = {"email": "no@mail.com"}
    )

    assert response.status_code == 200

    res_data = response.json
    assert res_data == False

def test_get_user_as_another_user(client, auth):
    auth.login()

    user_id = auth.user.id
    response = client.get(
        USER_ENDPOINT_WITH_ID.format(user_id + 1), headers=auth.token_auth_header
    )

    assert response.status_code == 200
    assert response.json["id"] == user_id + 1
    assert "email" not in response.json
    assert "password" not in response.json


def test_get_user_as_admin(client, auth):
    auth.login(username="admin", password="admin")

    user_id = auth.user.id
    response = client.get(
        USER_ENDPOINT_WITH_ID.format(user_id + 1), headers=auth.token_auth_header
    )

    assert response.status_code == 200
    assert response.json["id"] == user_id + 1
    assert "email" in response.json
    assert "password" not in response.json


def test_get_user_as_anonymous_fails(client):
    user_id = 2
    response_1 = client.get(USER_ENDPOINT_WITH_ID.format(user_id))
    response_2 = client.get(
        USER_ENDPOINT_WITH_ID.format(user_id),
        headers={"Authorization": "token: someRandomStringPretendingToBeAValidToken"},
    )

    assert response_1.status_code == 401
    assert response_2.status_code == 401


def test_get_user_with_invaid_id(client, auth):
    auth.login()
    user_id = str(auth.user.id) + "a"
    response = client.get(
        "/api/1/users/{}".format(user_id),
        headers={"Authorization": "token: someRandomStringPretendingToBeAValidToken"},
    )

    assert response.status_code == 404


def test_edit_user(app, client, auth):
    auth.login()
    user_id = auth.user.id
    request_body = {"username": "foo", "email": "foo@abc.de", "password": "foo"}
    response = client.put(
        USER_ENDPOINT_WITH_ID.format(user_id),
        headers=auth.token_auth_header,
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json["username"] == request_body["username"]
    assert response.json["email"] == request_body["email"]
    assert "password" not in response.json
    with app.app_context():
        user: User = db.session.execute(
            db.select(User).filter_by(id=user_id)
        ).scalar_one()
    assert user.check_password(request_body["password"])


def test_edit_user_as_another_user(client, auth):
    auth.login()
    user_id = auth.user.id
    request_body = {"username": "foo", "email": "foo@abc.de", "password": "foo"}
    response = client.put(
        USER_ENDPOINT_WITH_ID.format(user_id + 1),
        headers=auth.token_auth_header,
        json=request_body,
    )

    assert response.status_code == 403


def test_edit_user_as_admin(client, auth):
    auth.login(username="admin", password="admin")
    user_id = auth.user.id
    request_body = {"username": "foo", "email": "foo@abc.de", "password": "foo"}
    response = client.put(
        USER_ENDPOINT_WITH_ID.format(user_id + 1),
        headers=auth.token_auth_header,
        json=request_body,
    )

    assert response.status_code == 200


def test_edit_user_with_malformed_body(client, auth):
    auth.login()
    user_id = auth.user.id
    request_bodies = [
        {"username": "foo", "email": "foo@abc.de"},
        {"username": "foo", "password": "foo"},
        {"email": "foo@abc.de", "password": "foo"},
    ]

    for rb in request_bodies:
        response = client.put(
            USER_ENDPOINT_WITH_ID.format(user_id),
            headers=auth.token_auth_header,
            json=rb,
        )
        assert response.status_code == 400


def test_edit_user_with_existing_name_email(client, auth):
    auth.login()
    user_id = auth.user.id
    request_bodies = [
        {"username": "user_2", "email": "foo@abc.de", "password": "foo"},
        {"username": "foo", "email": "user_2@example.com", "password": "foo"},
    ]

    for rb in request_bodies:
        response = client.put(
            USER_ENDPOINT_WITH_ID.format(user_id),
            headers=auth.token_auth_header,
            json=rb,
        )
        assert response.status_code == 400


def test_get_users(client, auth):
    auth.login(username="admin", password="admin")
    response = client.get(
        USER_ENDPOINT,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 1
    assert "username" in response.json[0]
    assert "email" in response.json[0]
    assert "_links" in response.json[0]
    assert "id" in response.json[0]
    assert "roles" in response.json[0]


def test_get_users_as_non_admin(client, auth):
    auth.login()
    response_1 = client.get(
        USER_ENDPOINT,
        headers=auth.token_auth_header,
    )
    auth.logout()
    response_2 = client.get(
        USER_ENDPOINT,
        headers=auth.token_auth_header,
    )

    assert response_1.status_code == 403
    assert response_2.status_code == 401
