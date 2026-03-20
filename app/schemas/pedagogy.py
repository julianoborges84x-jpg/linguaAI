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


class ClickPathUnitOut(BaseModel):
    unit_id: int
    title: str
    cefr_level: str
    primary_skill: str
    is_pro_only: bool
    completed: bool
    current_step: int
    total_steps: int


class ClickLessonStepOut(BaseModel):
    step_index: int
    step_type: str
    instruction: str
    expected_pattern: str


class ClickLessonOut(BaseModel):
    unit_id: int
    title: str
    description: str
    cefr_level: str
    language_code: str
    current_step: int
    total_steps: int
    completed: bool
    score: float
    steps: list[ClickLessonStepOut]


class ClickAdvanceIn(BaseModel):
    correct: bool = True
    score_delta: float = 1.0


class ClickAdvanceOut(BaseModel):
    unit_id: int
    current_step: int
    total_steps: int
    completed: bool
    score: float


class CurrentTrackOut(BaseModel):
    track_slug: str
    track_title: str
    estimated_level: str
    entry_profile: str
    current_module_id: int | None = None
    current_lesson_id: int | None = None
    current_step_index: int = 0
    resume_available: bool = False
    next_lesson_id: int | None = None
    completed_lessons: int
    total_lessons: int


class ModuleLessonStatusOut(BaseModel):
    id: int
    title: str
    status: str
    current_step: int
    total_steps: int


class ModuleOut(BaseModel):
    id: int
    slug: str
    title: str
    progress_percent: int
    lessons: list[ModuleLessonStatusOut]


class LessonExampleOut(BaseModel):
    en: str
    pt: str


class LessonExerciseOut(BaseModel):
    id: str
    type: str
    prompt: str
    hint_pt: str


class LessonCriteriaOut(BaseModel):
    min_exercises_correct: int
    min_conversation_turns: int
    checkpoint_required: bool


class LessonProgressOut(BaseModel):
    current_step: int
    total_steps: int
    completed: bool
    score: float


class LessonDetailOut(BaseModel):
    id: int
    module_name: str
    order_index: int
    title: str
    lesson_objective: str
    cefr_level: str
    estimated_duration_min: int
    target_vocabulary: list[str]
    key_structures: list[str]
    grammar_explanation_pt: str
    examples: list[LessonExampleOut]
    exercises: list[LessonExerciseOut]
    ai_context: dict
    final_review: list[str]
    completion_criteria: LessonCriteriaOut
    progress: LessonProgressOut


class LessonSubmitIn(BaseModel):
    correct_count: int = 0
    total_count: int = 0
    conversation_turns: int = 0


class LessonSubmitOut(BaseModel):
    lesson_id: int
    completed: bool
    accuracy: float
    next_review_at: str
    next_step: str


class LessonStepSaveIn(BaseModel):
    current_step: int


class LessonStepSaveOut(BaseModel):
    lesson_id: int
    current_step: int
    total_steps: int
    completed: bool
    score: float


class ReviewTodayItemOut(BaseModel):
    id: int
    queue_type: str
    reference_id: int
    priority: int
    due_at: str


class ReviewTodayOut(BaseModel):
    items: list[ReviewTodayItemOut]
    estimated_minutes: int


class ReviewSubmitIn(BaseModel):
    review_item_id: int
    correct: bool


class ReviewSubmitOut(BaseModel):
    review_item_id: int
    correct: bool
    next_review_at: str


class ProgressSummaryOut(BaseModel):
    lesson_progress: dict
    module_completion: int
    vocabulary_mastered: int
    review_due: int
    estimated_level: str
    weekly_consistency: int
