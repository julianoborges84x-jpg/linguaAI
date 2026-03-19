import { apiRequest, clearToken, getToken, storeToken } from './client';
import {
  AuthUser,
  BillingStatus,
  ChatHistoryItem,
  ChatResponse,
  CheckoutResponse,
  PedagogyDashboardData,
  DailyChallengeInfo,
  DailyChallengeStartResponse,
  DailyChallengeSubmitResponse,
  GrowthDashboardData,
  ImmersionDashboardData,
  ImmersionFinishResponse,
  ImmersionMission,
  ImmersionScenario,
  ImmersionStartResponse,
  ImmersionTurnResponse,
  RealLifeMessageResponse,
  RealLifeSessionStart,
  ReferralMe,
  ReferralStats,
  RoleplayCharacter,
  SessionFinishResponse,
  SessionStartResponse,
  SessionTopic,
  OAuthProviderStatus,
  VoiceMentor,
  VoiceMentorChatResponse,
  VoiceUsage,
} from '../types';

export async function register(name: string, email: string, password: string, referralCode?: string | null) {
  return apiRequest<AuthUser>('/users', {
    method: 'POST',
    body: JSON.stringify({ name, email, password, referral_code: referralCode || undefined }),
  });
}

export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const payload = await apiRequest<{ access_token: string; token_type: string }>('/auth/login', {
    method: 'POST',
    body: formData.toString(),
    isForm: true,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  storeToken(payload.access_token);
  return payload;
}

export async function fetchOAuthProviders() {
  return apiRequest<OAuthProviderStatus[]>('/auth/oauth/providers', {
    method: 'GET',
  });
}

export async function oauthLogin(provider: 'google' | 'apple', code: string, state: string) {
  const payload = await apiRequest<{ access_token: string; token_type: string; user: AuthUser }>(`/auth/oauth/${provider}/callback`, {
    method: 'POST',
    body: JSON.stringify({ code, state }),
  });

  storeToken(payload.access_token);
  return payload;
}

export async function fetchCurrentUser() {
  if (!getToken()) {
    throw new Error('Sessao ausente.');
  }

  try {
    return await apiRequest<AuthUser>('/users/me', {
      method: 'GET',
      authenticated: true,
    });
  } catch (error) {
    clearToken();
    throw error;
  }
}

export async function updateOnboarding(payload: { target_language: 'en' | 'es' | 'fr' | 'it'; timezone: string }) {
  return apiRequest<AuthUser>('/users/me', {
    method: 'PATCH',
    authenticated: true,
    body: JSON.stringify(payload),
  });
}

export async function fetchBillingStatus() {
  return apiRequest<BillingStatus>('/billing/status', {
    method: 'GET',
    authenticated: true,
  });
}

export async function createCheckoutSession() {
  return apiRequest<CheckoutResponse>('/billing/create-checkout-session', {
    method: 'POST',
    authenticated: true,
  });
}

export async function createPortalSession() {
  return apiRequest<{ portal_url: string; url: string }>('/billing/create-portal-session', {
    method: 'POST',
    authenticated: true,
  });
}

export async function cancelSubscription() {
  return apiRequest<{ ok: boolean }>('/billing/cancel-subscription', {
    method: 'POST',
    authenticated: true,
  });
}

export async function fetchSessionTopics() {
  return apiRequest<SessionTopic[]>('/sessions/topics', {
    method: 'GET',
    authenticated: true,
  });
}

export async function startLessonSession() {
  const topics = await fetchSessionTopics();
  const firstTopicId = topics.length > 0 ? topics[0].id : null;
  return apiRequest<SessionStartResponse>('/sessions/start', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ mode: 'writing', topic_id: firstTopicId }),
  });
}

export async function finishLessonSession(sessionId: number, interactionsCount: number) {
  return apiRequest<SessionFinishResponse>(`/sessions/${sessionId}/finish`, {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ interactions_count: interactionsCount }),
  });
}

export async function sendChatMessage(message: string) {
  return apiRequest<ChatResponse>('/mentor/chat', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ message, feature: 'writing' }),
  });
}

export async function fetchChatHistory() {
  return apiRequest<ChatHistoryItem[]>('/mentor/history', {
    method: 'GET',
    authenticated: true,
  });
}

export async function fetchGrowthDashboard() {
  return apiRequest<GrowthDashboardData>('/growth/dashboard', {
    method: 'GET',
    authenticated: true,
  });
}

export async function trackGrowthEvent(eventType: string, payload?: Record<string, unknown>) {
  return apiRequest<{ id: number; event_type: string; created_at: string }>('/growth/events', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ event_type: eventType, payload }),
  });
}

