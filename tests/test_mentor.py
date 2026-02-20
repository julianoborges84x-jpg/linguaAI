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


def seed_languages(db_session):
    from app.models.language import Language

    db_session.add(Language(iso_code="por", name="Portuguese", region="Brazil", family="Indo-European"))
    db_session.add(Language(iso_code="eng", name="English", region="United States", family="Indo-European"))
    db_session.commit()


def test_mentor_free_writing_allowed(client, monkeypatch, db_session):
    seed_languages(db_session)
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "ok")

    res = register_user(client, "Lia", "lia@example.com", "secret123")
    assert res.status_code == 201
    user_id = res.json()["id"]

    res = client.patch(f"/users/{user_id}", json={"target_language_code": "eng"})
    assert res.status_code == 200

    login = login_user(client, "lia@example.com", "secret123")
    token = login.json()["access_token"]

    res = client.post(
        "/mentor/chat",
        headers=auth_header(token),
        json={"message": "teste", "feature": "writing"},
    )
    assert res.status_code == 200
    assert res.json()["reply"] == "ok"
    assert res.json()["ads"]


def test_mentor_free_speaking_blocked(client, monkeypatch, db_session):
    seed_languages(db_session)
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "ok")

    res = register_user(client, "Rui", "rui@example.com", "secret123")
    user_id = res.json()["id"]
    client.patch(f"/users/{user_id}", json={"target_language_code": "eng"})

    login = login_user(client, "rui@example.com", "secret123")
    token = login.json()["access_token"]

    res = client.post(
        "/mentor/chat",
        headers=auth_header(token),
        json={"message": "teste", "feature": "speaking"},
    )
    assert res.status_code == 403


def test_mentor_pro_speaking_allowed(client, monkeypatch, db_session):
    seed_languages(db_session)
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "ok")

    res = register_user(client, "Mia", "mia@example.com", "secret123")
    user_id = res.json()["id"]

    client.patch(f"/users/{user_id}", json={"plan": "PRO", "target_language_code": "eng"})

    login = login_user(client, "mia@example.com", "secret123")
    token = login.json()["access_token"]

    res = client.post(
        "/mentor/chat",
        headers=auth_header(token),
        json={"message": "teste", "feature": "speaking"},
    )
    assert res.status_code == 200
    assert res.json()["reply"] == "ok"
    assert res.json()["ads"] is None
