import io
import re


def test_put_image(client, auth, books, recipes, mocker):
    auth.login()

    mocker.patch("PIL.Image.open", spec=True).return_value.__enter__.return_value.format = "JPEG"
    mocker.patch("PIL.Image.Image.save")
    mocker.patch("PIL.Image.Image.thumbnail")
    mocker.patch("PIL.ImageOps.fit")
    mocker.patch("os.unlink")
        
    response = client.put(
        "/api/1/recipes/1/image",
        data={"image": (io.BytesIO(b"abcdef"), "test.jpg")},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    data = response.json

    assert "image" in data
    assert data["image"]
    assert re.compile(r"[a-z0-9]{32}.[a-z]{3,4}(.thumbnail)?").match(data["image"])
    assert data["_links"]["image"] == "/images/1/{}".format(data["image"])
    assert data["_links"]["thumbnail"] == "/images/1/{}.thumbnail".format(
        data["image"]
    )

def test_put_image_invalid_file_extension(client, auth, books, recipes, mocker):
    auth.login()

    mocker.patch("PIL.Image.open", spec=True).return_value.__enter__.return_value.format = "JPEG"
    mocker.patch("PIL.Image.Image.save")
    mocker.patch("PIL.Image.Image.thumbnail")
    mocker.patch("PIL.ImageOps.fit")
    mocker.patch("os.unlink")
        
    response = client.put(
        "/api/1/recipes/1/image",
        data={"image": (io.BytesIO(b"abcdef"), "test.txt")},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 400

def test_put_image_invalid_image_format(client, auth, books, recipes, mocker):
    auth.login()

    mocker.patch("PIL.Image.open", spec=True).return_value.__enter__.return_value.format = "TIF"
    mocker.patch("PIL.Image.Image.save")
    mocker.patch("PIL.Image.Image.thumbnail")
    mocker.patch("PIL.ImageOps.fit")
    mocker.patch("os.unlink")
        
    response = client.put(
        "/api/1/recipes/1/image",
        data={"image": (io.BytesIO(b"abcdef"), "test.jpg")},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 400

def test_put_image_not_authenticated(client, auth, books, recipes, mocker):
     
    response = client.put(
        "/api/1/recipes/1/image",
        data={"image": (io.BytesIO(b"abcdef"), "test.jpg")},
    )

    assert response.status_code == 401

def test_put_image_not_authorized(client, auth, books, recipes, mocker):
    auth.login()

    mocker.patch("PIL.Image.open", spec=True).return_value.__enter__.return_value.format = "JPEG"
    mocker.patch("PIL.Image.Image.save")
    mocker.patch("PIL.Image.Image.thumbnail")
    mocker.patch("PIL.ImageOps.fit")
    mocker.patch("os.unlink")
        
    # Recipe id: 6 belongs to user_2
    response = client.put(
        "/api/1/recipes/6/image",
        data={"image": (io.BytesIO(b"abcdef"), "test.jpg")},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 404

def test_put_image_not_found(client, auth, books, recipes, mocker):
    auth.login()

    mocker.patch("PIL.Image.open", spec=True).return_value.__enter__.return_value.format = "JPEG"
    mocker.patch("PIL.Image.Image.save")
    mocker.patch("PIL.Image.Image.thumbnail")
    mocker.patch("PIL.ImageOps.fit")
    mocker.patch("os.unlink")
        
    response = client.put(
        "/api/1/recipes/999/image",
        data={"image": (io.BytesIO(b"abcdef"), "test.jpg")},
        headers=auth.token_auth_header,
    )

    assert response.status_code == 404


def test_delete_image(client, auth, books, recipes, mocker):
    auth.login()
    mocker.patch("os.unlink")
    
    response = client.delete(
        "/api/1/recipes/1/image",
        headers=auth.token_auth_header,
    )

    assert response.status_code == 200
    data = response.json

    assert "image" in data
    assert data["image"] == None

def test_delete_image_not_authenticated(client, auth, books, recipes, mocker):
    mocker.patch("os.unlink")
    
    response = client.delete(
        "/api/1/recipes/1/image",
    )

    assert response.status_code == 401

def test_delete_image_not_authorized(client, auth, books, recipes, mocker):
    auth.login()
    mocker.patch("os.unlink")
    
    # Recipe id: 6 belongs to user_2
    response = client.delete(
        "/api/1/recipes/6/image",
        headers=auth.token_auth_header,
    )

    assert response.status_code == 404

def test_delete_image_not_found(client, auth, books, recipes, mocker):
    auth.login()
    mocker.patch("os.unlink")
    
    response = client.delete(
        "/api/1/recipes/999/image",
        headers=auth.token_auth_header,
    )

    assert response.status_code == 404
