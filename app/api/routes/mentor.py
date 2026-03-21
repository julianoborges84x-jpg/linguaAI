from datetime import datetime, timedelta
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.database import get_db
from app.models.history import LearningHistory
from app.models.language import Language
from app.models.pedagogy import MistakeLog
from app.models.user import PlanEnum, User
from app.schemas.mentor import (
    MentorChatIn,
    MentorChatOut,
    MentorDetectIn,
    MentorDetectOut,
    VoiceChatIn,
    VoiceChatOut,
    VoiceMentorOut,
    VoiceUsageOut,
)
from app.services import llm_client
from app.services.adaptive_learning_service import build_recommendations, get_or_create_learner_profile, log_mistake, update_strength
from app.services.analytics_service import track_event
from app.services.pedagogy_seed import ensure_pedagogical_seed
from app.services.progress_service import today_for_user

router = APIRouter(prefix="/mentor", tags=["mentor"])
logger = logging.getLogger("linguaai.mentor")
VOICE_FREE_LIMIT_MESSAGE = "🔒 Você atingiu o limite gratuito. Desbloqueie o PRO para continuar falando com seu mentor."
LLM_QUOTA_SIGNATURE = "openai is temporarily unavailable due to quota limits"
LLM_KEY_SIGNATURE = "openai_api_key not configured"
DEFAULT_LANGUAGE_CATALOG: dict[str, tuple[str, str, str]] = {
    "en": ("English", "United States", "Indo-European"),
    "eng": ("English", "United States", "Indo-European"),
    "pt": ("Portuguese", "Brazil", "Indo-European"),
    "por": ("Portuguese", "Brazil", "Indo-European"),
    "es": ("Spanish", "Spain", "Indo-European"),
    "spa": ("Spanish", "Spain", "Indo-European"),
}
VOICE_MENTORS: list[dict[str, str]] = [
    {
        "id": "clara",
        "name": "Clara",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&h=300&fit=crop",
        "description": "Elegante, acolhedora e paciente para destravar iniciantes.",
        "speaking_style": "Voz suave, calma e paciente",
        "pedagogical_focus": "Iniciantes e confianca",
    },
    {
        "id": "maya",
        "name": "Maya",
        "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&h=300&fit=crop",
        "description": "Gentil e natural para conversas do dia a dia e viagens.",
        "speaking_style": "Voz quente, gentil e natural",
        "pedagogical_focus": "Conversacao cotidiana e viagens",
    },
    {
        "id": "ethan",
        "name": "Ethan",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&h=300&fit=crop",
        "description": "Claro e confiante para entrevistas e business English.",
        "speaking_style": "Voz masculina suave, clara e segura",
        "pedagogical_focus": "Trabalho, entrevistas e business English",
    },
    {
        "id": "noah",
        "name": "Noah",
        "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&h=300&fit=crop",
        "description": "Maduro e acolhedor para pronuncia e clareza.",
        "speaking_style": "Voz masculina madura e acolhedora",
        "pedagogical_focus": "Pronuncia, clareza e confianca",
    },
]


def level_style(level: int) -> str:
    if level <= 3:
        return "Use frases curtas e vocabulario simples."
    if level <= 6:
        return "Use explicacoes moderadas com exemplos curtos."
    return "Use linguagem avancada, com nuances e termos tecnicos quando necessario."


def language_context(db: Session, code: str | None) -> Language | None:
    if not code:
        return None
    return db.query(Language).filter(Language.iso_code == code).first()


def ensure_language_row(db: Session, code: str) -> Language:
    existing = db.query(Language).filter(Language.iso_code == code).first()
    if existing:
        return existing

    name, region, family = DEFAULT_LANGUAGE_CATALOG.get(code, (code.upper(), "Unknown", "Unknown"))
    lang = Language(iso_code=code, name=name, region=region, family=family)
    db.add(lang)
    db.flush()
    return lang


def resolve_target_language(db: Session, user: User) -> Language:
    candidates = [
        (user.target_language_code or "").strip().lower(),
        (user.target_language or "").strip().lower(),
    ]
    candidates = [item for item in candidates if item]
    if not candidates:
        candidates = ["en"]

    for code in candidates:
        lang = language_context(db, code)
        if lang:
            if user.target_language_code != code:
                user.target_language_code = code
            if user.target_language != code:
                user.target_language = code
            return lang

    fallback_code = candidates[0]
    lang = ensure_language_row(db, fallback_code)
    if user.target_language_code != fallback_code:
        user.target_language_code = fallback_code
    if user.target_language != fallback_code:
        user.target_language = fallback_code
    return lang


