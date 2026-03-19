from __future__ import annotations

from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.daily_challenge import DailyChallengeAttempt
from app.models.real_life import RealLifeSession, RealLifeTurn
from app.models.user import User
from app.services.analytics_service import track_event
from app.services.growth_service import update_streak
from app.services.progress_service import mark_daily_activity, recalculate_level, today_for_user
from app.services.real_life_service import SCENARIOS, start_real_life_session

SCENARIO_ROTATION = list(SCENARIOS.keys())


def _challenge_title_for_scenario(scenario: str) -> str:
    titles = {
        "restaurante": "Desafio Diario: Pedido no Restaurante",
        "aeroporto": "Desafio Diario: Check-in no Aeroporto",
        "entrevista de emprego": "Desafio Diario: Entrevista sob Pressao",
        "reuniao de trabalho": "Desafio Diario: Atualizacao de Reuniao",
        "date / conversa casual": "Desafio Diario: Conversa Casual Fluida",
        "emergencia": "Desafio Diario: Comunicacao em Emergencia",
    }
    return titles.get(scenario, "Desafio Diario")


def _scenario_for_day(day_date: date) -> str:
    return SCENARIO_ROTATION[day_date.toordinal() % len(SCENARIO_ROTATION)]


def _difficulty_for_user(user: User) -> int:
    base = 1 + max(0, (user.current_streak or 0) // 4)
    if (user.level or 0) >= 6:
        base += 1
    return min(5, max(1, base))


def _attempts_today(db: Session, user_id: int, day_date: date) -> int:
    return (
        db.query(func.count(DailyChallengeAttempt.id))
        .filter(DailyChallengeAttempt.user_id == user_id, DailyChallengeAttempt.day_date == day_date)
        .scalar()
        or 0
    )


def _best_score_today(db: Session, user_id: int, day_date: date) -> int:
    return (
        db.query(func.max(DailyChallengeAttempt.score))
        .filter(DailyChallengeAttempt.user_id == user_id, DailyChallengeAttempt.day_date == day_date)
        .scalar()
        or 0
    )


def get_daily_challenge(db: Session, user: User) -> dict:
    day_date = today_for_user(user)
    scenario = _scenario_for_day(day_date)
    attempts = _attempts_today(db, user.id, day_date)
    best_score = _best_score_today(db, user.id, day_date)
    badge = (
        db.query(DailyChallengeAttempt.id)
        .filter(
            DailyChallengeAttempt.user_id == user.id,
            DailyChallengeAttempt.day_date == day_date,
            DailyChallengeAttempt.badge_awarded.is_(True),
        )
        .first()
    )
    return {
        "day_date": day_date,
        "challenge_title": _challenge_title_for_scenario(scenario),
        "scenario": scenario,
        "difficulty_level": _difficulty_for_user(user),
        "attempts_today": attempts,
        "best_score_today": best_score,
        "can_play_without_penalty": attempts == 0,
        "daily_badge_earned": bool(badge),
    }


def start_daily_challenge(db: Session, user: User) -> dict:
    challenge_info = get_daily_challenge(db, user)
    attempts_today = challenge_info["attempts_today"]
    attempt_number = attempts_today + 1
    penalty_percent = max(0, (attempt_number - 1) * 15)

    real_life = start_real_life_session(db, user, scenario=challenge_info["scenario"])
    now = datetime.now(UTC).replace(tzinfo=None)
    attempt = DailyChallengeAttempt(
        user_id=user.id,
        day_date=challenge_info["day_date"],
        scenario=challenge_info["scenario"],
        challenge_title=challenge_info["challenge_title"],
        attempt_number=attempt_number,
        difficulty_level=challenge_info["difficulty_level"],
        real_life_session_id=real_life["session_id"],
        status="active",
        started_at=now,
    )
    db.add(attempt)
    track_event(
        db,
        "daily_challenge_started",
        user_id=user.id,
        payload={"challenge_title": attempt.challenge_title, "attempt_number": attempt_number, "scenario": attempt.scenario},
    )
    db.commit()
    db.refresh(attempt)

    return {
        "challenge_id": attempt.id,
        "day_date": attempt.day_date,
        "challenge_title": attempt.challenge_title,
        "scenario": attempt.scenario,
        "attempt_number": attempt.attempt_number,
        "penalty_percent": penalty_percent,
        "session_id": real_life["session_id"],
        "character_role": real_life["character_role"],
        "difficulty_level": real_life["difficulty_level"],
        "pressure_seconds": real_life["pressure_seconds"],
        "opening_message": real_life["opening_message"],
        "started_at": attempt.started_at,
    }


def _score_from_session(session: RealLifeSession, turns: list[RealLifeTurn], attempt_number: int, streak_active: bool) -> tuple[int, int, dict[str, int], bool]:
    if not turns:
        return 0, 0, {"speed": 0, "quality": 0, "errors": 0, "fluency": 0, "streak_bonus": 0, "first_try_bonus": 0, "penalty": 0}, False

    total_turns = len(turns)
    correct_turns = sum(1 for t in turns if t.is_correct == 1)
    avg_rt = sum(max(0, t.response_time_seconds) for t in turns) / max(1, total_turns)
    speed_score = max(0, min(25, int(25 - avg_rt / 2)))
    quality_score = int((correct_turns / max(1, total_turns)) * 35)
    errors_score = max(0, 20 - ((total_turns - correct_turns) * 4))
    fluency_score = max(0, min(20, int(session.total_score / max(1, total_turns))))
    streak_bonus = 8 if streak_active else 0
    first_try_bonus = 10 if attempt_number == 1 else 0
    penalty = max(0, (attempt_number - 1) * 10)
    final_score = max(0, min(100, speed_score + quality_score + errors_score + fluency_score + streak_bonus + first_try_bonus - penalty))

    xp = int(final_score * 0.8) + (10 if attempt_number == 1 else 0)
    badge_awarded = final_score >= 70 and attempt_number == 1
    return (
        final_score,
        xp,
        {
            "speed": speed_score,
            "quality": quality_score,
            "errors": errors_score,
            "fluency": fluency_score,
            "streak_bonus": streak_bonus,
            "first_try_bonus": first_try_bonus,
            "penalty": penalty,
        },
        badge_awarded,
    )


def submit_daily_challenge(db: Session, user: User, challenge_id: int) -> dict:
    challenge = (
        db.query(DailyChallengeAttempt)
        .filter(DailyChallengeAttempt.id == challenge_id, DailyChallengeAttempt.user_id == user.id)
        .first()
    )
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

    if challenge.status == "completed" and challenge.finished_at is not None:
        attempts = _attempts_today(db, user.id, challenge.day_date)
        best = _best_score_today(db, user.id, challenge.day_date)
        return {
            "challenge_id": challenge.id,
            "status": challenge.status,
            "score": challenge.score,
            "xp_awarded": challenge.xp_awarded,
            "bonus_breakdown": {"reused": 1},
            "badge_awarded": challenge.badge_awarded,
            "attempts_today": attempts,
            "best_score_today": best,
            "finished_at": challenge.finished_at,
        }

    if not challenge.real_life_session_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Challenge session missing")

    real_life_session = (
        db.query(RealLifeSession)
        .filter(RealLifeSession.id == challenge.real_life_session_id, RealLifeSession.user_id == user.id)
        .first()
    )
    if not real_life_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Real life session not found")

    turns = (
        db.query(RealLifeTurn)
        .filter(RealLifeTurn.session_id == real_life_session.id)
        .order_by(RealLifeTurn.id.asc())
        .all()
    )
    score, xp, bonus_breakdown, badge_awarded = _score_from_session(
        real_life_session,
        turns,
        challenge.attempt_number,
        streak_active=(user.current_streak or 0) > 0,
    )

    challenge.status = "completed"
    challenge.score = score
    challenge.xp_awarded = xp
    challenge.penalty_applied = bonus_breakdown.get("penalty", 0)
    challenge.badge_awarded = badge_awarded
    challenge.finished_at = datetime.now(UTC).replace(tzinfo=None)
    real_life_session.status = "completed"
    real_life_session.completed_at = challenge.finished_at

    user.xp_total = max(0, (user.xp_total or 0) + xp)
    user.level = recalculate_level(user.xp_total)
    active_day = today_for_user(user)
    mark_daily_activity(db, user.id, active_day)
    update_streak(user, active_day)

    track_event(
        db,
        "daily_challenge_completed",
        user_id=user.id,
        payload={"challenge_id": challenge.id, "score": score, "xp_awarded": xp, "attempt_number": challenge.attempt_number},
    )
    track_event(
        db,
        "daily_challenge_score",
        user_id=user.id,
        payload={"challenge_id": challenge.id, "score": score},
    )

    db.commit()
    db.refresh(challenge)
    attempts = _attempts_today(db, user.id, challenge.day_date)
    best = _best_score_today(db, user.id, challenge.day_date)
    return {
        "challenge_id": challenge.id,
        "status": challenge.status,
        "score": challenge.score,
        "xp_awarded": challenge.xp_awarded,
        "bonus_breakdown": bonus_breakdown,
        "badge_awarded": challenge.badge_awarded,
        "attempts_today": attempts,
        "best_score_today": best,
        "finished_at": challenge.finished_at,
    }
