from __future__ import annotations

import json
import re
import secrets
from collections import Counter
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.immersion import (
    ImmersionMission,
    ImmersionScenario,
    ImmersionSession,
    ImmersionTurn,
    MultiplayerChallenge,
    RoleplayCharacter,
    SmartNotificationQueue,
    TutorProfile,
    UserImmersionMissionProgress,
)
from app.models.user import User
from app.services.analytics_service import track_event
from app.services.growth_service import update_streak
from app.services.progress_service import mark_daily_activity, recalculate_level, today_for_user

FLUENCY_LEVELS = [
    ("Turista", 0),
    ("Viajante", 25),
    ("Morador", 45),
    ("Profissional", 65),
    ("Especialista", 80),
    ("Nativo", 92),
]

SCENARIO_SEEDS = [
    ("aeroporto", "Check-in no Aeroporto", "viagem", "beginner"),
    ("restaurante", "Pedido no Restaurante", "comida", "beginner"),
    ("hotel", "Check-in no Hotel", "viagem", "beginner"),
    ("reuniao", "Reuniao de Trabalho", "carreira", "intermediate"),
    ("entrevista", "Entrevista de Emprego", "carreira", "intermediate"),
    ("networking", "Evento de Networking", "carreira", "intermediate"),
    ("viagem", "Planejamento de Viagem", "viagem", "beginner"),
    ("hospital", "Atendimento no Hospital", "emergencia", "advanced"),
    ("policia", "Conversa com Policia", "emergencia", "advanced"),
    ("namoro", "Encontro e Conversa Casual", "social", "intermediate"),
]

CHARACTER_SEEDS = [
    ("Agente de Check-in", "objetivo e educado", "americano", "Confirmar reserva e despachar bagagem", "aeroporto"),
    ("Garcom Local", "amigavel e rapido", "britanico", "Anotar pedido com customizacoes", "restaurante"),
    ("Recepcionista", "profissional e cordial", "canadense", "Concluir check-in no hotel", "hotel"),
    ("Gestor de Produto", "direto e analitico", "americano", "Conduzir reuniao com entregaveis", "reuniao"),
    ("Recrutadora", "formal e curiosa", "britanico", "Avaliar experiencia profissional", "entrevista"),
    ("Fundadora Startup", "energica e estrategica", "australiano", "Trocar contatos para parceria", "networking"),
    ("Medico Plantonista", "calmo e preciso", "americano", "Coletar sintomas e orientar tratamento", "hospital"),
    ("Oficial", "objetivo e atento", "americano", "Entender ocorrido e orientar proximos passos", "policia"),
    ("Pessoa do Encontro", "descontraido e curioso", "irlandes", "Manter conversa natural e empatica", "namoro"),
]

MISSION_SEEDS = [
    ("pedir-comida", "Peca comida em ingles", "Finalize um pedido completo com bebida e acompanhamento.", "restaurante", 120),
    ("checkin-hotel", "Faca check-in no hotel", "Confirme dados da reserva e pergunte sobre cafe da manha.", "hotel", 130),
    ("reuniao-standup", "Participe de reuniao", "Explique progresso, bloqueios e proximos passos.", "reuniao", 150),
]

FILLER_WORDS = {"um", "uh", "ah", "er", "like", "you know", "tipo", "entao"}
GRAMMAR_PATTERNS = ("i has", "he go", "she go", "i am agree", "no have", "goed")


def _json_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, list):
        return [str(item) for item in parsed][:30]
    return []


def _json_dict(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _to_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=True)


def fluency_level_from_score(score: int) -> str:
    label = FLUENCY_LEVELS[0][0]
    for tier, minimum in FLUENCY_LEVELS:
        if score >= minimum:
            label = tier
    return label


