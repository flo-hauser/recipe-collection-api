def test_config(app):
    assert app.testing == True


def test_client(client):
    assert str(type(client)) == "<class 'flask.testing.FlaskClient'>"


def test_healthy(client):
    response = client.get("api/1/healthy")
    assert response.status_code == 200
    assert response.json == {"healthy": True}
