import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

const fetchCurrentUserMock = vi.fn();
const fetchBillingStatusMock = vi.fn();
const fetchGrowthDashboardMock = vi.fn();
const fetchDailyChallengeMock = vi.fn();
const fetchPedagogyDashboardMock = vi.fn();
const fetchAdaptiveRecommendationsMock = vi.fn();
const fetchCurrentTrackMock = vi.fn();
const fetchPedagogyModulesMock = vi.fn();
const fetchReviewTodayMock = vi.fn();
const fetchProgressSummaryMock = vi.fn();
const trackPublicGrowthEventMock = vi.fn();

vi.mock('./api/auth', async () => {
  const actual = await vi.importActual<typeof import('./api/auth')>('./api/auth');
  return {
    ...actual,
    clearToken: vi.fn(),
    createCheckoutSession: vi.fn(),
    fetchBillingStatus: (...args: unknown[]) => fetchBillingStatusMock(...args),
    fetchCurrentUser: (...args: unknown[]) => fetchCurrentUserMock(...args),
    fetchGrowthDashboard: (...args: unknown[]) => fetchGrowthDashboardMock(...args),
    fetchDailyChallenge: (...args: unknown[]) => fetchDailyChallengeMock(...args),
    fetchPedagogyDashboard: (...args: unknown[]) => fetchPedagogyDashboardMock(...args),
    fetchAdaptiveRecommendations: (...args: unknown[]) => fetchAdaptiveRecommendationsMock(...args),
    fetchCurrentTrack: (...args: unknown[]) => fetchCurrentTrackMock(...args),
    fetchPedagogyModules: (...args: unknown[]) => fetchPedagogyModulesMock(...args),
    fetchReviewToday: (...args: unknown[]) => fetchReviewTodayMock(...args),
    fetchProgressSummary: (...args: unknown[]) => fetchProgressSummaryMock(...args),
    fetchPedagogyLesson: vi.fn(),
    fetchPedagogyModule: vi.fn(),
    submitPedagogyLesson: vi.fn(),
    submitReviewToday: vi.fn(),
    getToken: vi.fn(() => localStorage.getItem('token')),
    storeToken: vi.fn((token: string) => localStorage.setItem('token', token)),
    trackPublicGrowthEvent: (...args: unknown[]) => trackPublicGrowthEventMock(...args),
    trackGrowthEvent: vi.fn(),
    updateOnboarding: vi.fn(),
  };
});

