def register_user(client, name, email, password):
    return client.post(
        "/users",
        json={"name": name, "email": email, "password": password},
    )


def login_user(client, email, password):
    return client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )


def test_register_and_login_with_short_password(client):
    password = "123"
    register = register_user(client, "Short Pass", "short-pass@example.com", password)
    assert register.status_code == 201

    login = login_user(client, "short-pass@example.com", password)
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_register_and_login_with_long_password(client):
    password = "a" * 220
    register = register_user(client, "Long Pass", "long-pass@example.com", password)
    assert register.status_code == 201

    login = login_user(client, "long-pass@example.com", password)
    assert login.status_code == 200
    assert login.json()["access_token"]
