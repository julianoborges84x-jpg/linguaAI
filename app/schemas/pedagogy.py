from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PlacementIn(BaseModel):
    sentence_complexity: float = 0.0
    vocabulary_variety: float = 0.0
    error_frequency: float = 0.0
    tense_control: float = 0.0
    autonomy: float = 0.0
    clarity: float = 0.0


class PlacementOut(BaseModel):
    estimated_level: str
    confidence: float
    speaking_score: float
    vocabulary_score: float
    grammar_score: float
    fluency_score: float


class MistakeIn(BaseModel):
    user_text: str = Field(min_length=1)
    corrected_text: str = Field(min_length=1)
    error_type: str = Field(min_length=1)
    explanation: str = ""
    severity: int = 1
    context_feature: str = "chat"


class MistakeOut(BaseModel):
    id: int
    error_type: str
    severity: int
    explanation: str


class VocabularyReviewIn(BaseModel):
    item_id: int
    correct: bool


class RecommendationOut(BaseModel):
    recommendation_type: str
    title: str
    description: str
    locked_for_free: bool = False


class LearningTrackProgressOut(BaseModel):
    level: str
    completed_units: int
    total_units: int


class PedagogyDashboardOut(BaseModel):
    estimated_level: str
    confidence: float
    strengths: list[str]
    weaknesses: list[str]
    recurring_errors: list[str]
    words_in_review: int
    next_step: RecommendationOut
    track_progress: list[LearningTrackProgressOut]
    recommendations: list[RecommendationOut]


class ReviewQueueItemOut(BaseModel):
    id: int
    queue_type: str
    reference_id: int
    due_at: datetime
    priority: int
