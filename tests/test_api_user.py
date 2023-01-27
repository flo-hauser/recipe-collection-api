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
