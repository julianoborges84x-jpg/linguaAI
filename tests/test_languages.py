from app.services import llm_client


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


def test_language_selection_and_detection(client, monkeypatch, db_session):
    from app.models.language import Language

    db_session.add(Language(iso_code="por", name="Portuguese", region="Brazil", family="Indo-European"))
    db_session.add(Language(iso_code="eng", name="English", region="United States", family="Indo-European"))
    db_session.commit()

    monkeypatch.setattr(llm_client, "detect_language", lambda text: "por")
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "ok")

    res = register_user(client, "Tia", "tia@example.com", "secret123")
    user_id = res.json()["id"]

    res = client.patch(f"/users/{user_id}", json={"target_language_code": "eng"})
    assert res.status_code == 200

    login = login_user(client, "tia@example.com", "secret123")
    token = login.json()["access_token"]

    res = client.post(
        "/mentor/detect-language",
        headers=auth_header(token),
        json={"text": "Olá, tudo bem?"},
    )
    assert res.status_code == 200
    assert res.json()["iso_code"] == "por"

    res = client.post(
        "/mentor/chat",
        headers=auth_header(token),
        json={"message": "hello", "feature": "writing"},
    )
    assert res.status_code == 200
