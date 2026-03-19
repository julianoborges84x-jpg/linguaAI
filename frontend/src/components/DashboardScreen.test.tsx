import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DashboardScreen from './DashboardScreen';

const baseUser = {
  id: 1,
  name: 'Maria',
  email: 'maria@example.com',
  plan: 'FREE' as const,
  xp_total: 120,
  level: 2,
  timezone: 'America/Sao_Paulo',
  onboarding_completed: true,
  target_language_code: 'en',
  subscription_status: 'inactive',
};

describe('DashboardScreen', () => {
  const growthData = {
    current_streak: 3,
    longest_streak: 7,
    xp_total: 120,
    level: 2,
    xp_in_level: 20,
    xp_to_next_level: 80,
    next_level: 3,
    mission_today: {
      day_date: '2026-03-16',
      target_sessions: 1,
      completed_sessions: 1,
      is_completed: true,
      bonus_xp_awarded: true,
    },
    weekly_progress: [],
    weekly_sessions_total: 4,
    weekly_minutes_total: 37,
    weekly_xp_total: 150,
    leaderboard_top: [{ rank: 1, user_id: 1, name: 'Maria', xp_week: 150, target_language_code: 'en' }],
    referral: {
      referral_code: 'ABC12345',
      referral_link: 'http://localhost:3000/?ref=ABC12345',
      referred_count: 2,
      reward_xp_total: 300,
    },
  };

  const dailyChallenge = {
    day_date: '2026-03-17',
    challenge_title: 'Desafio Diario: Pedido no Restaurante',
    scenario: 'restaurante',
    difficulty_level: 2,
    attempts_today: 0,
    best_score_today: 0,
    can_play_without_penalty: true,
    daily_badge_earned: false,
  };

  const pedagogyData = {
    estimated_level: 'A2',
    confidence: 0.78,
    strengths: ['vocabulary'],
    weaknesses: ['tense'],
    recurring_errors: ['tense (2)'],
    words_in_review: 4,
    next_step: {
      recommendation_type: 'continue_track',
      title: 'Basic Questions',
      description: 'Practice asking daily questions.',
      locked_for_free: false,
    },
    track_progress: [{ level: 'A2', completed_units: 0, total_units: 10 }],
    recommendations: [],
  };

  it('renderiza dados reais do usuario e inicia checkout', async () => {
    const onUpgrade = vi.fn();
    const user = userEvent.setup();

    render(
      <DashboardScreen
        user={baseUser}
        growthData={growthData}
        dailyChallenge={dailyChallenge}
        stripeConfigured
        billingLoading={false}
        onStartLesson={() => undefined}
        onOpenChat={() => undefined}
        onOpenImmersion={() => undefined}
        onOpenRealLife={() => undefined}
        onOpenDailyChallenge={() => undefined}
        onOpenReferral={() => undefined}
        onOpenVoiceMentor={() => undefined}
        onOpenSettings={() => undefined}
        onReferralCopy={() => undefined}
        onReferralSend={() => undefined}
        onUpgrade={onUpgrade}
        onManageSubscription={() => undefined}
        onCancelSubscription={() => undefined}
        onLogout={() => undefined}
      />,
    );

    expect(screen.getByText('Maria')).toBeInTheDocument();
    expect(screen.getByText(/Plano FREE/i)).toBeInTheDocument();
    expect(screen.getByText(/Ranking semanal/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Assinar plano PRO/i }));
    expect(onUpgrade).toHaveBeenCalled();
  });

  it('remove botao de assinar quando usuario ja e PRO e exibe status ativo', async () => {
    const onManageSubscription = vi.fn();
    const onCancelSubscription = vi.fn();
    const user = userEvent.setup();

    render(
      <DashboardScreen
        user={{ ...baseUser, plan: 'PRO', subscription_status: 'active' }}
        growthData={growthData}
        dailyChallenge={dailyChallenge}
        stripeConfigured
        billingLoading={false}
        onStartLesson={() => undefined}
        onOpenChat={() => undefined}
        onOpenImmersion={() => undefined}
        onOpenRealLife={() => undefined}
        onOpenDailyChallenge={() => undefined}
        onOpenReferral={() => undefined}
        onOpenVoiceMentor={() => undefined}
        onOpenSettings={() => undefined}
        onReferralCopy={() => undefined}
        onReferralSend={() => undefined}
        onUpgrade={() => undefined}
        onManageSubscription={onManageSubscription}
        onCancelSubscription={onCancelSubscription}
        onLogout={() => undefined}
        appError="Erro temporario no dashboard"
      />,
    );

    expect(screen.getByText(/Erro temporario no dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/Seu acesso PRO esta ativo/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Assinar plano PRO/i })).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Gerenciar assinatura PRO/i }));
    await user.click(screen.getByRole('button', { name: /Cancelar assinatura PRO/i }));
    expect(onManageSubscription).toHaveBeenCalled();
    expect(onCancelSubscription).toHaveBeenCalled();
  });

  it('executa os principais botoes de acao no dashboard FREE', async () => {
    const user = userEvent.setup();
    const handlers = {
      onStartLesson: vi.fn(),
      onOpenChat: vi.fn(),
      onOpenImmersion: vi.fn(),
      onOpenRealLife: vi.fn(),
      onOpenDailyChallenge: vi.fn(),
      onOpenReferral: vi.fn(),
      onOpenVoiceMentor: vi.fn(),
      onOpenSettings: vi.fn(),
      onReferralCopy: vi.fn(),
      onReferralSend: vi.fn(),
      onUpgrade: vi.fn(),
      onManageSubscription: vi.fn(),
      onCancelSubscription: vi.fn(),
      onLogout: vi.fn(),
    };

    render(
      <DashboardScreen
        user={baseUser}
        growthData={growthData}
        dailyChallenge={dailyChallenge}
        stripeConfigured
        billingLoading={false}
        onStartLesson={handlers.onStartLesson}
        onOpenChat={handlers.onOpenChat}
        onOpenImmersion={handlers.onOpenImmersion}
        onOpenRealLife={handlers.onOpenRealLife}
        onOpenDailyChallenge={handlers.onOpenDailyChallenge}
        onOpenReferral={handlers.onOpenReferral}
        onOpenVoiceMentor={handlers.onOpenVoiceMentor}
        onOpenSettings={handlers.onOpenSettings}
        onReferralCopy={handlers.onReferralCopy}
        onReferralSend={handlers.onReferralSend}
        onUpgrade={handlers.onUpgrade}
        onManageSubscription={handlers.onManageSubscription}
        onCancelSubscription={handlers.onCancelSubscription}
        onLogout={handlers.onLogout}
      />,
    );

    await user.click(screen.getByRole('button', { name: /Jogar agora/i }));
    await user.click(screen.getByRole('button', { name: /Experimentar voz gratis/i }));
    await user.click(screen.getByRole('button', { name: /Comecar agora/i }));
    await user.click(screen.getByRole('button', { name: /Abrir mentor chat/i }));
    await user.click(screen.getByRole('button', { name: /Abrir Immersion Engine/i }));
    await user.click(screen.getByRole('button', { name: /Modo Vida Real/i }));
    await user.click(screen.getByRole('button', { name: /Convide amigos/i }));
    await user.click(screen.getByRole('button', { name: /Copiar link/i }));
    await user.click(screen.getByRole('button', { name: /Enviar convite/i }));
    await user.click(screen.getByRole('button', { name: /Assinar plano PRO/i }));
    await user.click(screen.getByRole('button', { name: /Licoes/i }));
    await user.click(screen.getByRole('button', { name: /Imersao/i }));
    await user.click(screen.getAllByRole('button', { name: /Abrir configuracoes/i })[0]);

    expect(handlers.onOpenDailyChallenge).toHaveBeenCalled();
    expect(handlers.onUpgrade).toHaveBeenCalled();
    expect(handlers.onStartLesson).toHaveBeenCalled();
    expect(handlers.onOpenChat).toHaveBeenCalled();
    expect(handlers.onOpenImmersion).toHaveBeenCalled();
    expect(handlers.onOpenRealLife).toHaveBeenCalled();
    expect(handlers.onOpenReferral).toHaveBeenCalled();
    expect(handlers.onReferralCopy).toHaveBeenCalled();
    expect(handlers.onReferralSend).toHaveBeenCalled();
    expect(handlers.onOpenSettings).toHaveBeenCalled();
  }, 15000);

  it('renderiza cards pedagogicos com dados reais', async () => {
    render(
      <DashboardScreen
        user={baseUser}
        growthData={growthData}
        dailyChallenge={dailyChallenge}
        pedagogyData={pedagogyData}
        stripeConfigured
        billingLoading={false}
        onStartLesson={() => undefined}
        onOpenChat={() => undefined}
        onOpenImmersion={() => undefined}
        onOpenRealLife={() => undefined}
        onOpenDailyChallenge={() => undefined}
        onOpenReferral={() => undefined}
        onOpenVoiceMentor={() => undefined}
        onOpenSettings={() => undefined}
        onReferralCopy={() => undefined}
        onReferralSend={() => undefined}
        onUpgrade={() => undefined}
        onOpenPedagogyRecommendation={() => undefined}
        onOpenVocabularyReview={() => undefined}
        onManageSubscription={() => undefined}
        onCancelSubscription={() => undefined}
        onLogout={() => undefined}
      />,
    );

    expect(screen.getByText(/Seu nivel estimado/i)).toBeInTheDocument();
    expect(screen.getByText(/Proximo passo inteligente/i)).toBeInTheDocument();
    expect(screen.getByText(/Vocabulario em revisao/i)).toBeInTheDocument();
  });
});
