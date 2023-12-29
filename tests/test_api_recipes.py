new_recipe_dict = {
    "title": "New Title",
    "page": 250,
    "book_id": 1,
}


def test_get_all_recipes(client, auth, books, recipes):
    auth.login()

    response = client.get("api/1/recipes", headers=auth.token_auth_header)

    assert response.status_code == 200
    assert len(response.json) == 5

    for r in response.json:
        # only own books
        assert r["_links"]["user"][-1] == str(recipes.user_1["id"])


def test_get_recipe(client, auth, books, recipes):
    auth.login()

    response = client.get(
        "api/1/recipes/{}".format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    data = response.json

    assert data["title"] == recipes.recipe_1["title"]
    assert data["page"] == recipes.recipe_1["page"]
    assert data["image"] == recipes.recipe_1["image"]
    assert data["_links"] == recipes.recipe_1["_links"]
    assert "image" in data["_links"]
    assert "thumbnail" in data["_links"]
    assert "self" in data["_links"]


def test_get_recipe_of_another_user_404(books, auth, client, recipes):
    auth.login()

    response = client.get(
        "api/1/recipes/{}".format(recipes.recipe_4["id"]),
        headers=auth.token_auth_header,
    )
    assert response.status_code == 404


def test_get_recipe_not_existing_id_404(auth, client, books, recipes):
    auth.login()

    response = client.get("api/1/recipes/1234", headers=auth.token_auth_header)
    assert response.status_code == 404


def test_create_new_recipe(auth, client, books, recipes):
    auth.login()

    response = client.post(
        "/api/1/recipes", json=new_recipe_dict, headers=auth.token_auth_header
    )

    assert response.status_code == 201
    res_data = response.json

    assert "id" in res_data
    assert res_data["title"] == new_recipe_dict["title"]
    assert res_data["page"] == new_recipe_dict["page"]
    assert "image" in res_data
    assert "_links" in res_data
    assert res_data["_links"]["book"][-1] == str(new_recipe_dict["book_id"])


def test_create_recipe_fails_on_missing_title(auth, client, books):
    auth.login()
    test_data = {k: new_recipe_dict[k] for k in ["page", "book_id"]}
    response = client.post(
        "/api/1/recipes", json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400


def test_create_recipe_fails_on_empty_title(auth, client, books):
    auth.login()
    test_data = {k: new_recipe_dict[k] for k in ["page", "book_id"]}
    test_data["title"] = ""
    response = client.post(
        "/api/1/recipes", json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400


def test_create_recipe_fails_on_missing_book_id(auth, client, books):
    auth.login()
    test_data = {k: new_recipe_dict[k] for k in ["title", "page"]}
    response = client.post(
        "/api/1/recipes", json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400


def test_create_recipe_fails_on_missing_login(client):
    response = client.post("/api/1/books", json=new_recipe_dict)

    assert response.status_code == 401

def test_search_recipe(client, auth, books, recipes):
    auth.login()

    response = client.get(
        "api/1/recipes/search",
        headers=auth.token_auth_header,
        query_string = {"q": "rezept"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 2

def test_search_recipe_only_own_recipes(client, auth, books, recipes):
    auth.login()

    response = client.get(
        "api/1/recipes/search",
        headers=auth.token_auth_header,
        query_string = {"q": "title"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3


def test_update_recipe(client, auth, books, recipes):
    auth.login()

    updateData = {
        "title": "Updated Title",
        "page": 999,
        "book_id": str(books.book_2["id"])
    }

    response = client.put(
        "api/1/recipes/{}".format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        json=updateData
    )

    assert response.status_code == 200
    data = response.json
    assert data["title"] == updateData["title"]
    assert data["page"] == updateData["page"]
    assert data["_links"]["book"][-1] == updateData["book_id"]

def test_update_recipe_of_another_user_fails(client, auth, books, recipes):
    auth.login()

    updateData = {
        "title": "Updated Title",
        "page": 999,
        "book_id": str(books.book_2["id"])
    }

    response = client.put(
        "api/1/recipes/{}".format(recipes.recipe_4["id"]),
        headers=auth.token_auth_header,
        json=updateData
    )

    assert response.status_code == 404

def test_delete_recipe(client, auth, books, recipes):
    auth.login()

    response = client.delete(
        "api/1/recipes/{}".format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 204

def test_delete_recipe_of_another_user(client, auth, books, recipes):
    auth.login()

    response = client.delete(
        "api/1/recipes/{}".format(recipes.recipe_4["id"]),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 404