def build_instructions(user: User, target_language: Language | None, base_language: Language | None, feature: str) -> str:
    target_text = "Indefinido"
    if target_language:
        target_text = (
            f"{target_language.name} ({target_language.iso_code}), "
            f"regiao principal: {target_language.region}, familia: {target_language.family}"
        )
    base_text = "Indefinido"
    if base_language:
        base_text = (
            f"{base_language.name} ({base_language.iso_code}), "
            f"regiao principal: {base_language.region}, familia: {base_language.family}"
        )

    return (
        "Voce e o agente de IA MentorLingua."
        " Chame o aluno pelo nome em cada resposta."
        f" O nome do aluno e {user.name}."
        " Adapte a linguagem ao nivel do aluno."
        f" Nivel do aluno: {user.level}."
        f" {level_style(user.level)}"
        " Ensine escrita, conversacao, dialeto e vicios de linguagem conforme o pedido."
        " Corrija erros detalhadamente."
        " Explique diferencas culturais."
        " Explique diferencas formais e informais."
        f" O foco atual e: {feature}."
        f" Idioma alvo do aluno: {target_text}."
        f" Idioma base do aluno: {base_text}."
        " Ajuste o ensino conforme a estrutura gramatical do idioma alvo."
    )


def build_history_context(db: Session, user_id: int, limit: int = 10) -> str:
    items = (
        db.query(LearningHistory)
        .filter(LearningHistory.user_id == user_id)
        .order_by(LearningHistory.id.desc())
        .limit(limit)
        .all()
    )
    items.reverse()
    filtered: list[str] = []
    for item in items:
        content = (item.content or "").strip()
        lowered = content.lower()
        if LLM_QUOTA_SIGNATURE in lowered or LLM_KEY_SIGNATURE in lowered:
            continue
        filtered.append(f"{item.role}: {content}")
    return "\n".join(filtered)


def _is_upstream_quota_fallback(text: str) -> bool:
    lowered = (text or "").strip().lower()
    return LLM_QUOTA_SIGNATURE in lowered or LLM_KEY_SIGNATURE in lowered


def _voice_free_limit() -> int:
    return 6


def _sync_voice_usage_window(user: User) -> bool:
    if user.plan == PlanEnum.PRO:
        return False
    if not settings.voice_free_daily_reset:
        return False

    today = today_for_user(user)
    if user.voice_usage_reset_at == today:
        return False

    user.voice_messages_used = 0
    user.voice_usage_reset_at = today
    return True


def _voice_usage_payload(user: User) -> VoiceUsageOut:
    if user.plan == PlanEnum.PRO:
        return VoiceUsageOut(plan="PRO", used=max(0, user.voice_messages_used or 0), limit=None, remaining=None, blocked=False, reset_on=None)

    limit = _voice_free_limit()
    used = max(0, user.voice_messages_used or 0)
    remaining = max(0, limit - used)
    reset_on = user.voice_usage_reset_at if settings.voice_free_daily_reset else None
    return VoiceUsageOut(
        plan="FREE",
        used=used,
        limit=limit,
        remaining=remaining,
        blocked=used >= limit,
        reset_on=reset_on,
    )


def _enforce_voice_limit(user: User) -> None:
    if user.plan == PlanEnum.PRO:
        return
    usage = _voice_usage_payload(user)
    if usage.blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=VOICE_FREE_LIMIT_MESSAGE)


def _maybe_detect_mistake(user_text: str) -> tuple[str, str] | None:
    lowered = user_text.lower()
    if "goed" in lowered:
        return ("tense", "Use 'went' instead of 'goed' for simple past.")
    if "i no understand" in lowered:
        return ("word order", "Try 'I don't understand'.")
    if "in monday" in lowered:
        return ("preposition", "Use 'on Monday'.")
    return None


@router.get("/history")
def get_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = (
        db.query(LearningHistory)
        .filter(LearningHistory.user_id == user.id)
        .order_by(LearningHistory.id.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "id": item.id,
            "feature": item.feature,
            "created_at": item.created_at.isoformat(),
            "preview": (item.content[:180] + "...") if len(item.content) > 180 else item.content,
        }
        for item in items
    ]


@router.get("/progress/weekly")
def weekly_progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        tz = ZoneInfo(user.timezone)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")

    today = datetime.now(tz).date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    results = []

    for day in days:
        start_local = datetime.combine(day, datetime.min.time(), tzinfo=tz)
        end_local = datetime.combine(day, datetime.max.time(), tzinfo=tz)
        start_utc = start_local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
        end_utc = end_local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

        count = (
            db.query(LearningHistory.id)
            .filter(
                LearningHistory.user_id == user.id,
                LearningHistory.created_at >= start_utc,
                LearningHistory.created_at <= end_utc,
            )
            .count()
        )
        results.append(
            {
                "date": day.isoformat(),
                "label": day.strftime("%a"),
                "count": count,
            }
        )

    return results


