from base64 import b64encode
from datetime import datetime
from app import db
from app.models.user import User

username, password = ("admin", "admin")
admin_credentials = b64encode(b"admin:admin").decode("utf-8")


def test_get_token(client):
    response = client.get(
        "/api/1/tokens",
        headers={"Authorization": "Basic {}".format(admin_credentials)},
    )

    assert response.status_code == 200

    data = response.json
    assert "token" in data
    d = datetime.strptime(data["token_expiration"], "%a, %d %b %Y %H:%M:%S %Z")
    assert type(d) == datetime
    assert data["token_lifetime"] > 3500


def test_get_token_fails_on_wrong_password(client):
    wrong_credentials = b64encode(b"admin:wrong").decode("utf-8")

    response = client.get(
        "/api/1/tokens",
        headers={"Authorization": "Basic {}".format(wrong_credentials)},
    )

    assert response.status_code == 401


def test_revoke_token(app, client):
    response = client.get(
        "/api/1/tokens",
        headers={"Authorization": "Basic {}".format(admin_credentials)},
    )

    token = response.json["token"]

    with app.app_context():
        user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one()

        lifetime = user.get_token_lifetime()
        exp = user.token_expiration

    response = client.delete(
        "/api/1/tokens", headers={"Authorization": "Bearer {}".format(token)}
    )
    assert response.status_code == 204

    with app.app_context():
        assert User.check_token(token) is None
