from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.real_life import RealLifeSession, RealLifeTurn
from app.models.user import User
from app.services.analytics_service import track_event
from app.services.progress_service import recalculate_level

SCENARIOS = {
    "restaurante": {
        "role": "Garcom",
        "opening": "Boa noite. Posso anotar seu pedido agora?",
        "questions": [
            "Perfeito. Qual prato principal voce quer hoje?",
            "Quer bebida com gelo ou sem gelo?",
            "Deseja sobremesa tambem?",
            "Tudo bem, mas preciso confirmar: mesa para quantas pessoas?",
        ],
    },
    "aeroporto": {
        "role": "Atendente de Check-in",
        "opening": "Passaporte e destino, por favor. Precisamos agilizar a fila.",
        "questions": [
            "Voce tem bagagem para despachar?",
            "Prefere assento na janela ou corredor?",
            "Seu voo conecta em outra cidade?",
            "Seu embarque fecha em 20 minutos, voce consegue chegar no portao?",
        ],
    },
    "entrevista de emprego": {
        "role": "Recrutador",
        "opening": "Vamos direto ao ponto: fale sobre seu ultimo projeto.",
        "questions": [
            "Qual impacto concreto voce gerou?",
            "Como voce lida com conflito no time?",
            "Por que deveriamos contratar voce?",
            "Tem disponibilidade para comecar em 2 semanas?",
        ],
    },
    "reuniao de trabalho": {
        "role": "Lider de Reuniao",
        "opening": "Estamos atrasados. Me atualize em 30 segundos.",
        "questions": [
            "Qual bloqueio principal impede a entrega?",
            "Qual seu plano para recuperar o cronograma?",
            "Quem precisa ser envolvido para destravar isso hoje?",
            "Voce confirma o prazo final para sexta-feira?",
        ],
    },
    "date / conversa casual": {
        "role": "Pessoa no encontro",
        "opening": "Oi! Conta algo divertido sobre sua semana.",
        "questions": [
            "Que tipo de viagem voce mais gosta?",
            "Qual foi seu ultimo filme favorito e por que?",
            "Como seria seu fim de semana ideal?",
            "Vamos marcar outro encontro?",
        ],
    },
    "emergencia": {
        "role": "Atendente de Emergencia",
        "opening": "Estou ouvindo. O que aconteceu e onde voce esta?",
        "questions": [
            "A pessoa esta consciente agora?",
            "Tem algum sangramento intenso?",
            "Consegue descrever o local com um ponto de referencia?",
            "Voce consegue manter a linha enquanto a equipe chega?",
        ],
    },
}


def _normalize_scenario(scenario: str) -> str:
    normalized = scenario.strip().lower()
    if normalized not in SCENARIOS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported scenario",
        )
    return normalized


def _starting_difficulty(user: User) -> int:
    if (user.level or 0) >= 6:
        return 3
    if (user.level or 0) >= 3:
        return 2
    return 1


def _pressure_for_level(level: int) -> int:
    return {1: 35, 2: 25, 3: 18, 4: 14, 5: 10}.get(level, 10)


def _next_question(session: RealLifeSession) -> str:
    config = SCENARIOS[session.scenario]
    questions = config["questions"]
    index = session.turns_count % len(questions)
    return questions[index]


def _evaluate_message(message: str, response_time_seconds: int, pressure_seconds: int) -> tuple[bool, str, str]:
    text = message.strip()
    words = [w for w in text.split() if w]
    is_long_enough = len(words) >= 5
    has_polite_form = any(token in text.lower() for token in ("could", "would", "please", "i'd", "can i"))
    is_correct = is_long_enough and has_polite_form

    if is_correct:
        correction = "Boa estrutura. Sua mensagem ficou natural para uma situacao real."
    elif is_long_enough:
        correction = "Sua resposta foi compreensivel, mas faltou naturalidade. Use formas mais educadas."
    else:
        correction = "Resposta curta demais para o contexto. Amplie com objetivo e detalhe."

    better_response = "I'd like to order now, please. Could you also recommend a drink?"
    pressure_note = "Voce respondeu dentro do tempo." if response_time_seconds <= pressure_seconds else "Resposta lenta: tente ser mais direto sob pressao."
    return is_correct, correction, pressure_note


