def _create_user_and_token(client, email="prefs@example.com", password="123"):
    created = client.post(
        "/users",
        json={"name": "Prefs User", "email": email, "password": password},
    )
    assert created.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_update_language_success(client):
    headers = _create_user_and_token(client, "prefs-language@example.com")

    response = client.patch(
        "/users/me",
        headers=headers,
        json={"target_language": "en", "timezone": "America/Sao_Paulo"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["target_language"] == "en"
    assert payload["onboarding_completed"] is True


def test_update_timezone_success(client):
    headers = _create_user_and_token(client, "prefs-timezone@example.com")

    response = client.patch(
        "/users/me",
        headers=headers,
        json={"target_language": "es", "timezone": "Europe/Madrid"},
    )

    assert response.status_code == 200
    assert response.json()["timezone"] == "Europe/Madrid"


def test_update_preferences_without_token_returns_401(client):
    response = client.patch(
        "/users/me",
        json={"target_language": "fr", "timezone": "Europe/Paris"},
    )
    assert response.status_code == 401


def test_update_preferences_invalid_payload_returns_422(client):
    headers = _create_user_and_token(client, "prefs-invalid@example.com")

    response = client.patch(
        "/users/me",
        headers=headers,
        json={"target_language": "de", "timezone": ""},
    )
    assert response.status_code == 422
