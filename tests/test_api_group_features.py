from .test_api_recipes import (
    RECIPE_ENDPOINT,
    RECIPE_ENDPOINT_WITH_ID,
    RECIPE_RATING,
    RECIPE_SEARCH,
)
from .test_api_books import (
    BOOK_ENDPOINT,
    BOOK_ENDPOINT_WITH_ID,
)
from flask.testing import FlaskClient
from .auth_actions import AuthActions

"""
Users of Group 1:
user_5:
    id: 6
    username: user_5
    email: user_5@example.com
    password: pass_5
    user_group_id: 1
    group_admin_of: UserGroup<1>

user_6:
    id: 7
    username: user_6
    email: user_6@example.com
    password: pass_6
    user_group_id: 1
"""


def _create_shared_books(client: FlaskClient, auth: AuthActions):
    created_books = []

    # create 2 books for user_5
    auth.login("user_5", "pass_5")

    response = client.post(
        BOOK_ENDPOINT,
        json={"title": "b_1", "type": "cookbook"},
        headers=auth.token_auth_header,
    )
    assert response.status_code == 201
    created_books.append(response.json)

    response = client.post(
        BOOK_ENDPOINT,
        json={"title": "b_2", "type": "magazine"},
        headers=auth.token_auth_header,
    )
    assert response.status_code == 201
    created_books.append(response.json)

    # create 1 book for user_6
    auth.login("user_6", "pass_6")
    response = client.post(
        BOOK_ENDPOINT,
        json={"title": "b_3", "type": "cookbook"},
        headers=auth.token_auth_header,
    )
    assert response.status_code == 201
    created_books.append(response.json)

    return created_books


def _create_shared_recipes(client: FlaskClient, auth: AuthActions, books: list):
    assert len(books) == 3

    created_recipes = []

    # create 2 recipes for user_5
    auth.login("user_5", "pass_5")

    response = client.post(
        RECIPE_ENDPOINT,
        json={"title": "r_1", "page": 42, "book_id": books[0]["id"]},
        headers=auth.token_auth_header,
    )
    assert response.status_code == 201
    created_recipes.append(response.json)

    response = client.post(
        RECIPE_ENDPOINT,
        json={"title": "r_2", "page": 51, "book_id": books[1]["id"]},
        headers=auth.token_auth_header,
    )
    assert response.status_code == 201
    created_recipes.append(response.json)

    # create 1 recipe for user_6
    auth.login("user_6", "pass_6")
    response = client.post(
        RECIPE_ENDPOINT,
        json={"title": "r_3", "page": 4, "book_id": books[2]["id"]},
        headers=auth.token_auth_header,
    )
    assert response.status_code == 201
    created_recipes.append(response.json)

    return created_recipes


def test_get_all_recipes(client, app, auth, books, recipes):
    """Test that users of the same group can see each other's recipes
    calling the standard books and recipe fixtures to create non-shared books and recipes
    """

    new_books = _create_shared_books(client, auth)
    new_recipes = _create_shared_recipes(client, auth, new_books)

    auth.login("user_5", "pass_5")
    response = client.get(RECIPE_ENDPOINT, headers=auth.token_auth_header)
    assert response.status_code == 200
    assert len(response.json) == 3
    assert response.json == new_recipes

    auth.login("user_6", "pass_6")
    response_2 = client.get(RECIPE_ENDPOINT, headers=auth.token_auth_header)
    assert response_2.status_code == 200
    assert response_2.json == response.json


def test_create_recipe_on_shared_book(app, client, auth):
    """tries to create a recipe on a book that belongs to the group
    new_books[2] belongs to user_6
    """

    new_books = _create_shared_books(client, auth)

    auth.login("user_5", "pass_5")
    response = client.post(
        RECIPE_ENDPOINT,
        json={"title": "r_1", "page": 42, "book_id": new_books[2]["id"]},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 201


def test_rate_shared_recipe(app, client, auth):
    """tries to rate a recipe that belongs to the group
    new_recipes[2] belongs to user_6
    """

    new_books = _create_shared_books(client, auth)
    new_recipes = _create_shared_recipes(client, auth, new_books)

    auth.login("user_5", "pass_5")
    response = client.put(
        RECIPE_RATING.format(new_recipes[2]["id"]),
        query_string={"rating": 5},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    assert response.json["rating"] == 5


def test_rate_shared_recipe_returns_average_group_rating(app, client, auth):
    """if a recipe is rated by a user of the group, the average rating of the group is returned"""

    new_books = _create_shared_books(client, auth)
    new_recipes = _create_shared_recipes(client, auth, new_books)

    auth.login("user_5", "pass_5")
    response = client.put(
        RECIPE_RATING.format(new_recipes[2]["id"]),
        query_string={"rating": 5},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    assert response.json["rating"] == 5

    auth.login("user_6", "pass_6")
    response = client.put(
        RECIPE_RATING.format(new_recipes[2]["id"]),
        query_string={"rating": 3},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    assert response.json["rating"] == 4


def test_user_can_modify_shared_recipe(app, client, auth):
    """user can modify a recipe that belongs to the group"""

    new_books = _create_shared_books(client, auth)
    new_recipes = _create_shared_recipes(client, auth, new_books)

    auth.login("user_5", "pass_5")
    update_data = {key: value for key, value in new_recipes[2].items()}
    update_data["title"] = "new_title"
    update_data["book_id"] = new_books[2]["id"]
    del update_data["rating"]

    response = client.put(
        RECIPE_ENDPOINT_WITH_ID.format(new_recipes[2]["id"]),
        json=update_data,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    assert response.json["title"] == "new_title"


def test_user_modifies_shared_recipe_and_adds_rating(app, client, auth):
    """user can modify a recipe that belongs to the group and add a rating"""

    new_books = _create_shared_books(client, auth)
    new_recipes = _create_shared_recipes(client, auth, new_books)

    # rate book 3 as user_6 with 3
    auth.login("user_6", "pass_6")
    response = client.put(
        RECIPE_RATING.format(new_recipes[2]["id"]),
        query_string={"rating": 3},
        headers=auth.token_auth_header,
    )
    assert response.status_code == 200

    # update recipe as user_5, add rating not modify rating
    auth.login("user_5", "pass_5")
    update_data = {key: value for key, value in new_recipes[2].items()}
    update_data["title"] = "new_title"
    update_data["book_id"] = new_books[2]["id"]
    update_data["rating"] = 5

    response = client.put(
        RECIPE_ENDPOINT_WITH_ID.format(new_recipes[2]["id"]),
        json=update_data,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    assert response.json["title"] == "new_title"
    assert response.json["rating"] == 4


def test_search_returns_shared_recipes(app, client, auth):
    """search returns recipes from the group"""

    new_books = _create_shared_books(client, auth)
    _create_shared_recipes(client, auth, new_books)

    auth.login("user_5", "pass_5")
    response = client.get(
        RECIPE_SEARCH, query_string={"q": "r_1"}, headers=auth.token_auth_header
    )
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "r_1"

    auth.login("user_6", "pass_6")
    response = client.get(
        RECIPE_SEARCH, query_string={"q": "r_1"}, headers=auth.token_auth_header
    )
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["title"] == "r_1"
