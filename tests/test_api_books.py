from app.extensions import db
from app.models.book import Book


def test_get_book_types(client):
    response = client.get("api/1/books/types")

    assert response.status_code == 200
    assert response.json == ["cookbook", "magazine"]


def test_get_all_books(books, auth, client):
    auth.login()

    response = client.get("api/1/books", headers=auth.token_auth_header)

    assert response.status_code == 200
    assert len(response.json) == 2
    for b in response.json:
        # only own books
        assert b["_links"]["user"][-1] == str(books.user_1["id"])


def test_get_book(books, auth, client):
    auth.login()

    response = client.get(
        "api/1/books/{}".format(books.book_1["id"]), headers=auth.token_auth_header
    )

    assert response.status_code == 200
    data = response.json
    assert data["title"] == books.book_1["title"]
    assert data["type"] == books.book_1["type"]
    assert data["year"] == books.book_1["year"]
    assert data["author"] == books.book_1["author"]
    assert data["_links"] == books.book_1["_links"]

def test_get_book_with_recipes(books, recipes, auth, client):
    auth.login()

    response = client.get(
        "api/1/books/{}".format(books.book_1["id"]), headers=auth.token_auth_header
    ) 

    assert response.status_code == 200
    data = response.json
    assert len(data["_links"]["recipes"]) == 2
    assert data["_links"]["recipes"][0] == recipes.recipe_1["_links"]["self"]
    assert data["_links"]["recipes"][1] == recipes.recipe_2["_links"]["self"]


def test_get_book_of_another_user_404(books, auth, client):
    auth.login()

    response = client.get(
        "api/1/books/{}".format(books.book_3["id"]), headers=auth.token_auth_header
    )
    assert response.status_code == 404


def test_get_book_not_existing_id_404(auth, client):
    auth.login()

    response = client.get("api/1/books/1234", headers=auth.token_auth_header)
    assert response.status_code == 404


new_cb_dict = {"title": "t1", "year": 2000, "author": "a b", "type": "cookbook"}
new_mag_dict = {"title": "t2", "year": 2001, "issue": "15 - 5", "type": "magazine"}


def test_create_cookbook(auth, client):
    auth.login()
    response = client.post(
        "/api/1/books", json=new_cb_dict, headers=auth.token_auth_header
    )

    assert response.status_code == 201
    res_data = response.json

    assert "id" in res_data
    assert res_data["title"] == new_cb_dict["title"]
    assert res_data["year"] == new_cb_dict["year"]
    assert res_data["author"] == new_cb_dict["author"]
    assert res_data["type"] == new_cb_dict["type"]


def test_create_magazine(auth, client):
    auth.login()
    response = client.post(
        "/api/1/books", json=new_mag_dict, headers=auth.token_auth_header
    )

    assert response.status_code == 201
    res_data = response.json

    assert "id" in res_data
    assert res_data["title"] == new_mag_dict["title"]
    assert res_data["year"] == new_mag_dict["year"]
    assert res_data["issue"] == new_mag_dict["issue"]
    assert res_data["type"] == new_mag_dict["type"]


def test_create_cookbook_fails_on_missing_title(auth, client):
    auth.login()
    test_data = {k: new_cb_dict[k] for k in ["year", "author", "type"]}
    response = client.post(
        "/api/1/books", json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400


def test_create_cookbook_fails_on_missing_type(auth, client):
    auth.login()
    test_data = {k: new_cb_dict[k] for k in ["year", "author", "title"]}
    response = client.post(
        "/api/1/books", json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400


def test_create_cookbook_fails_on_wrong_type(auth, client):
    auth.login()
    test_data = {**new_cb_dict, "type": "something stupid"}
    response = client.post(
        "/api/1/books", json=test_data, headers=auth.token_auth_header
    )

    assert response.status_code == 400


def test_create_cookbook_fails_on_missing_login(client):
    response = client.post("/api/1/books", json=new_cb_dict)

    assert response.status_code == 401


updated_dict = {"title": "t2", "year": 2020, "author": "c d", "type": "cookbook"}


def test_update_cookbook(books, auth, client):
    auth.login()

    response = client.put(
        "api/1/books/{}".format(books.book_1["id"]),
        json=updated_dict,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    data = response.json
    assert data["title"] == updated_dict["title"]
    assert data["year"] == updated_dict["year"]
    assert data["author"] == updated_dict["author"]
    assert data["type"] == books.book_1["type"]
    assert data["_links"] == books.book_1["_links"]


def test_update_magazine(books, auth, client):
    auth.login()
    updated_mag_dict = {**updated_dict, "type": "magazine", "issue": "newIss"}

    response = client.put(
        "api/1/books/{}".format(books.book_2["id"]),
        json=updated_mag_dict,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    data = response.json
    assert data["title"] == updated_mag_dict["title"]
    assert data["year"] == updated_mag_dict["year"]
    assert data["issue"] == updated_mag_dict["issue"]
    assert data["type"] == books.book_2["type"]
    assert data["_links"] == books.book_2["_links"]


def test_update_book_of_another_user_fails(books, auth, client):
    auth.login()

    response = client.put(
        "api/1/books/{}".format(books.book_3["id"]),
        json=updated_dict,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 404


def test_update_book_fails_on_not_existing_id(auth, client):
    auth.login()

    response = client.put(
        "api/1/books/{}".format(1234),
        json=updated_dict,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 404


def test_update_book_fails_on_missing_type(auth, client, books):
    auth.login()

    data = {**updated_dict}.pop("type")

    response = client.put(
        "api/1/books/{}".format(books.book_1["id"]),
        json=data,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 400


def test_update_book_fails_on_missing_title(auth, client, books):
    auth.login()

    data = {**updated_dict}.pop("title")

    response = client.put(
        "api/1/books/{}".format(books.book_1["id"]),
        json=data,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 400


def test_update_book_fails_on_wrong_type(auth, client, books):
    auth.login()

    data = {**updated_dict, "type": "blahblah"}

    response = client.put(
        "api/1/books/{}".format(books.book_1["id"]),
        json=data,
        headers=auth.token_auth_header,
    )

    assert response.status_code == 400


def test_delete_book(books, auth, app, client):
    auth.login()
    book_id = books.book_1["id"]

    response = client.delete(
        "api/1/books/{}".format(book_id), headers=auth.token_auth_header
    )

    assert response.status_code == 204

    with app.app_context():
        db_res = (
            db.session.execute(db.select(Book).filter_by(id=book_id))
            .scalars()
            .one_or_none()
        )

        assert db_res is None


def test_delete_book_of_another_user(books, auth, app, client):
    auth.login()
    book_id = books.book_3["id"]

    response = client.delete(
        "api/1/books/{}".format(book_id), headers=auth.token_auth_header
    )

    assert response.status_code == 404

    with app.app_context():
        db_res = (
            db.session.execute(db.select(Book).filter_by(id=book_id))
            .scalars()
            .one_or_none()
        )

        assert db_res is not None