export async function trackPublicGrowthEvent(
  eventType: 'hero_cta_click' | 'demo_cta_click' | 'final_cta_click' | 'landing_variant_exposed' | 'referral_link_opened',
  payload?: Record<string, unknown>,
) {
  return apiRequest<{ id: number; event_type: string; created_at: string }>('/growth/events/public', {
    method: 'POST',
    body: JSON.stringify({ event_type: eventType, payload }),
  });
}

export async function fetchImmersionScenarios() {
  return apiRequest<ImmersionScenario[]>('/immersion/scenarios', {
    method: 'GET',
    authenticated: true,
  });
}

export async function fetchScenarioCharacters(scenarioSlug: string) {
  return apiRequest<RoleplayCharacter[]>(`/immersion/scenarios/${scenarioSlug}/characters`, {
    method: 'GET',
    authenticated: true,
  });
}

export async function fetchImmersionDashboard() {
  return apiRequest<ImmersionDashboardData>('/immersion/dashboard', {
    method: 'GET',
    authenticated: true,
  });
}

export async function fetchImmersionMissions() {
  return apiRequest<ImmersionMission[]>('/immersion/missions', {
    method: 'GET',
    authenticated: true,
  });
}

export async function startImmersionSession(scenarioSlug: string, characterId?: number | null) {
  return apiRequest<ImmersionStartResponse>('/immersion/sessions/start', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ scenario_slug: scenarioSlug, character_id: characterId || undefined, source: 'mobile' }),
  });
}

export async function sendImmersionTurn(sessionId: number, message: string) {
  return apiRequest<ImmersionTurnResponse>(`/immersion/sessions/${sessionId}/turn`, {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ message }),
  });
}

export async function finishImmersionSession(sessionId: number) {
  return apiRequest<ImmersionFinishResponse>(`/immersion/sessions/${sessionId}/finish`, {
    method: 'POST',
    authenticated: true,
  });
}

export async function claimImmersionMission(missionId: number) {
  return apiRequest<{ mission_id: number; status: string; xp_reward: number; new_xp_total: number; new_level: number }>(`/immersion/missions/${missionId}/claim`, {
    method: 'POST',
    authenticated: true,
  });
}

export async function startRealLifeSession(scenario: string, retrySessionId?: number | null) {
  return apiRequest<RealLifeSessionStart>('/real-life/session', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ scenario, retry_session_id: retrySessionId || undefined }),
  });
}

export async function sendRealLifeMessage(sessionId: number, message: string, responseTimeSeconds: number) {
  return apiRequest<RealLifeMessageResponse>('/real-life/message', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ session_id: sessionId, message, response_time_seconds: responseTimeSeconds }),
  });
}

export async function fetchDailyChallenge() {
  return apiRequest<DailyChallengeInfo>('/daily-challenge', {
    method: 'GET',
    authenticated: true,
  });
}

export async function startDailyChallenge() {
  return apiRequest<DailyChallengeStartResponse>('/daily-challenge/start', {
    method: 'POST',
    authenticated: true,
  });
}

export async function submitDailyChallenge(challengeId: number) {
  return apiRequest<DailyChallengeSubmitResponse>('/daily-challenge/submit', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ challenge_id: challengeId }),
  });
}

export async function fetchReferralMe() {
  return apiRequest<ReferralMe>('/referral/me', {
    method: 'GET',
    authenticated: true,
  });
}

export async function fetchReferralStats() {
  return apiRequest<ReferralStats>('/referral/stats', {
    method: 'GET',
    authenticated: true,
  });
}

export async function applyReferralCode(referralCode: string) {
  return apiRequest<{ applied: boolean; referred_by?: number | null; xp_total: number; level: number; pro_access_until?: string | null }>('/referral/apply', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ referral_code: referralCode }),
  });
}

export async function fetchVoiceMentors() {
  return apiRequest<VoiceMentor[]>('/mentor/voice/mentors', {
    method: 'GET',
    authenticated: true,
  });
}

export async function sendVoiceMentorMessage(mentorId: string, message: string) {
  return apiRequest<VoiceMentorChatResponse>('/mentor/voice/chat', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify({ mentor_id: mentorId, message }),
  });
}

export async function fetchVoiceUsage() {
  return apiRequest<VoiceUsage>('/mentor/voice/usage', {
    method: 'GET',
    authenticated: true,
  });
}

export async function fetchPedagogyDashboard() {
  return apiRequest<PedagogyDashboardData>('/pedagogy/dashboard', {
    method: 'GET',
    authenticated: true,
  });
}

export async function fetchAdaptiveRecommendations() {
  return apiRequest<PedagogyDashboardData['recommendations']>('/pedagogy/recommendations', {
    method: 'GET',
    authenticated: true,
  });
}

export { clearToken, getToken, storeToken };
