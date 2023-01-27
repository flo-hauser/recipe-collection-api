new_user_dict = {
    "username": "user1",
    "email": "mail@example.com",
    "password": "pass",
}


def test_create_user(client):
    response = client.post("/api/1/users", json=new_user_dict)

    assert response.status_code == 201
    res_data = response.json

    assert "id" in res_data
    assert "password" not in res_data
    assert res_data["username"] == new_user_dict["username"]


def test_create_user_fails_on_missing_username(client):
    test_data = {k: new_user_dict[k] for k in ["password", "email"]}

    response = client.post("/api/1/users", json=test_data)

    assert response.status_code == 400


def test_create_user_fails_on_missing_password(client):
    test_data = {k: new_user_dict[k] for k in ["username", "email"]}

    response = client.post("/api/1/users", json=test_data)

    assert response.status_code == 400


def test_create_user_fails_on_missing_email(client):
    test_data = {k: new_user_dict[k] for k in ["password", "username"]}

    response = client.post("/api/1/users", json=test_data)

    assert response.status_code == 400


def test_create_user_fails_on_existing_email(client):
    test_data = {**new_user_dict, "email": "admin@example.com"}

    response = client.post("/api/1/users", json=test_data)

    assert response.status_code == 400


def test_create_user_fails_on_existing_username(client):
    test_data = {**new_user_dict, "username": "admin"}

    response = client.post("/api/1/users", json=test_data)

    assert response.status_code == 400


def test_get_user(client, auth):
    auth.login()

    user_id = auth.user.id
    response = client.get(
        "/api/1/users/{:d}".format(user_id), headers=auth.token_auth_header
    )

    assert response.status_code == 200

    res_data = response.json
    assert res_data["username"] == auth.user.username
    assert res_data["id"] == auth.user.id
    assert "roles" in res_data
    assert "self" in res_data["_links"]


def test_get_user_as_another_user(client, auth):
    auth.login()

    user_id = auth.user.id
    response = client.get(
        "/api/1/users/{:d}".format(user_id + 1), headers=auth.token_auth_header
    )

    assert response.status_code == 200
    assert response.json["id"] == user_id + 1
    assert "email" not in response.json
    assert "password" not in response.json


def test_get_user_as_admin(client, auth):
    auth.login(username="admin", password="admin")

    user_id = auth.user.id
    response = client.get(
        "/api/1/users/{:d}".format(user_id + 1), headers=auth.token_auth_header
    )

    assert response.status_code == 200
    assert response.json["id"] == user_id + 1
    assert "email" in response.json
    assert "password" not in response.json


def test_get_user_as_anonymous_fails(client):
    user_id = 2
    response_1 = client.get("/api/1/users/{:d}".format(user_id))
    response_2 = client.get(
        "/api/1/users/{:d}".format(user_id),
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
