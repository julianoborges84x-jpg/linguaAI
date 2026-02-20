from datetime import date, timedelta
from app.models.daily_message import DailyMessage
from app.services import motivation


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


def seed_quotes(db_session):
    from app.models.motivational_quote import MotivationalQuote

    db_session.add(MotivationalQuote(text="Q1", category="level_up"))
    db_session.add(MotivationalQuote(text="Q2", category="exercise"))
    db_session.add(MotivationalQuote(text="Q3", category="streak"))
    db_session.commit()


def test_level_up_quote(client, db_session, monkeypatch):
    seed_quotes(db_session)
    monkeypatch.setattr(motivation, "seed_quotes_if_empty", lambda db: None)

    res = register_user(client, "Leo", "leo@example.com", "secret123")
    assert res.status_code == 201

    login = login_user(client, "leo@example.com", "secret123")
    token = login.json()["access_token"]

    res = client.post(
        "/motivation/event",
        headers=auth_header(token),
        json={"type": "level_up", "new_level": 1},
    )
    assert res.status_code == 200
    assert res.json()["quote"] == "Q1"


def test_streak_quote(client, db_session, monkeypatch):
    seed_quotes(db_session)
    monkeypatch.setattr(motivation, "seed_quotes_if_empty", lambda db: None)

    res = register_user(client, "Nico", "nico@example.com", "secret123")
    user_id = res.json()["id"]

    today = date.today()
    for i in range(5):
        db_session.add(
            DailyMessage(
                user_id=user_id,
                day=today - timedelta(days=i),
                passage_id=str(i),
                reference="Ref",
                text="Text",
            )
        )
    db_session.commit()

    login = login_user(client, "nico@example.com", "secret123")
    token = login.json()["access_token"]

    res = client.post(
        "/motivation/event",
        headers=auth_header(token),
        json={"type": "streak_check"},
    )
    assert res.status_code == 200
    assert res.json()["quote"] == "Q3"
