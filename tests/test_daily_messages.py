from app.services import daily_messages


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


def test_daily_message_same_day(client, monkeypatch):
    monkeypatch.setattr(daily_messages, "today_for_timezone", lambda tz: __import__("datetime").date(2024, 1, 1))
    monkeypatch.setattr(
        daily_messages,
        "load_passages",
        lambda: [
            {"id": "a", "reference": "Ref A", "text": "Text A"},
            {"id": "b", "reference": "Ref B", "text": "Text B"},
        ],
    )

    res = register_user(client, "Nina", "nina@example.com", "secret123")
    assert res.status_code == 201
    user_id = res.json()["id"]
    client.patch(f"/users/{user_id}", json={"timezone": "America/Sao_Paulo"})

    login = login_user(client, "nina@example.com", "secret123")
    token = login.json()["access_token"]

    res1 = client.get("/daily-message/today", headers=auth_header(token))
    assert res1.status_code == 200

    res2 = client.get("/daily-message/today", headers=auth_header(token))
    assert res2.status_code == 200

    assert res1.json() == res2.json()