describe('App routes', () => {
  beforeEach(() => {
    fetchCurrentUserMock.mockReset();
    fetchBillingStatusMock.mockReset();
    fetchGrowthDashboardMock.mockReset();
    fetchDailyChallengeMock.mockReset();
    fetchPedagogyDashboardMock.mockReset();
    fetchAdaptiveRecommendationsMock.mockReset();
    fetchCurrentTrackMock.mockReset();
    fetchPedagogyModulesMock.mockReset();
    fetchReviewTodayMock.mockReset();
    fetchProgressSummaryMock.mockReset();
    trackPublicGrowthEventMock.mockReset();
    fetchPedagogyDashboardMock.mockResolvedValue(null);
    fetchAdaptiveRecommendationsMock.mockResolvedValue([]);
    fetchCurrentTrackMock.mockResolvedValue({
      track_slug: 'english-foundations-a1',
      track_title: 'English Foundations A1',
      estimated_level: 'A1',
      entry_profile: 'absolute beginner',
      next_lesson_id: 1,
      completed_lessons: 0,
      total_lessons: 24,
    });
    fetchPedagogyModulesMock.mockResolvedValue([]);
    fetchReviewTodayMock.mockResolvedValue({ items: [], estimated_minutes: 5 });
    fetchProgressSummaryMock.mockResolvedValue({
      lesson_progress: { completed: 0, total: 24 },
      module_completion: 0,
      vocabulary_mastered: 0,
      review_due: 0,
      estimated_level: 'A1',
      weekly_consistency: 0,
    });
    localStorage.clear();
    window.history.pushState({}, '', '/');
  });

  const growthBase = {
    current_streak: 1,
    longest_streak: 1,
    xp_total: 100,
    level: 1,
    xp_in_level: 0,
    xp_to_next_level: 100,
    next_level: 2,
    mission_today: {
      day_date: '2026-03-16',
      target_sessions: 1,
      completed_sessions: 0,
      is_completed: false,
      bonus_xp_awarded: false,
    },
    weekly_progress: [],
    weekly_sessions_total: 0,
    weekly_minutes_total: 0,
    weekly_xp_total: 0,
    leaderboard_top: [],
    referral: {
      referral_code: 'ABCD1234',
      referral_link: 'http://localhost:3000/?ref=ABCD1234',
      referred_count: 0,
      reward_xp_total: 0,
    },
  };

  const dailyChallengeBase = {
    day_date: '2026-03-17',
    challenge_title: 'Desafio Diario: Pedido no Restaurante',
    scenario: 'restaurante',
    difficulty_level: 1,
    attempts_today: 0,
    best_score_today: 0,
    can_play_without_penalty: true,
    daily_badge_earned: false,
  };

  const pedagogyBase = {
    estimated_level: 'A2',
    confidence: 0.72,
    strengths: ['vocabulary'],
    weaknesses: ['tense'],
    recurring_errors: ['tense (2)'],
    words_in_review: 3,
    next_step: {
      recommendation_type: 'continue_track',
      title: 'Basic Questions',
      description: 'Practice asking daily questions.',
      locked_for_free: false,
    },
    track_progress: [{ level: 'A2', completed_units: 0, total_units: 12 }],
    recommendations: [],
  };

  it('abre landing em / e CTA principal leva para /login', async () => {
    fetchCurrentUserMock.mockRejectedValue(new Error('Sessao ausente.'));
    const user = userEvent.setup();

    render(<App />);

    expect(await screen.findByText(/Fale ingles com IA. De verdade./i)).toBeInTheDocument();
    await user.click(screen.getAllByRole('link', { name: /Comecar gratis agora/i })[0]);
    expect(await screen.findByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    expect(window.location.pathname).toBe('/login');
  });

  it('abre dashboard em /dashboard quando usuario autenticado', async () => {
    localStorage.setItem('token', 'jwt-valid');
    window.history.pushState({}, '', '/dashboard');

    fetchCurrentUserMock.mockResolvedValue({
      id: 1,
      name: 'Maria',
      email: 'maria@example.com',
      plan: 'PRO',
      xp_total: 450,
      level: 4,
      timezone: 'America/Sao_Paulo',
      onboarding_completed: true,
      target_language_code: 'en',
      subscription_status: 'active',
    });
    fetchBillingStatusMock.mockResolvedValue({
      stripe_configured: true,
      plan: 'PRO',
      subscription_status: 'active',
    });
    fetchGrowthDashboardMock.mockResolvedValue(growthBase);
    fetchDailyChallengeMock.mockResolvedValue(dailyChallengeBase);
    fetchPedagogyDashboardMock.mockResolvedValue(pedagogyBase);

    render(<App />);

    await waitFor(() => expect(screen.getByText(/Hello,\s*Maria/i)).toBeInTheDocument());
    expect(screen.getByText(/Painel de Aprendizagem/i)).toBeInTheDocument();
    expect(window.location.pathname).toBe('/dashboard');
  });

  it('redireciona /dashboard para /login quando nao autenticado', async () => {
    window.history.pushState({}, '', '/dashboard');
    fetchCurrentUserMock.mockRejectedValue(new Error('Sessao ausente.'));

    render(<App />);

    expect(await screen.findByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    expect(window.location.pathname).toBe('/login');
  });

  it('sincroniza checkout=success no dashboard sem quebrar rota', async () => {
    localStorage.setItem('token', 'jwt-valid');
    window.history.pushState({}, '', '/dashboard?checkout=success');

    fetchCurrentUserMock
      .mockResolvedValueOnce({
        id: 1,
        name: 'Maria',
        email: 'maria@example.com',
        plan: 'FREE',
        xp_total: 100,
        level: 1,
        timezone: 'America/Sao_Paulo',
        onboarding_completed: true,
        target_language_code: 'en',
        subscription_status: 'inactive',
      })
      .mockResolvedValueOnce({
        id: 1,
        name: 'Maria',
        email: 'maria@example.com',
        plan: 'PRO',
        xp_total: 120,
        level: 2,
        timezone: 'America/Sao_Paulo',
        onboarding_completed: true,
        target_language_code: 'en',
        subscription_status: 'active',
      });
    fetchBillingStatusMock
      .mockResolvedValueOnce({
        stripe_configured: true,
        plan: 'FREE',
        subscription_status: 'inactive',
      })
      .mockResolvedValueOnce({
        stripe_configured: true,
        plan: 'PRO',
        subscription_status: 'active',
      });
    fetchGrowthDashboardMock
      .mockResolvedValueOnce(growthBase)
      .mockResolvedValueOnce({ ...growthBase, xp_total: 120, level: 2, xp_in_level: 20, xp_to_next_level: 80 });
    fetchDailyChallengeMock.mockResolvedValue(dailyChallengeBase);
    fetchPedagogyDashboardMock.mockResolvedValue(pedagogyBase);

    render(<App />);

    expect(await screen.findByText(/Assinatura PRO confirmada com sucesso/i, {}, { timeout: 4000 })).toBeInTheDocument();
    expect(window.location.pathname).toBe('/dashboard');
    expect(window.location.search).toBe('');
  });

  it('abre paginas de privacidade e termos via rotas publicas', async () => {
    fetchCurrentUserMock.mockRejectedValue(new Error('Sessao ausente.'));

    window.history.pushState({}, '', '/privacy');
    const { unmount } = render(<App />);
    expect(await screen.findByText(/Privacidade/i)).toBeInTheDocument();
    unmount();

    window.history.pushState({}, '', '/terms');
    render(<App />);
    expect(await screen.findByText(/Termos de Uso/i)).toBeInTheDocument();
  });

  it('salva codigo em /invite/:code e redireciona para /login', async () => {
    fetchCurrentUserMock.mockRejectedValue(new Error('Sessao ausente.'));
    window.history.pushState({}, '', '/invite/lingua123');

    render(<App />);

    expect(await screen.findByRole('button', { name: /Sign In/i })).toBeInTheDocument();
    expect(window.location.pathname).toBe('/login');
    expect(localStorage.getItem('lingua_referral_code')).toBe('lingua123');
    expect(trackPublicGrowthEventMock).toHaveBeenCalledWith('referral_link_opened', { referral_code: 'lingua123' });
  });
});