@router.post("/detect-language", response_model=MentorDetectOut)
def detect_base_language(
    payload: MentorDetectIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info("detect-language request received user_id=%s", user.id)
    sample_text = payload.text.strip()
    if not sample_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text is required")

    try:
        logger.info("detect-language calling llm user_id=%s url=%s", user.id, llm_client.get_llm_service_url())
        iso_code = llm_client.detect_language(sample_text)
        logger.info("detect-language llm response ok user_id=%s", user.id)
    except llm_client.LLMServiceError as exc:
        logger.warning("detect-language failed for user_id=%s: %s", user.id, exc.message)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message)

    lang = db.query(Language).filter(Language.iso_code == iso_code).first()
    if not lang:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Detected language not supported")

    user.base_language_code = iso_code
    db.commit()
    return MentorDetectOut(iso_code=iso_code, name=lang.name)


@router.post("/chat", response_model=MentorChatOut)
def chat(
    payload: MentorChatIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info("chat request received user_id=%s feature=%s", user.id, payload.feature)
    if user.plan == PlanEnum.FREE and payload.feature in {"speaking", "dialect", "fillers"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Upgrade para PRO para acessar este recurso",
        )

    target_language = resolve_target_language(db, user)
    base_language = language_context(db, user.base_language_code)

    history_text = build_history_context(db, user.id)
    instructions = build_instructions(user, target_language, base_language, payload.feature)
    input_text = payload.message
    if history_text:
        input_text = f"Historico:\n{history_text}\n\nMensagem atual:\n{payload.message}"

    llm_fallback_reason: str | None = None
    try:
        logger.info("chat calling llm user_id=%s url=%s", user.id, llm_client.get_llm_service_url())
        reply = llm_client.generate_reply(instructions, input_text)
        logger.info("chat llm response ok user_id=%s", user.id)
        if _is_upstream_quota_fallback(reply):
            llm_fallback_reason = "OpenAI quota limits"
            reply = (
                "Estou com indisponibilidade temporaria no motor de IA agora. "
                "Tente novamente em alguns instantes e, se quiser, envie uma frase curta para eu revisar manualmente."
            )
    except llm_client.LLMServiceError as exc:
        logger.warning("mentor chat llm failed user_id=%s feature=%s: %s", user.id, payload.feature, exc.message)
        llm_fallback_reason = exc.message
        reply = (
            "Estou com instabilidade para acessar o motor de IA agora. "
            "Ainda assim, vamos continuar: tente escrever a frase novamente no passado e eu reviso em seguida."
        )

    db.add(LearningHistory(user_id=user.id, role="user", content=payload.message, feature=payload.feature))
    db.add(LearningHistory(user_id=user.id, role="assistant", content=reply, feature=payload.feature))
    ensure_pedagogical_seed(db)
    update_strength(db, user.id, payload.feature, boost=0.04)
    detected_errors: list[str] = []
    correction: str | None = None
    explanation: str | None = None
    suggestion: str | None = None
    recommendation: str | None = None
    micro_intervention: str | None = None
    micro_drill_questions: list[str] = []

    mistake_detected = _maybe_detect_mistake(payload.message)
    if mistake_detected:
        error_type, explanation = mistake_detected
        detected_errors.append(error_type)
        correction = payload.message.replace("goed", "went").replace("I no understand", "I don't understand").replace("in Monday", "on Monday")
        suggestion = f"Try: {correction}" if correction != payload.message else "Try a cleaner sentence using the corrected structure."
        log_mistake(
            db,
            user_id=user.id,
            error_type=error_type,
            user_text=payload.message,
            corrected_text=reply,
            explanation=explanation,
            severity=2,
            context_feature=payload.feature,
        )
        track_event(db, "grammar_reinforcement_triggered", user_id=user.id, payload={"error_type": error_type})
        occurrences = (
            db.query(MistakeLog.id)
            .filter(MistakeLog.user_id == user.id, MistakeLog.error_type == error_type)
            .count()
        )
        if occurrences >= 3:
            micro_intervention = f"Percebi recorrencia em {error_type}. Vamos treinar isso rapidamente?"
            if error_type == "tense":
                micro_drill_questions = [
                    "Complete: Yesterday I ___ to work. (go)",
                    "Say one sentence about what you did last night.",
                    "Rewrite: Today I go to the gym -> past tense.",
                ]
            elif error_type == "preposition":
                micro_drill_questions = [
                    "Choose: on Monday / in Monday",
                    "Write one sentence with 'on Friday'.",
                ]

    learner_profile = get_or_create_learner_profile(db, user.id)
    pedagogical_recs = build_recommendations(db, user, learner_profile)
    if pedagogical_recs:
        recommendation = pedagogical_recs[0].get("title") if isinstance(pedagogical_recs[0], dict) else None
    track_event(db, "chat_message_sent", user_id=user.id, payload={"feature": payload.feature})
    db.commit()

    ads = None
    if user.plan == PlanEnum.FREE:
        ads = ["Assine o plano PRO para desbloquear fala, dialeto e sem anuncios."]

    return MentorChatOut(
        message=reply,
        reply=reply,
        correction=correction,
        explanation=explanation,
        suggestion=suggestion,
        detected_errors=detected_errors,
        recommendation=recommendation,
        micro_intervention=micro_intervention,
        micro_drill_questions=micro_drill_questions,
        fallback_reason=llm_fallback_reason,
        ads=ads,
    )


@router.get("/voice/mentors", response_model=list[VoiceMentorOut])
def voice_mentors(_: User = Depends(get_current_user)):
    return [VoiceMentorOut(**mentor) for mentor in VOICE_MENTORS]


@router.get("/voice/usage", response_model=VoiceUsageOut)
def voice_usage(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if _sync_voice_usage_window(user):
        db.commit()
        db.refresh(user)
    return _voice_usage_payload(user)


@router.post("/voice/chat", response_model=VoiceChatOut)
def voice_chat(
    payload: VoiceChatIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logger.info("voice chat request received user_id=%s mentor_id=%s", user.id, payload.mentor_id)
    if _sync_voice_usage_window(user):
        db.flush()
    _enforce_voice_limit(user)

    mentor = next((item for item in VOICE_MENTORS if item["id"] == payload.mentor_id), None)
    if not mentor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice mentor not found")

    target_language = resolve_target_language(db, user)
    base_language = language_context(db, user.base_language_code)
    history_text = build_history_context(db, user.id, limit=6)
    instructions = (
        build_instructions(user, target_language, base_language, feature="speaking")
        + f" Persona do mentor: {mentor['name']}. Estilo de fala: {mentor['speaking_style']}."
        + f" Foco pedagogico: {mentor['pedagogical_focus']}."
        + " Sempre responda em ingles americano natural (en-US), com tom de conversa realista ao vivo."
        + " Responda de forma conversacional para audio e inclua correcao natural."
    )
    input_text = payload.message
    if history_text:
        input_text = f"Historico:\n{history_text}\n\nTranscricao atual:\n{payload.message}"

    try:
        logger.info("voice chat calling llm user_id=%s mentor_id=%s url=%s", user.id, payload.mentor_id, llm_client.get_llm_service_url())
        reply = llm_client.generate_reply(instructions, input_text)
        logger.info("voice chat llm response ok user_id=%s mentor_id=%s", user.id, payload.mentor_id)
        if _is_upstream_quota_fallback(reply):
            raise llm_client.LLMServiceError("OpenAI quota limits")
    except llm_client.LLMServiceError as exc:
        logger.warning("voice chat failed for user_id=%s mentor_id=%s: %s", user.id, payload.mentor_id, exc.message)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message)

    db.add(LearningHistory(user_id=user.id, role="user", content=payload.message, feature="voice"))
    db.add(LearningHistory(user_id=user.id, role="assistant", content=reply, feature="voice"))
    ensure_pedagogical_seed(db)
    update_strength(db, user.id, "speaking", boost=0.05)
    mistake_detected = _maybe_detect_mistake(payload.message)
    if mistake_detected:
        error_type, explanation = mistake_detected
        log_mistake(
            db,
            user_id=user.id,
            error_type=error_type,
            user_text=payload.message,
            corrected_text=reply,
            explanation=explanation,
            severity=2,
            context_feature="voice",
        )
        track_event(db, "grammar_reinforcement_triggered", user_id=user.id, payload={"error_type": error_type})
    if user.plan == PlanEnum.FREE:
        user.voice_messages_used = max(0, user.voice_messages_used or 0) + 1
        if settings.voice_free_daily_reset and user.voice_usage_reset_at != today_for_user(user):
            user.voice_usage_reset_at = today_for_user(user)
    track_event(db, "voice_session_started", user_id=user.id, payload={"mentor_id": mentor["id"]})
    db.commit()
    db.refresh(user)

    return VoiceChatOut(
        mentor_id=mentor["id"],
        mentor_name=mentor["name"],
        transcript=payload.message,
        reply=reply,
        tts_text=reply,
        audio_available=True,
        voice_usage=_voice_usage_payload(user),
    )

