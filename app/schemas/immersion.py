from datetime import datetime

from pydantic import BaseModel


class ImmersionScenarioOut(BaseModel):
    id: int
    slug: str
    title: str
    category: str
    difficulty: str


class RoleplayCharacterOut(BaseModel):
    id: int
    name: str
    personality: str
    accent: str
    objective: str
    difficulty: str


class ImmersionStartIn(BaseModel):
    scenario_slug: str
    character_id: int | None = None
    source: str = "single"


class ImmersionStartOut(BaseModel):
    session_id: int
    scenario_slug: str
    character: RoleplayCharacterOut | None = None
    opening_message: str


class ImmersionTurnIn(BaseModel):
    message: str


class ImmersionTurnOut(BaseModel):
    session_id: int
    ai_reply: str
    hints: list[str]
    turn_number: int


class ImmersionFinishOut(BaseModel):
    session_id: int
    fluency_score: int
    confidence_score: int
    speaking_speed_wpm: int
    filler_words_count: int
    grammar_mistakes: int
    pronunciation_score: int
    fluency_level: str
    recommended_focus: list[str]
    share_token: str | None = None


class TutorInsightOut(BaseModel):
    frequent_errors: list[str]
    weak_vocabulary: list[str]
    pronunciation_gaps: list[str]
    confidence_score: int
    avg_speaking_speed_wpm: int
    adaptation_plan: list[str]


class ImmersionMissionOut(BaseModel):
    id: int
    slug: str
    title: str
    description: str
    scenario_slug: str
    xp_reward: int
    status: str = "pending"


class MissionClaimOut(BaseModel):
    mission_id: int
    status: str
    xp_reward: int
    new_xp_total: int
    new_level: int


class ImmersionDashboardOut(BaseModel):
    fluency_level: str
    latest_fluency_score: int
    tutor_insights: TutorInsightOut
    recommended_scenarios: list[ImmersionScenarioOut]
    missions: list[ImmersionMissionOut]
    growth_loops: list[str]


class MultiplayerChallengeIn(BaseModel):
    scenario_slug: str


class MultiplayerChallengeOut(BaseModel):
    challenge_id: int
    scenario_slug: str
    status: str
    share_token: str | None = None


class NotificationSyncOut(BaseModel):
    queued: int
    triggers: list[str]


class LandingConversationSample(BaseModel):
    scenario: str
    line_user: str
    line_ai: str


class LandingPageOut(BaseModel):
    headline: str
    subheadline: str
    cta_primary: str
    cta_secondary: str
    trust_points: list[str]
    conversation_samples: list[LandingConversationSample]
    updated_at: datetime
