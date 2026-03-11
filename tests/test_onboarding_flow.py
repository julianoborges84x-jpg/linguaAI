def _create_user(client, email="first-setup@example.com", password="123"):
    response = client.post(
        "/users",
        json={"name": "First Setup User", "email": email, "password": password},
    )
    assert response.status_code == 201
    return response.json()


def _auth_headers(client, email, password="123"):
    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_new_user_has_onboarding_completed_false(client):
    email = "onboarding-new@example.com"
    _create_user(client, email=email)
    headers = _auth_headers(client, email)

    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["onboarding_completed"] is False


def test_patch_onboarding_valid_payload_marks_completed(client):
    email = "onboarding-valid@example.com"
    _create_user(client, email=email)
    headers = _auth_headers(client, email)

    response = client.patch(
        "/users/me/onboarding",
        headers=headers,
        json={"target_language": "en", "timezone": "America/Sao_Paulo"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["target_language"] == "en"
    assert payload["timezone"] == "America/Sao_Paulo"
    assert payload["onboarding_completed"] is True


def test_patch_onboarding_invalid_language_returns_422(client):
    email = "onboarding-invalid-lang@example.com"
    _create_user(client, email=email)
    headers = _auth_headers(client, email)

    response = client.patch(
        "/users/me/onboarding",
        headers=headers,
        json={"target_language": "de", "timezone": "America/Sao_Paulo"},
    )
    assert response.status_code == 422


def test_patch_onboarding_without_token_returns_401(client):
    response = client.patch(
        "/users/me/onboarding",
        json={"target_language": "en", "timezone": "America/Sao_Paulo"},
    )
    assert response.status_code == 401