def ensure_catalog_seed(db: Session) -> None:
    if db.query(ImmersionScenario.id).first():
        return

    created_by_slug: dict[str, int] = {}
    for slug, title, category, difficulty in SCENARIO_SEEDS:
        scenario = ImmersionScenario(
            slug=slug,
            title=title,
            category=category,
            difficulty=difficulty,
            context_json=_to_json({"tags": [category, difficulty], "real_world": True}),
        )
        db.add(scenario)
        db.flush()
        created_by_slug[slug] = scenario.id

    for name, personality, accent, objective, scenario_slug in CHARACTER_SEEDS:
        db.add(
            RoleplayCharacter(
                scenario_id=created_by_slug.get(scenario_slug),
                name=name,
                personality=personality,
                accent=accent,
                objective=objective,
                difficulty="intermediate" if scenario_slug in {"reuniao", "entrevista", "networking"} else "beginner",
            )
        )

    for slug, title, description, scenario_slug, xp_reward in MISSION_SEEDS:
        db.add(
            ImmersionMission(
                slug=slug,
                title=title,
                description=description,
                scenario_slug=scenario_slug,
                required_outcomes_json=_to_json({"min_turns": 4, "scenario_slug": scenario_slug}),
                xp_reward=xp_reward,
            )
        )

    db.commit()


def list_scenarios(db: Session) -> list[ImmersionScenario]:
    ensure_catalog_seed(db)
    return db.query(ImmersionScenario).filter(ImmersionScenario.is_active.is_(True)).order_by(ImmersionScenario.id.asc()).all()


def list_characters_by_scenario(db: Session, scenario_slug: str) -> list[RoleplayCharacter]:
    ensure_catalog_seed(db)
    scenario = db.query(ImmersionScenario).filter(ImmersionScenario.slug == scenario_slug).first()
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
    return (
        db.query(RoleplayCharacter)
        .filter(RoleplayCharacter.is_active.is_(True), RoleplayCharacter.scenario_id == scenario.id)
        .order_by(RoleplayCharacter.id.asc())
        .all()
    )


def _build_opening_message(scenario: ImmersionScenario, character: RoleplayCharacter | None) -> str:
    actor = character.name if character else "local guide"
    return f"Cenario: {scenario.title}. Personagem: {actor}. Comece com uma frase curta para destravar a conversa."


def start_immersion_session(db: Session, user: User, scenario_slug: str, character_id: int | None = None, source: str = "single") -> tuple[ImmersionSession, RoleplayCharacter | None, str]:
    ensure_catalog_seed(db)
    scenario = db.query(ImmersionScenario).filter(ImmersionScenario.slug == scenario_slug, ImmersionScenario.is_active.is_(True)).first()
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")

    character: RoleplayCharacter | None = None
    if character_id:
        character = (
            db.query(RoleplayCharacter)
            .filter(
                RoleplayCharacter.id == character_id,
                RoleplayCharacter.is_active.is_(True),
            )
            .first()
        )
        if not character:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    else:
        character = (
            db.query(RoleplayCharacter)
            .filter(RoleplayCharacter.scenario_id == scenario.id, RoleplayCharacter.is_active.is_(True))
            .order_by(RoleplayCharacter.id.asc())
            .first()
        )

    session = ImmersionSession(
        user_id=user.id,
        scenario_id=scenario.id,
        character_id=character.id if character else None,
        source=source[:24],
        status="active",
    )
    db.add(session)
    opening_message = _build_opening_message(scenario, character)
    db.flush()
    db.add(ImmersionTurn(session_id=session.id, speaker="ai", message=opening_message))
    track_event(db, "immersion_session_started", user_id=user.id, payload={"scenario": scenario.slug, "source": source})
    db.commit()
    db.refresh(session)
    return session, character, opening_message


def _analyze_user_text(message: str) -> dict[str, int | list[str]]:
    text = message.strip().lower()
    words = re.findall(r"[a-zA-Z']+", text)
    word_count = len(words)

    filler_count = 0
    for filler in FILLER_WORDS:
        filler_count += text.count(filler)

    grammar_hits = [pattern for pattern in GRAMMAR_PATTERNS if pattern in text]
    grammar_count = len(grammar_hits)

    short_words = [word for word in words if len(word) <= 3]
    repeated_short = [word for word, count in Counter(short_words).items() if count >= 3 and word not in FILLER_WORDS]

    return {
        "word_count": word_count,
        "filler_count": filler_count,
        "grammar_count": grammar_count,
        "grammar_hits": grammar_hits,
        "weak_vocabulary": repeated_short[:6],
    }


def _build_ai_reply(scenario_title: str, character: RoleplayCharacter | None, user_message: str) -> str:
    actor = character.name if character else "Coach"
    return f"{actor}: Entendi. Em {scenario_title}, voce pode expandir a frase com contexto e um pedido objetivo."


