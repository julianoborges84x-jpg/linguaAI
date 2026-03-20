export type Screen = 
  | 'welcome' 
  | 'language-select' 
  | 'proficiency-level' 
  | 'learning-goal' 
  | 'creating-plan' 
  | 'login' 
  | 'dashboard' 
  | 'lesson' 
  | 'chat'
  | 'immersion'
  | 'real-life'
  | 'daily-challenge';

export interface UserProfile {
  language: string;
  level: string;
  goal: string;
}

export interface AuthUser {
  id: number;
  name: string;
  email: string;
  plan: 'FREE' | 'PRO';
  xp_total: number;
  level: number;
  timezone: string;
  onboarding_completed: boolean;
  target_language?: string | null;
  language?: string | null;
  target_language_code?: string | null;
  base_language_code?: string | null;
  subscription_status?: string | null;
  current_streak?: number;
  longest_streak?: number;
  last_active_date?: string | null;
  referral_code?: string | null;
  referred_count?: number;
  referred_by?: number | null;
  referral_count?: number;
  pro_access_until?: string | null;
  voice_messages_used?: number;
  voice_usage_reset_at?: string | null;
}

export interface ChatMessage {
  role: 'user' | 'model';
  text: string;
  translation?: string;
  correction?: string | null;
  explanation?: string | null;
  suggestion?: string | null;
  detected_errors?: string[];
  recommendation?: string | null;
  micro_intervention?: string | null;
  micro_drill_questions?: string[];
  fallback_reason?: string | null;
}

export interface BillingStatus {
  stripe_configured: boolean;
  plan: 'FREE' | 'PRO';
  subscription_status?: string | null;
}

export interface CheckoutResponse {
  checkout_url: string;
  url: string;
}

export interface SessionStartResponse {
  session_id: number;
}

export interface SessionTopic {
  id: number;
  name: string;
  category: string;
}

export interface SessionFinishResponse {
  session_id: number;
  xp_earned: number;
  interactions_count: number;
  finished_at: string;
}

export interface ChatResponse {
  message?: string;
  reply: string;
  correction?: string | null;
  explanation?: string | null;
  suggestion?: string | null;
  detected_errors?: string[];
  recommendation?: string | null;
  micro_intervention?: string | null;
  micro_drill_questions?: string[];
  fallback_reason?: string | null;
  ads?: string[] | null;
}

export interface ChatHistoryItem {
  id: number;
  feature: string;
  created_at: string;
  preview: string;
}

export interface MissionToday {
  day_date: string;
  target_sessions: number;
  completed_sessions: number;
  is_completed: boolean;
  bonus_xp_awarded: boolean;
}

export interface WeeklyProgressItem {
  date: string;
  sessions_count: number;
  minutes_studied: number;
  xp_earned: number;
}

export interface LeaderboardItem {
  rank: number;
  user_id: number;
  name: string;
  xp_week: number;
  target_language_code?: string | null;
}

export interface ReferralStatus {
  referral_code: string;
  referral_link: string;
  referred_count: number;
  reward_xp_total: number;
}

export interface ReferralMe {
  referral_code: string;
  invite_link: string;
  pro_access_until?: string | null;
}

export interface ReferralInvitedUser {
  user_id: number;
  name: string;
  email: string;
}

export interface ReferralStats {
  referral_count: number;
  reward_xp_total: number;
  pro_access_until?: string | null;
  invited_users: ReferralInvitedUser[];
}

export interface GrowthDashboardData {
  current_streak: number;
  longest_streak: number;
  xp_total: number;
  level: number;
  xp_in_level: number;
  xp_to_next_level: number;
  next_level: number;
  mission_today: MissionToday;
  weekly_progress: WeeklyProgressItem[];
  weekly_sessions_total: number;
  weekly_minutes_total: number;
  weekly_xp_total: number;
  leaderboard_top: LeaderboardItem[];
  referral: ReferralStatus;
}

export interface ImmersionScenario {
  id: number;
  slug: string;
  title: string;
  category: string;
  difficulty: string;
}

export interface RoleplayCharacter {
  id: number;
  name: string;
  personality: string;
  accent: string;
  objective: string;
  difficulty: string;
}

export interface ImmersionStartResponse {
  session_id: number;
  scenario_slug: string;
  opening_message: string;
  character?: RoleplayCharacter | null;
}

export interface ImmersionTurnResponse {
  session_id: number;
  ai_reply: string;
  hints: string[];
  turn_number: number;
}

export interface ImmersionMission {
  id: number;
  slug: string;
  title: string;
  description: string;
  scenario_slug: string;
  xp_reward: number;
  status: string;
}

export interface TutorInsights {
  frequent_errors: string[];
  weak_vocabulary: string[];
  pronunciation_gaps: string[];
  confidence_score: number;
  avg_speaking_speed_wpm: number;
  adaptation_plan: string[];
}

export interface ImmersionDashboardData {
  fluency_level: string;
  latest_fluency_score: number;
  tutor_insights: TutorInsights;
  recommended_scenarios: ImmersionScenario[];
  missions: ImmersionMission[];
  growth_loops: string[];
}

