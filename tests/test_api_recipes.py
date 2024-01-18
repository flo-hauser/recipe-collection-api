new_recipe_dict = {
    "title": "New Title",
    "page": 250,
    "book_id": 1,
}

RECIPE_ENDPOINT = "api/1/recipes"
RECIPE_ENDPOINT_WITH_ID = "{}/{}".format(RECIPE_ENDPOINT, "{}")
RECIPE_RATING = "{}/{}/rating".format(RECIPE_ENDPOINT, "{}")
RECIPE_SEARCH = "{}/search".format(RECIPE_ENDPOINT)


def test_get_all_recipes(client, auth, books, recipes):
    auth.login()

    response = client.get(RECIPE_ENDPOINT, headers=auth.token_auth_header)

    assert response.status_code == 200
    assert len(response.json) == 5

    for r in response.json:
        # only own books
        assert r["_links"]["user"][-1] == str(recipes.user_1["id"])

def test_get_recipe(client, auth, books, recipes):
    auth.login()

    response = client.get(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    data = response.json

    assert data["title"] == recipes.recipe_1["title"]
    assert data["page"] == recipes.recipe_1["page"]
    assert data["image"] == recipes.recipe_1["image"]
    assert isinstance(data["tags"], list) and len(data["tags"]) == 2
    assert data["tags"][0]["tag_name"] == recipes.recipe_1["tags"][0]["tag_name"]
    assert data["tags"][1]["tag_name"] == recipes.recipe_1["tags"][1]["tag_name"]
    assert data["_links"] == recipes.recipe_1["_links"]
    assert "image" in data["_links"]
    assert "thumbnail" in data["_links"]
    assert "self" in data["_links"]

def test_get_recipe_of_another_user_404(books, auth, client, recipes):
    auth.login()

    response = client.get(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_4["id"]),
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
        RECIPE_ENDPOINT, json=new_recipe_dict, headers=auth.token_auth_header
    )

    assert response.status_code == 201
    res_data = response.json

    assert "id" in res_data
    assert res_data["title"] == new_recipe_dict["title"]
    assert res_data["page"] == new_recipe_dict["page"]
    assert "image" in res_data
    assert res_data["rating"] == 0
    assert "_links" in res_data
    assert res_data["_links"]["book"][-1] == str(new_recipe_dict["book_id"])