def _bonus_xp(is_correct: bool, response_time_seconds: int, pressure_seconds: int, consecutive_correct: int) -> tuple[int, dict[str, int]]:
    base = 12
    quick = 8 if response_time_seconds <= pressure_seconds else 0
    correct = 10 if is_correct else 0
    streak = min(10, max(0, consecutive_correct) * 2)
    total = base + quick + correct + streak
    return total, {"base": base, "quick": quick, "correct": correct, "streak": streak}


def start_real_life_session(db: Session, user: User, scenario: str, retry_session_id: int | None = None) -> dict:
    normalized = _normalize_scenario(scenario)
    cfg = SCENARIOS[normalized]
    difficulty = _starting_difficulty(user)

    session = RealLifeSession(
        user_id=user.id,
        scenario=normalized,
        character_role=cfg["role"],
        difficulty_level=difficulty,
        pressure_seconds=_pressure_for_level(difficulty),
        status="active",
    )
    db.add(session)

    track_event(
        db,
        "real_life_started",
        user_id=user.id,
        payload={"scenario": normalized, "difficulty_level": difficulty},
    )
    if retry_session_id is not None:
        track_event(
            db,
            "real_life_retry",
            user_id=user.id,
            payload={"retry_session_id": retry_session_id, "scenario": normalized},
        )

    db.commit()
    db.refresh(session)
    return {
        "session_id": session.id,
        "scenario": session.scenario,
        "character_role": session.character_role,
        "difficulty_level": session.difficulty_level,
        "pressure_seconds": session.pressure_seconds,
        "opening_message": cfg["opening"],
    }


def send_real_life_message(db: Session, user: User, session_id: int, message: str, response_time_seconds: int | None = None) -> dict:
    session = (
        db.query(RealLifeSession)
        .filter(RealLifeSession.id == session_id, RealLifeSession.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session is not active")

    clean_message = message.strip()
    if not clean_message:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Message cannot be empty")

    rt = max(0, response_time_seconds or session.pressure_seconds + 1)
    is_correct, correction, pressure_note = _evaluate_message(clean_message, rt, session.pressure_seconds)

    if is_correct:
        session.consecutive_correct = max(0, session.consecutive_correct + 1)
    else:
        session.consecutive_correct = 0

    xp, bonus = _bonus_xp(is_correct, rt, session.pressure_seconds, session.consecutive_correct)
    session.total_xp = max(0, session.total_xp + xp)
    session.total_score = max(0, session.total_score + (15 if is_correct else 5))
    session.turns_count = max(0, session.turns_count + 1)

    if session.consecutive_correct >= 3:
        session.difficulty_level = min(5, session.difficulty_level + 1)
    elif not is_correct and session.difficulty_level > 1:
        session.difficulty_level = max(1, session.difficulty_level - 1)
    session.pressure_seconds = _pressure_for_level(session.difficulty_level)

    status_now = "active"
    if rt > session.pressure_seconds * 2:
        status_now = "failed"
    elif session.turns_count >= 6 and session.consecutive_correct >= 2:
        status_now = "completed"

    if status_now != "active":
        session.status = status_now
        session.completed_at = datetime.now(UTC).replace(tzinfo=None)
        track_event(
            db,
            f"real_life_{status_now}",
            user_id=user.id,
            payload={"session_id": session.id, "scenario": session.scenario, "total_xp": session.total_xp},
        )

    session.updated_at = datetime.now(UTC).replace(tzinfo=None)

    user.xp_total = max(0, (user.xp_total or 0) + xp)
    user.level = recalculate_level(user.xp_total)

    next_question = _next_question(session)
    if rt > session.pressure_seconds:
        next_question = f"Rapido: {next_question}"

    feedback = {
        "correction": correction,
        "better_response": "I'd like to order now, please. Could you also recommend a drink?",
        "pressure_note": pressure_note,
        "level_adaptation": f"Nivel ajustado para {session.difficulty_level}.",
    }
    db.add(
        RealLifeTurn(
            session_id=session.id,
            user_message=clean_message,
            ai_question=next_question,
            feedback_json=json.dumps(feedback, ensure_ascii=True),
            response_time_seconds=rt,
            is_correct=1 if is_correct else 0,
            xp_awarded=xp,
        )
    )

    db.commit()
    db.refresh(session)
    return {
        "session_id": session.id,
        "status": session.status,
        "ai_question": next_question,
        "feedback": feedback,
        "difficulty_level": session.difficulty_level,
        "pressure_seconds": session.pressure_seconds,
        "turns_count": session.turns_count,
        "xp_awarded": xp,
        "bonus_breakdown": bonus,
        "total_xp_session": session.total_xp,
        "updated_at": session.updated_at,
    }

