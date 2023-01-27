from base64 import b64encode
from app.models.user import User


class AuthActions:
    def __init__(self, app, client):
        self._app = app
        self._client = client
        self.token = ""
        self.user = None
        self._headers = {"basic": {}, "token": {}}

    def login(self, username="user_1", password="pass_1"):
        self._create_basic_auth_headers(username, password)
        response = self._client.get("/api/1/tokens", headers=self.basic_auth_header)

        self.token = response.json["token"]
        self._create_token_auth_headers(self.token)

        with self._app.app_context():
            self.user = User.check_token(self.token)

        return response

    def logout(self):
        response = self._client.delete("/api/1/tokens", headers=self.token_auth_header)
        self.token = ""
        self.user = None
        self._headers = {"basic": {}, "token": {}}

        return response

    def _create_basic_auth_headers(self, username, password):
        cr_str = "{username}:{password}".format(username=username, password=password)
        credentials = b64encode(bytes(cr_str, "utf-8")).decode("utf-8")
        self._headers["basic"] = {"Authorization": "Basic {}".format(credentials)}

    def _create_token_auth_headers(self, token):
        self._headers["token"] = {"Authorization": "Bearer {}".format(self.token)}

    @property
    def basic_auth_header(self):
        return self._headers["basic"]

    @property
    def token_auth_header(self):
        return self._headers["token"]
