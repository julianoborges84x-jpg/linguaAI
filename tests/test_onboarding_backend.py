def _create_user_and_token(client, email="onboarding-test@example.com", password="123"):
    created = client.post(
        "/users",
        json={"name": "Onboarding User", "email": email, "password": password},
    )
    assert created.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_patch_users_me_with_full_payload_ok(client):
    headers = _create_user_and_token(client, "partial-ok@example.com")

    response = client.patch(
        "/users/me",
        headers=headers,
        json={"target_language": "en", "timezone": "America/Sao_Paulo"},
    )
    assert response.status_code == 200
    assert response.json()["target_language"] == "en"


def test_get_users_me_returns_null_before_onboarding(client):
    headers = _create_user_and_token(client, "null-before@example.com")

    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["target_language"] is None


def test_patch_users_me_requires_timezone(client):
    headers = _create_user_and_token(client, "no-timezone@example.com")

    response = client.patch(
        "/users/me",
        headers=headers,
        json={"target_language": "fr"},
    )
    assert response.status_code == 422


def test_unauthorized_users_me(client):
    response = client.get("/users/me")
    assert response.status_code == 401