export interface ImmersionFinishResponse {
  session_id: number;
  fluency_score: number;
  confidence_score: number;
  speaking_speed_wpm: number;
  filler_words_count: number;
  grammar_mistakes: number;
  pronunciation_score: number;
  fluency_level: string;
  recommended_focus: string[];
  share_token?: string | null;
}

export interface RealLifeSessionStart {
  session_id: number;
  scenario: string;
  character_role: string;
  difficulty_level: number;
  pressure_seconds: number;
  opening_message: string;
}

export interface RealLifeFeedback {
  correction: string;
  better_response: string;
  pressure_note: string;
  level_adaptation: string;
}

export interface RealLifeMessageResponse {
  session_id: number;
  status: 'active' | 'completed' | 'failed';
  ai_question: string;
  feedback: RealLifeFeedback;
  difficulty_level: number;
  pressure_seconds: number;
  turns_count: number;
  xp_awarded: number;
  bonus_breakdown: Record<string, number>;
  total_xp_session: number;
  updated_at: string;
}

export interface DailyChallengeInfo {
  day_date: string;
  challenge_title: string;
  scenario: string;
  difficulty_level: number;
  attempts_today: number;
  best_score_today: number;
  can_play_without_penalty: boolean;
  daily_badge_earned: boolean;
}

export interface DailyChallengeStartResponse {
  challenge_id: number;
  day_date: string;
  challenge_title: string;
  scenario: string;
  attempt_number: number;
  penalty_percent: number;
  session_id: number;
  character_role: string;
  difficulty_level: number;
  pressure_seconds: number;
  opening_message: string;
  started_at: string;
}

export interface DailyChallengeSubmitResponse {
  challenge_id: number;
  status: string;
  score: number;
  xp_awarded: number;
  bonus_breakdown: Record<string, number>;
  badge_awarded: boolean;
  attempts_today: number;
  best_score_today: number;
  finished_at: string;
}

export interface VoiceMentor {
  id: string;
  name: string;
  avatar: string;
  description: string;
  speaking_style: string;
  pedagogical_focus: string;
}

export interface VoiceMentorChatResponse {
  mentor_id: string;
  mentor_name: string;
  transcript: string;
  reply: string;
  tts_text: string;
  audio_available: boolean;
  voice_usage: VoiceUsage;
}

export interface VoiceUsage {
  plan: 'FREE' | 'PRO';
  used: number;
  limit?: number | null;
  remaining?: number | null;
  blocked: boolean;
  reset_on?: string | null;
}

export interface OAuthProviderStatus {
  provider: 'google' | 'apple' | string;
  enabled: boolean;
  authorization_url?: string | null;
}

export interface AdaptiveRecommendation {
  recommendation_type: string;
  title: string;
  description: string;
  locked_for_free: boolean;
}

export interface LearningTrackProgress {
  level: string;
  completed_units: number;
  total_units: number;
}

export interface PedagogyDashboardData {
  estimated_level: string;
  confidence: number;
  strengths: string[];
  weaknesses: string[];
  recurring_errors: string[];
  words_in_review: number;
  next_step: AdaptiveRecommendation;
  track_progress: LearningTrackProgress[];
  recommendations: AdaptiveRecommendation[];
}

export interface CurrentTrackData {
  track_slug: string;
  track_title: string;
  estimated_level: string;
  entry_profile: string;
  current_module_id?: number | null;
  current_lesson_id?: number | null;
  current_step_index?: number;
  resume_available?: boolean;
  next_lesson_id: number | null;
  completed_lessons: number;
  total_lessons: number;
}

export interface ModuleLessonStatus {
  id: number;
  title: string;
  status: string;
  current_step: number;
  total_steps: number;
}

export interface PedagogyModule {
  id: number;
  slug: string;
  title: string;
  progress_percent: number;
  lessons: ModuleLessonStatus[];
}

export interface LessonExample {
  en: string;
  pt: string;
}

export interface LessonExercise {
  id: string;
  type: string;
  prompt: string;
  hint_pt: string;
}

export interface LessonDetail {
  id: number;
  module_name: string;
  order_index: number;
  title: string;
  lesson_objective: string;
  cefr_level: string;
  estimated_duration_min: number;
  target_vocabulary: string[];
  key_structures: string[];
  grammar_explanation_pt: string;
  examples: LessonExample[];
  exercises: LessonExercise[];
  ai_context: Record<string, unknown>;
  final_review: string[];
  completion_criteria: {
    min_exercises_correct: number;
    min_conversation_turns: number;
    checkpoint_required: boolean;
  };
  progress: {
    current_step: number;
    total_steps: number;
    completed: boolean;
    score: number;
  };
}

export interface LessonSubmitResponse {
  lesson_id: number;
  completed: boolean;
  accuracy: number;
  next_review_at: string;
  next_step: string;
}

export interface LessonStepSaveResponse {
  lesson_id: number;
  current_step: number;
  total_steps: number;
  completed: boolean;
  score: number;
}

export interface ReviewTodayItem {
  id: number;
  queue_type: string;
  reference_id: number;
  priority: number;
  due_at: string;
}

export interface ReviewTodayData {
  items: ReviewTodayItem[];
  estimated_minutes: number;
}

export interface ProgressSummaryData {
  lesson_progress: { completed: number; total: number };
  module_completion: number;
  vocabulary_mastered: number;
  review_due: number;
  estimated_level: string;
  weekly_consistency: number;
}
