from app.services import llm_client


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


def test_mentor_chat_fallback_target_language_when_missing(client, monkeypatch):
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "ok")

    res = register_user(client, "NoLang", "nolang@example.com", "secret123")
    assert res.status_code == 201

    login = login_user(client, "nolang@example.com", "secret123")
    token = login.json()["access_token"]

    res = client.post(
        "/mentor/chat",
        headers=auth_header(token),
        json={"message": "hello", "feature": "writing"},
    )
    assert res.status_code == 200
    assert res.json()["reply"] == "ok"


def test_mentor_chat_returns_pedagogical_payload(client, monkeypatch, db_session):
    seed_languages(db_session)
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "Good progress!")

    res = register_user(client, "PedChat", "ped_chat@example.com", "secret123")
    assert res.status_code == 201
    user_id = res.json()["id"]
    client.patch(f"/users/{user_id}", json={"target_language_code": "eng"})

    token = login_user(client, "ped_chat@example.com", "secret123").json()["access_token"]
    chat = client.post(
        "/mentor/chat",
        headers=auth_header(token),
        json={"message": "I goed yesterday", "feature": "writing"},
    )
    assert chat.status_code == 200
    payload = chat.json()
    assert payload["message"] == "Good progress!"
    assert payload["reply"] == "Good progress!"
    assert payload["correction"] is not None
    assert payload["explanation"] is not None
    assert "tense" in payload["detected_errors"]
    assert "recommendation" in payload


def test_mentor_chat_llm_fallback_returns_useful_response(client, monkeypatch, db_session):
    seed_languages(db_session)

    def raise_llm_error(instructions, input_text):
        raise llm_client.LLMServiceError("Nao foi possivel conectar ao servico de IA em http://localhost:8010.")

    monkeypatch.setattr(llm_client, "generate_reply", raise_llm_error)

    res = register_user(client, "Fallback", "fallback_chat@example.com", "secret123")
    assert res.status_code == 201
    user_id = res.json()["id"]
    client.patch(f"/users/{user_id}", json={"target_language_code": "eng"})
    token = login_user(client, "fallback_chat@example.com", "secret123").json()["access_token"]

    chat = client.post(
        "/mentor/chat",
        headers=auth_header(token),
        json={"message": "hello mentor", "feature": "writing"},
    )
    assert chat.status_code == 200
    payload = chat.json()
    assert payload["fallback_reason"] is not None
    assert "instabilidade" in payload["reply"].lower()


def test_voice_mentor_free_allows_until_limit_then_blocks(client, monkeypatch, db_session):
    seed_languages(db_session)
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "voz-ok")

    res = register_user(client, "FreeVoice", "free_voice@example.com", "secret123")
    assert res.status_code == 201
    user_id = res.json()["id"]
    client.patch(f"/users/{user_id}", json={"target_language_code": "eng"})

    login = login_user(client, "free_voice@example.com", "secret123")
    token = login.json()["access_token"]

    mentors = client.get("/mentor/voice/mentors", headers=auth_header(token))
    assert mentors.status_code == 200
    assert len(mentors.json()) >= 1

    usage = client.get("/mentor/voice/usage", headers=auth_header(token))
    assert usage.status_code == 200
    assert usage.json()["plan"] == "FREE"
    assert usage.json()["used"] == 0
    assert usage.json()["limit"] == 6
    assert usage.json()["blocked"] is False

    for _ in range(6):
        chat = client.post(
            "/mentor/voice/chat",
            headers=auth_header(token),
            json={"mentor_id": "clara", "message": "hello"},
        )
        assert chat.status_code == 200

    blocked = client.post(
        "/mentor/voice/chat",
        headers=auth_header(token),
        json={"mentor_id": "clara", "message": "hello again"},
    )
    assert blocked.status_code == 403
    assert blocked.json()["detail"] == "🔒 Você atingiu o limite gratuito. Desbloqueie o PRO para continuar falando com seu mentor."


def test_voice_mentor_pro_access_and_chat(client, monkeypatch, db_session):
    seed_languages(db_session)
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "reply-by-voice")

    res = register_user(client, "ProVoice", "pro_voice@example.com", "secret123")
    assert res.status_code == 201
    user_id = res.json()["id"]
    patch = client.patch(f"/users/{user_id}", json={"plan": "PRO", "target_language_code": "eng"})
    assert patch.status_code == 200

    login = login_user(client, "pro_voice@example.com", "secret123")
    token = login.json()["access_token"]

    mentors = client.get("/mentor/voice/mentors", headers=auth_header(token))
    assert mentors.status_code == 200
    assert len(mentors.json()) >= 4
    assert any(item["id"] == "maya" for item in mentors.json())

    chat = client.post(
        "/mentor/voice/chat",
        headers=auth_header(token),
        json={"mentor_id": "maya", "message": "i need help"},
    )
    assert chat.status_code == 200
    assert chat.json()["mentor_id"] == "maya"
    assert chat.json()["reply"] == "reply-by-voice"
    assert chat.json()["audio_available"] is True
    assert chat.json()["voice_usage"]["plan"] == "PRO"
    assert chat.json()["voice_usage"]["limit"] is None


def test_voice_mentor_pro_is_unlimited(client, monkeypatch, db_session):
    seed_languages(db_session)
    monkeypatch.setattr(llm_client, "generate_reply", lambda instructions, input_text: "reply-by-voice")

    res = register_user(client, "ProMax", "pro_max@example.com", "secret123")
    assert res.status_code == 201
    user_id = res.json()["id"]
    patch = client.patch(f"/users/{user_id}", json={"plan": "PRO", "target_language_code": "eng"})
    assert patch.status_code == 200

    login = login_user(client, "pro_max@example.com", "secret123")
    token = login.json()["access_token"]

    for idx in range(8):
        chat = client.post(
            "/mentor/voice/chat",
            headers=auth_header(token),
            json={"mentor_id": "maya", "message": f"turn {idx}"},
        )
        assert chat.status_code == 200


def test_voice_mentor_returns_useful_llm_error(client, monkeypatch, db_session):
    seed_languages(db_session)

    def raise_llm_error(instructions, input_text):
        raise llm_client.LLMServiceError("Nao foi possivel conectar ao servico de IA. Verifique o LLM_SERVICE_URL.")

    monkeypatch.setattr(llm_client, "generate_reply", raise_llm_error)

    res = register_user(client, "LlmErr", "llm_err@example.com", "secret123")
    assert res.status_code == 201
    user_id = res.json()["id"]
    client.patch(f"/users/{user_id}", json={"target_language_code": "eng"})

    login = login_user(client, "llm_err@example.com", "secret123")
    token = login.json()["access_token"]

    chat = client.post(
        "/mentor/voice/chat",
        headers=auth_header(token),
        json={"mentor_id": "clara", "message": "hello"},
    )
    assert chat.status_code == 200
    payload = chat.json()
    assert payload["audio_available"] is False
    assert "indisponibilidade temporaria" in payload["reply"].lower()