def _merge_unique(previous: list[str], new_items: list[str], limit: int = 20) -> list[str]:
    merged = list(previous)
    for item in new_items:
        if item and item not in merged:
            merged.append(item)
    return merged[:limit]


def add_turn(db: Session, user: User, session_id: int, message: str) -> dict:
    session = (
        db.query(ImmersionSession)
        .filter(ImmersionSession.id == session_id, ImmersionSession.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.status != "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session is not active")

    clean_message = message.strip()
    if not clean_message:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Message cannot be empty")

    scenario = db.query(ImmersionScenario).filter(ImmersionScenario.id == session.scenario_id).first()
    character = None
    if session.character_id:
        character = db.query(RoleplayCharacter).filter(RoleplayCharacter.id == session.character_id).first()

    analysis = _analyze_user_text(clean_message)
    hints: list[str] = []
    if int(analysis["filler_count"]) > 1:
        hints.append("Reduza fillers para soar mais confiante.")
    if int(analysis["grammar_count"]) > 0:
        hints.append("Revise a estrutura gramatical desta frase.")
    if int(analysis["word_count"]) < 5:
        hints.append("Tente responder com 1 frase mais detalhada.")
    if not hints:
        hints.append("Otimo ritmo. Adicione uma pergunta para manter o dialogo.")

    user_turn = ImmersionTurn(session_id=session.id, speaker="user", message=clean_message, feedback_json=_to_json({"hints": hints}))
    db.add(user_turn)

    ai_reply = _build_ai_reply(scenario.title if scenario else "o cenario", character, clean_message)
    ai_turn = ImmersionTurn(session_id=session.id, speaker="ai", message=ai_reply)
    db.add(ai_turn)

    session.total_turns = max(0, session.total_turns + 1)
    track_event(db, "immersion_turn_added", user_id=user.id, payload={"session_id": session.id, "turn": session.total_turns})
    db.commit()
    return {"session_id": session.id, "ai_reply": ai_reply, "hints": hints, "turn_number": session.total_turns}


def _analyze_session_turns(user_messages: list[str], turns: int) -> dict:
    aggregate_words = 0
    fillers = 0
    grammar = 0
    frequent_errors: list[str] = []
    weak_vocabulary: list[str] = []

    for message in user_messages:
        item = _analyze_user_text(message)
        aggregate_words += int(item["word_count"])
        fillers += int(item["filler_count"])
        grammar += int(item["grammar_count"])
        frequent_errors = _merge_unique(frequent_errors, [str(v) for v in item["grammar_hits"]])
        weak_vocabulary = _merge_unique(weak_vocabulary, [str(v) for v in item["weak_vocabulary"]])

    estimated_minutes = max(1, int(max(1, turns) * 0.7))
    speed = max(40, min(220, int(aggregate_words / estimated_minutes)))
    confidence = max(30, min(95, 45 + min(35, aggregate_words // 2) - fillers * 2))
    pronunciation = max(35, min(99, 90 - grammar * 4 - fillers * 2))

    fluency = int((confidence * 0.35) + (pronunciation * 0.35) + (max(30, min(100, speed // 2)) * 0.30))
    fluency = max(0, min(100, fluency))

    recommended_focus: list[str] = []
    if grammar > 0:
        recommended_focus.append("Estruturas gramaticais de alta frequencia")
    if fillers > 1:
        recommended_focus.append("Reducao de filler words em respostas espontaneas")
    if speed < 95:
        recommended_focus.append("Aumentar velocidade de resposta com roleplays curtos")
    if not recommended_focus:
        recommended_focus.append("Expandir vocabulario de contexto profissional")

    return {
        "speaking_speed_wpm": speed,
        "filler_words_count": fillers,
        "grammar_mistakes": grammar,
        "pronunciation_score": pronunciation,
        "confidence_score": confidence,
        "fluency_score": fluency,
        "frequent_errors": frequent_errors,
        "weak_vocabulary": weak_vocabulary,
        "recommended_focus": recommended_focus[:4],
    }


def _get_or_create_tutor_profile(db: Session, user_id: int) -> TutorProfile:
    profile = db.query(TutorProfile).filter(TutorProfile.user_id == user_id).first()
    if profile:
        return profile
    profile = TutorProfile(
        user_id=user_id,
        frequent_errors_json="[]",
        weak_vocabulary_json="[]",
        pronunciation_gaps_json="[]",
        adaptation_state_json="{}",
    )
    db.add(profile)
    db.flush()
    return profile


def finish_immersion_session(db: Session, user: User, session_id: int) -> dict:
    session = (
        db.query(ImmersionSession)
        .filter(ImmersionSession.id == session_id, ImmersionSession.user_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.status != "active":
        return {
            "session_id": session.id,
            "fluency_score": session.fluency_score,
            "confidence_score": session.confidence_score,
            "speaking_speed_wpm": session.speaking_speed_wpm,
            "filler_words_count": session.filler_words_count,
            "grammar_mistakes": session.grammar_mistakes,
            "pronunciation_score": session.pronunciation_score,
            "fluency_level": fluency_level_from_score(session.fluency_score),
            "recommended_focus": _json_dict(session.summary_json).get("recommended_focus", []),
            "share_token": session.share_token,
        }

    turns = (
        db.query(ImmersionTurn)
        .filter(ImmersionTurn.session_id == session.id, ImmersionTurn.speaker == "user")
        .order_by(ImmersionTurn.id.asc())
        .all()
    )
    user_messages = [turn.message for turn in turns]
    metrics = _analyze_session_turns(user_messages, session.total_turns)
    fluency_level = fluency_level_from_score(int(metrics["fluency_score"]))

    session.status = "completed"
    session.finished_at = datetime.now(UTC).replace(tzinfo=None)
    session.speaking_speed_wpm = int(metrics["speaking_speed_wpm"])
    session.filler_words_count = int(metrics["filler_words_count"])
    session.grammar_mistakes = int(metrics["grammar_mistakes"])
    session.pronunciation_score = int(metrics["pronunciation_score"])
    session.confidence_score = int(metrics["confidence_score"])
    session.fluency_score = int(metrics["fluency_score"])
    session.share_token = secrets.token_urlsafe(10)
    session.summary_json = _to_json(
        {
            "fluency_level": fluency_level,
            "recommended_focus": metrics["recommended_focus"],
            "frequent_errors": metrics["frequent_errors"],
            "weak_vocabulary": metrics["weak_vocabulary"],
        }
    )

    profile = _get_or_create_tutor_profile(db, user.id)
    profile.frequent_errors_json = _to_json(_merge_unique(_json_list(profile.frequent_errors_json), metrics["frequent_errors"]))
    profile.weak_vocabulary_json = _to_json(_merge_unique(_json_list(profile.weak_vocabulary_json), metrics["weak_vocabulary"]))
    pronunciation_gaps = _json_list(profile.pronunciation_gaps_json)
    if int(metrics["pronunciation_score"]) < 70:
        pronunciation_gaps = _merge_unique(pronunciation_gaps, ["entonacao", "sons curtos e longos"])
    profile.pronunciation_gaps_json = _to_json(pronunciation_gaps)
    profile.avg_speaking_speed_wpm = int((profile.avg_speaking_speed_wpm + int(metrics["speaking_speed_wpm"])) / 2) if profile.avg_speaking_speed_wpm else int(metrics["speaking_speed_wpm"])
    profile.confidence_score = int((profile.confidence_score + int(metrics["confidence_score"])) / 2) if profile.confidence_score else int(metrics["confidence_score"])
    profile.adaptation_state_json = _to_json(
        {
            "next_focus": metrics["recommended_focus"],
            "next_scenario_types": ["viagem", "carreira"] if fluency_level in {"Turista", "Viajante"} else ["carreira", "social"],
        }
    )
    profile.updated_at = datetime.now(UTC).replace(tzinfo=None)

    xp_reward = 40 + max(0, int(metrics["fluency_score"]) // 2)
    user.xp_total = max(0, (user.xp_total or 0) + xp_reward)
    user.level = recalculate_level(user.xp_total)
    active_day = today_for_user(user)
    mark_daily_activity(db, user.id, active_day)
    update_streak(user, active_day)

    track_event(
        db,
        "immersion_session_finished",
        user_id=user.id,
        payload={
            "session_id": session.id,
            "fluency_score": session.fluency_score,
            "fluency_level": fluency_level,
            "xp_reward": xp_reward,
        },
    )
    db.commit()
    return {
        "session_id": session.id,
        "fluency_score": session.fluency_score,
        "confidence_score": session.confidence_score,
        "speaking_speed_wpm": session.speaking_speed_wpm,
        "filler_words_count": session.filler_words_count,
        "grammar_mistakes": session.grammar_mistakes,
        "pronunciation_score": session.pronunciation_score,
        "fluency_level": fluency_level,
        "recommended_focus": metrics["recommended_focus"],
        "share_token": session.share_token,
    }


def list_missions(db: Session, user: User) -> list[dict]:
    ensure_catalog_seed(db)
    missions = db.query(ImmersionMission).filter(ImmersionMission.is_active.is_(True)).order_by(ImmersionMission.id.asc()).all()
    progress_rows = db.query(UserImmersionMissionProgress).filter(UserImmersionMissionProgress.user_id == user.id).all()
    status_by_mission = {row.mission_id: row.status for row in progress_rows}
    return [
        {
            "id": mission.id,
            "slug": mission.slug,
            "title": mission.title,
            "description": mission.description,
            "scenario_slug": mission.scenario_slug,
            "xp_reward": mission.xp_reward,
            "status": status_by_mission.get(mission.id, "pending"),
        }
        for mission in missions
    ]


def claim_mission(db: Session, user: User, mission_id: int) -> dict:
    mission = db.query(ImmersionMission).filter(ImmersionMission.id == mission_id, ImmersionMission.is_active.is_(True)).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")

    progress = (
        db.query(UserImmersionMissionProgress)
        .filter(UserImmersionMissionProgress.user_id == user.id, UserImmersionMissionProgress.mission_id == mission.id)
        .first()
    )
    if not progress:
        progress = UserImmersionMissionProgress(user_id=user.id, mission_id=mission.id, status="pending", attempts=0, progress_json="{}")
        db.add(progress)
        db.flush()

    progress.attempts = max(0, progress.attempts + 1)
    if progress.status != "completed":
        progress.status = "completed"
        progress.completed_at = datetime.now(UTC).replace(tzinfo=None)
        progress.progress_json = _to_json({"completed_by": "self_claim", "attempts": progress.attempts})
        user.xp_total = max(0, (user.xp_total or 0) + mission.xp_reward)
        user.level = recalculate_level(user.xp_total)
        track_event(db, "immersion_mission_completed", user_id=user.id, payload={"mission": mission.slug, "xp": mission.xp_reward})

    db.commit()
    return {
        "mission_id": mission.id,
        "status": progress.status,
        "xp_reward": mission.xp_reward,
        "new_xp_total": max(0, user.xp_total or 0),
        "new_level": max(0, user.level or 0),
    }


def create_multiplayer_challenge(db: Session, user: User, scenario_slug: str) -> dict:
    scenario = db.query(ImmersionScenario).filter(ImmersionScenario.slug == scenario_slug, ImmersionScenario.is_active.is_(True)).first()
    if not scenario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")

    challenge = MultiplayerChallenge(
        host_user_id=user.id,
        scenario_id=scenario.id,
        status="open",
        share_token=secrets.token_urlsafe(9),
    )
    db.add(challenge)
    track_event(db, "multiplayer_challenge_created", user_id=user.id, payload={"scenario": scenario_slug})
    db.commit()
    db.refresh(challenge)
    return {"challenge_id": challenge.id, "scenario_slug": scenario.slug, "status": challenge.status, "share_token": challenge.share_token}


def join_multiplayer_challenge(db: Session, user: User, challenge_id: int) -> dict:
    challenge = db.query(MultiplayerChallenge).filter(MultiplayerChallenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    if challenge.status != "open":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Challenge is not open")
    if challenge.host_user_id == user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Host cannot join own challenge")

    challenge.guest_user_id = user.id
    challenge.status = "in_progress"
    challenge.started_at = datetime.now(UTC).replace(tzinfo=None)
    track_event(db, "multiplayer_challenge_joined", user_id=user.id, payload={"challenge_id": challenge.id})
    db.commit()
    scenario = db.query(ImmersionScenario).filter(ImmersionScenario.id == challenge.scenario_id).first()
    return {
        "challenge_id": challenge.id,
        "scenario_slug": scenario.slug if scenario else "unknown",
        "status": challenge.status,
        "share_token": challenge.share_token,
    }


def queue_smart_notifications(db: Session, user: User) -> dict:
    triggers: list[str] = []
    now = datetime.now(UTC).replace(tzinfo=None)

    if user.last_active_date and user.last_active_date <= (today_for_user(user) - timedelta(days=1)):
        triggers.append("streak_em_risco")

    latest = (
        db.query(ImmersionSession)
        .filter(ImmersionSession.user_id == user.id, ImmersionSession.status == "completed")
        .order_by(ImmersionSession.finished_at.desc().nullslast())
        .first()
    )
    if latest and latest.fluency_score < 55:
        triggers.append("progresso_lento")
    if latest and latest.fluency_score >= 70:
        triggers.append("novo_desafio_desbloqueado")
    if (user.current_streak or 0) >= 5:
        triggers.append("suba_no_ranking")

    queued = 0
    for idx, trigger in enumerate(triggers):
        db.add(
            SmartNotificationQueue(
                user_id=user.id,
                trigger_type=trigger,
                payload_json=_to_json({"channel": "push", "source": "immersion_engine"}),
                status="pending",
                scheduled_for=now + timedelta(minutes=idx * 30),
            )
        )
        queued += 1

    if queued:
        track_event(db, "smart_notifications_queued", user_id=user.id, payload={"count": queued, "triggers": triggers})
    db.commit()
    return {"queued": queued, "triggers": triggers}


def build_immersion_dashboard(db: Session, user: User) -> dict:
    ensure_catalog_seed(db)
    latest_session = (
        db.query(ImmersionSession)
        .filter(ImmersionSession.user_id == user.id, ImmersionSession.status == "completed")
        .order_by(ImmersionSession.finished_at.desc().nullslast())
        .first()
    )
    profile = _get_or_create_tutor_profile(db, user.id)

    latest_fluency = latest_session.fluency_score if latest_session else 0
    fluency_level = fluency_level_from_score(latest_fluency)
    adaptation = _json_dict(profile.adaptation_state_json)
    adaptation_plan = [str(item) for item in adaptation.get("next_focus", [])] or [
        "Treinar respostas de 2 frases em cenarios cotidianos",
        "Priorizar conversas com menos fillers",
    ]

    scenarios = list_scenarios(db)
    recommended = scenarios[:4]
    missions = list_missions(db, user)[:3]

    return {
        "fluency_level": fluency_level,
        "latest_fluency_score": latest_fluency,
        "tutor_insights": {
            "frequent_errors": _json_list(profile.frequent_errors_json),
            "weak_vocabulary": _json_list(profile.weak_vocabulary_json),
            "pronunciation_gaps": _json_list(profile.pronunciation_gaps_json),
            "confidence_score": max(0, profile.confidence_score or 0),
            "avg_speaking_speed_wpm": max(0, profile.avg_speaking_speed_wpm or 0),
            "adaptation_plan": adaptation_plan,
        },
        "recommended_scenarios": [
            {
                "id": item.id,
                "slug": item.slug,
                "title": item.title,
                "category": item.category,
                "difficulty": item.difficulty,
            }
            for item in recommended
        ],
        "missions": missions,
        "growth_loops": [
            "Convide 1 amigo e desbloqueie booster de XP por 24h",
            "Publique um roleplay e ganhe multiplicador de streak",
            "Complete 3 missoes seguidas para liberar semana PRO",
        ],
    }


def landing_page_payload() -> dict:
    return {
        "headline": "Pare de decorar palavras. Comece a viver o idioma.",
        "subheadline": "Treine conversacao real com IA em cenarios de vida real, feedback de fluencia e progressao RPG.",
        "cta_primary": "Comecar imersao gratuita",
        "cta_secondary": "Ver demo do AI Tutor",
        "trust_points": [
            "Roleplays em aeroporto, trabalho e situacoes de emergencia",
            "Tutor pessoal que aprende com seus erros recorrentes",
            "Pontuacao de fluencia com speaking speed e pronunciation score",
        ],
        "conversation_samples": [
            {
                "scenario": "Restaurante",
                "line_user": "Could I get a grilled chicken salad without onions?",
                "line_ai": "Absolutely. Would you like a drink with that order?",
            },
            {
                "scenario": "Entrevista",
                "line_user": "I led the migration project and reduced incidents by 40 percent.",
                "line_ai": "Great impact. How did you prioritize the rollout phases?",
            },
        ],
        "updated_at": datetime.now(UTC).replace(tzinfo=None),
    }