def test_create_new_recipe_with_rating(auth, client, books, recipes):
    auth.login()

    test_data = {k: new_recipe_dict[k] for k in ["title", "page", "book_id"]}
    test_data["rating"] = 3

    response = client.post(
        RECIPE_ENDPOINT, json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 201
    res_data = response.json

    assert res_data["rating"] == test_data["rating"]

def test_create_new_recipe_with_invalid_rating(auth, client, books, recipes):
    auth.login()

    # invalid range 
    test_data = {k: new_recipe_dict[k] for k in ["title", "page", "book_id"]}
    test_data["rating"] = 6

    response = client.post(
        RECIPE_ENDPOINT, json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 201
    res_data = response.json
    assert res_data["rating"] == 0

    # invalid literal
    test_data["rating"] = "abc"
    response = client.post(
        RECIPE_ENDPOINT, json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400

def test_create_recipe_fails_on_missing_title(auth, client, books):
    auth.login()
    test_data = {k: new_recipe_dict[k] for k in ["page", "book_id"]}
    response = client.post(
        RECIPE_ENDPOINT, json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400

def test_create_recipe_with_new_tag(auth, client, books, recipes):
    auth.login()
    test_data = {k: new_recipe_dict[k] for k in ["title", "page", "book_id"]}
    test_data["tags"] = [{"tag_name": "new tag"}]
    response = client.post(
        RECIPE_ENDPOINT, json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 201
    res_data = response.json

    assert len(res_data["tags"]) == 1
    assert res_data["tags"][0]["tag_name"] == "new tag"

def test_create_recipe_with_existing_tag(auth, client, books, recipes):
    auth.login()
    test_data = {k: new_recipe_dict[k] for k in ["title", "page", "book_id"]}
    test_data["tags"] = [{"id": recipes.recipe_1["tags"][0]["id"]}]
    response = client.post(
        RECIPE_ENDPOINT, json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 201
    res_data = response.json

    assert len(res_data["tags"]) == 1
    assert res_data["tags"][0]["tag_name"] == recipes.recipe_1["tags"][0]["tag_name"]

def test_create_recipe_with_invalid_tag_data(auth, client, books, recipes):
    auth.login()
    test_data = {k: new_recipe_dict[k] for k in ["title", "page", "book_id"]}
    test_data["tags"] = [{"no_id": 1234, "no_name": "new tag"}]
    response = client.post(
        RECIPE_ENDPOINT, json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400

def test_create_recipe_fails_on_empty_title(auth, client, books):
    auth.login()
    test_data = {k: new_recipe_dict[k] for k in ["page", "book_id"]}
    test_data["title"] = ""
    response = client.post(
        RECIPE_ENDPOINT, json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400

def test_create_recipe_fails_on_missing_book_id(auth, client, books):
    auth.login()
    test_data = {k: new_recipe_dict[k] for k in ["title", "page"]}
    response = client.post(
        RECIPE_ENDPOINT, json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400

def test_create_recipe_fails_on_missing_login(client):
    response = client.post("/api/1/books", json=new_recipe_dict)

    assert response.status_code == 401

def test_search_recipe_by_search_term(client, auth, books, recipes):
    auth.login()

    response = client.get(
        RECIPE_SEARCH,
        headers=auth.token_auth_header,
        query_string = {"q": "rezept"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 2

def test_search_recipes_by_book(client, auth, books, recipes):
    auth.login()

    response = client.get(
        RECIPE_SEARCH,
        headers=auth.token_auth_header,
        query_string = {"book": str(books.book_1["id"])}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 2
    for r in data:
        assert r["_links"]["book"][-1] == str(books.book_1["id"])

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

    update_data = {
        "title": "update title",
        "page": 999,
        "book_id": str(books.book_2["id"])
    }

    response = client.put(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        json=update_data
    )

    assert response.status_code == 200
    data = response.json
    assert data["title"] == update_data["title"]
    assert data["page"] == update_data["page"]
    assert data["_links"]["book"][-1] == update_data["book_id"]

def test_update_recipe_with_rating(client, auth, books, recipes):
    auth.login()
    
    update_data = {
        "title": "Updated Rating",
        "page": 999,
        "book_id": str(books.book_2["id"]),
        "rating": 1
    }

    response = client.put(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        json=update_data
    )

    assert response.status_code == 200
    data = response.json
    assert data["rating"] == update_data["rating"]

    update_data["rating"] = 5
    response = client.put(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        json=update_data
    )

    assert response.status_code == 200
    data = response.json
    assert data["rating"] == update_data["rating"]

def test_update_recipe_with_tags(client, auth, books, recipes):
    auth.login()
    
    update_data = {
        "title": "Updated Rating",
        "page": 999,
        "book_id": str(books.book_2["id"]),
        "tags": [{"tag_name": "new tag"}, {"id": recipes.recipe_1["tags"][0]["id"]}]
    }

    response = client.put(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        json=update_data
    )

    assert response.status_code == 200
    data = response.json
    assert len(data["tags"]) == 2
    assert "new tag" in [t["tag_name"] for t in data["tags"]]
    assert recipes.recipe_1["tags"][0]["tag_name"] in [t["tag_name"] for t in data["tags"]]

def test_update_recipe_with_invalid_rating(client, auth, books, recipes):
    auth.login()
    
    update_data = {
        "title": "Updated Rating",
        "page": 999,
        "book_id": str(books.book_2["id"]),
        "rating": 6
    }

    response = client.put(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        json=update_data
    )

    assert response.status_code == 200
    data = response.json
    assert data["rating"] == 0

    update_data["rating"] = "abc"
    response = client.put(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        json=update_data
    )

    assert response.status_code == 400

def test_update_recipe_of_another_user_fails(client, auth, books, recipes):
    auth.login()

    update_data = {
        "title": "Updated Title",
        "page": 999,
        "book_id": str(books.book_2["id"])
    }

    response = client.put(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_4["id"]),
        headers=auth.token_auth_header,
        json=update_data
    )

    assert response.status_code == 404

def test_delete_recipe(client, auth, books, recipes):
    auth.login()

    response = client.delete(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 204

def test_delete_recipe_of_another_user(client, auth, books, recipes):
    auth.login()

    response = client.delete(
        RECIPE_ENDPOINT_WITH_ID.format(recipes.recipe_4["id"]),
        headers=auth.token_auth_header,
    )

    assert response.status_code == 404

def test_recipe_rating(client, auth, books, recipes):
    auth.login()

    response = client.put(
        RECIPE_RATING.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        query_string={"rating": 3}
    )

    assert response.status_code == 200
    data = response.json
    assert data["rating"] == 3

def test_recipe_rating_of_another_user(client, auth, books, recipes):
    auth.login()

    response = client.put(
        RECIPE_RATING.format(recipes.recipe_4["id"]),
        headers=auth.token_auth_header,
        query_string={"rating": 3}
    )

    assert response.status_code == 404

def test_recipe_rating_invalid_rating(client, auth, books, recipes):
    auth.login()

    response = client.put(
        RECIPE_RATING.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        query_string={"rating": 6}
    )
    assert response.status_code == 400

    response = client.put(
        RECIPE_RATING.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        query_string={"rating": "abc"}
    )
    assert response.status_code == 400

    response = client.put(
        RECIPE_RATING.format(recipes.recipe_1["id"]),
        headers=auth.token_auth_header,
        query_string={"another_query": 3}
    )
    assert response.status_code == 400
