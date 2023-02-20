def test_get_all_recipes(client, auth, books, recipes):
    auth.login()

    response = client.get("api/1/recipes", headers=auth.token_auth_header)

    assert response.status_code == 200
    assert len(response.json) == 3

    for r in response.json:
        # only own books
        assert r["_links"]["user"][-1] == str(recipes.user_1["id"])


def test_get_recipe(client, auth, books, recipes):
    auth.login()

    response = client.get(
        "api/1/recipes/{}".format(recipes.book_1["id"]), headers=auth.token_auth_header
    )

    assert response.status_code == 200
    data = response.json

    assert data["title"] == books.book_1["title"]
    assert data["page"] == books.book_1["page"]
    assert data["image_path"] == books.book_1["image_path"]
    assert data["_links"] == books.book_1["_links"]
