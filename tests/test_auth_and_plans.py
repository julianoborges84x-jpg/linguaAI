
def register_user(client, name, email, password):
    return client.post(
        "/users",
        json={"name": name, "email": email, "password": password},
    )


def login_user(client, email, password):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    res = register_user(client, "Ana", "ana@example.com", "secret123")
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Ana"
    assert data["email"] == "ana@example.com"
    assert data["plan"] == "FREE"
    assert data["level"] == 0

    res = login_user(client, "ana@example.com", "secret123")
    assert res.status_code == 200
    token = res.json()["access_token"]
    assert token


def test_feature_access_by_plan(client):
    res = register_user(client, "Bob", "bob@example.com", "secret123")
    user_id = res.json()["id"]

    login = login_user(client, "bob@example.com", "secret123")
    token = login.json()["access_token"]

    res = client.get("/features/writing", headers=auth_header(token))
    assert res.status_code == 200

    res = client.get("/features/speaking", headers=auth_header(token))
    assert res.status_code == 403

    res = client.get("/features/ads", headers=auth_header(token))
    assert res.status_code == 200

    res = client.patch(f"/users/{user_id}", json={"plan": "PRO"})
    assert res.status_code == 200

    login = login_user(client, "bob@example.com", "secret123")
    token = login.json()["access_token"]

    res = client.get("/features/speaking", headers=auth_header(token))
    assert res.status_code == 200

    res = client.get("/features/dialect", headers=auth_header(token))
    assert res.status_code == 200

    res = client.get("/features/fillers", headers=auth_header(token))
    assert res.status_code == 200

    res = client.get("/features/ads", headers=auth_header(token))
    assert res.status_code == 403


def test_missing_token(client):
    res = client.get("/features/writing")
    assert res.status_code == 401
