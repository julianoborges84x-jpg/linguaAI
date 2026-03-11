def create_user_and_headers(client, email="learna@example.com", password="123", plan="FREE"):
    reg = client.post("/users", json={"name": "Learna", "email": email, "password": password})
    assert reg.status_code == 201
    if plan == "PRO":
        user_id = reg.json()["id"]
        promote = client.patch(f"/users/{user_id}", json={"plan": "PRO"})
        assert promote.status_code == 200
    login = client.post("/auth/login", data={"username": email, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_topics_endpoint_requires_pro(client):
    free_headers = create_user_and_headers(client, "topics-free@example.com")
    free_res = client.get("/topics", headers=free_headers)
    assert free_res.status_code == 403

    headers = create_user_and_headers(client, "topics-pro@example.com", plan="PRO")
    res = client.get("/topics", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 4


def test_vocabulary_endpoint(client):
    headers = create_user_and_headers(client, "vocabulary@example.com")
    res = client.get("/vocabulary", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
    assert len(res.json()) >= 1


def test_chat_saves_history(client):
    free_headers = create_user_and_headers(client, "chat-save-free@example.com")
    free_chat = client.post("/chat", headers=free_headers, json={"message": "i like travel"})
    assert free_chat.status_code == 403

    headers = create_user_and_headers(client, "chat-save@example.com", plan="PRO")
    chat = client.post("/chat", headers=headers, json={"message": "i like travel"})
    assert chat.status_code == 200
    payload = chat.json()
    assert "correction" in payload
    assert "explanation" in payload
    assert "corrected_text" in payload

    history = client.get("/history", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) >= 1


def test_progress_get_and_patch(client):
    headers = create_user_and_headers(client, "progress@example.com")
    res = client.get("/progress", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert {"streak", "hours_spoken", "words_learned"}.issubset(body.keys())

    updated = client.patch("/progress", headers=headers, json={"streak": 3, "hours_spoken": 2.5, "words_learned": 20})
    assert updated.status_code == 200
    assert updated.json()["streak"] == 3
    assert updated.json()["hours_spoken"] == 2.5
    assert updated.json()["words_learned"] == 20
