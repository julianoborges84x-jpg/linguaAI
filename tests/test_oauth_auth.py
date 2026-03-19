from urllib.parse import parse_qs, urlparse
import importlib

from app.core.config import settings

auth_route = importlib.import_module("app.api.routes.auth")


class FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeHttpClient:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, data=None, **kwargs):
        if "oauth2.googleapis.com/token" in url:
            return FakeResponse(200, {"access_token": "google-token"})
        if "appleid.apple.com/auth/token" in url:
            return FakeResponse(200, {"id_token": "apple-id-token"})
        raise AssertionError(f"Unexpected POST url: {url}")

    def get(self, url, headers=None, **kwargs):
        if "googleapis.com/oauth2/v3/userinfo" in url:
            return FakeResponse(200, {"email": "google_user@example.com", "name": "Google User", "sub": "google-sub-1"})
        raise AssertionError(f"Unexpected GET url: {url}")


def _extract_state_from_redirect(response) -> str:
    location = response.headers["location"]
    parsed = urlparse(location)
    return parse_qs(parsed.query).get("state", [""])[0]


def test_google_oauth_creates_user_and_logs_in(client, monkeypatch):
    settings.oauth_google_client_id = "google-client"
    settings.oauth_google_client_secret = "google-secret"

    monkeypatch.setattr(auth_route.httpx, "Client", lambda timeout=15.0: FakeHttpClient())

    start = client.get("/auth/oauth/google/start", follow_redirects=False)
    assert start.status_code == 307
    state = _extract_state_from_redirect(start)
    assert state

    callback = client.post("/auth/oauth/google/callback", json={"code": "valid-code", "state": state})
    assert callback.status_code == 200
    payload = callback.json()
    assert payload["access_token"]
    assert payload["user"]["email"] == "google_user@example.com"
    assert payload["user"]["google_sub"] == "google-sub-1"


def test_google_oauth_logs_existing_user(client, monkeypatch):
    settings.oauth_google_client_id = "google-client"
    settings.oauth_google_client_secret = "google-secret"

    register = client.post("/users", json={"name": "Existing", "email": "google_user@example.com", "password": "secret123"})
    assert register.status_code == 201

    monkeypatch.setattr(auth_route.httpx, "Client", lambda timeout=15.0: FakeHttpClient())

    start = client.get("/auth/oauth/google/start", follow_redirects=False)
    state = _extract_state_from_redirect(start)

    callback = client.post("/auth/oauth/google/callback", json={"code": "valid-code", "state": state})
    assert callback.status_code == 200
    payload = callback.json()
    assert payload["user"]["email"] == "google_user@example.com"


def test_apple_oauth_returns_error_when_no_email_and_unknown_sub(client, monkeypatch):
    settings.oauth_apple_client_id = "apple-client"
    settings.oauth_apple_team_id = "apple-team"
    settings.oauth_apple_key_id = "apple-key"
    settings.oauth_apple_private_key = "-----BEGIN PRIVATE KEY-----\\nFAKE\\n-----END PRIVATE KEY-----"

    monkeypatch.setattr(auth_route, "_build_apple_client_secret", lambda: "apple-secret")
    monkeypatch.setattr(auth_route.httpx, "Client", lambda timeout=15.0: FakeHttpClient())
    monkeypatch.setattr(auth_route.jwt, "get_unverified_claims", lambda token: {"sub": "apple-sub-1"})

    start = client.get("/auth/oauth/apple/start", follow_redirects=False)
    assert start.status_code == 307
    state = _extract_state_from_redirect(start)

    callback = client.post("/auth/oauth/apple/callback", json={"code": "valid-code", "state": state})
    assert callback.status_code == 422
    assert "sem e-mail" in callback.json()["detail"]
