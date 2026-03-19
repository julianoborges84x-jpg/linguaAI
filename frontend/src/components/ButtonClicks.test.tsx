import { cleanup, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

import ChatScreen from './ChatScreen';
import CreatingPlanScreen from './CreatingPlanScreen';
import DailyChallengeScreen from './DailyChallengeScreen';
import ImmersionScreen from './ImmersionScreen';
import LanguageSelectScreen from './LanguageSelectScreen';
import LearningGoalScreen from './LearningGoalScreen';
import LessonScreen from './LessonScreen';
import ProficiencyLevelScreen from './ProficiencyLevelScreen';
import RealLifeScreen from './RealLifeScreen';
import ReferralPromptModal from './ReferralPromptModal';
import VoiceMentorPicker from './VoiceMentorPicker';
import WelcomeScreen from './WelcomeScreen';

const fetchChatHistoryMock = vi.fn();
const startLessonSessionMock = vi.fn();
const finishLessonSessionMock = vi.fn();
const fetchDailyChallengeMock = vi.fn();
const startDailyChallengeMock = vi.fn();
const sendRealLifeMessageMock = vi.fn();
const submitDailyChallengeMock = vi.fn();
const fetchImmersionScenariosMock = vi.fn();
const fetchImmersionMissionsMock = vi.fn();
const fetchImmersionDashboardMock = vi.fn();
const fetchScenarioCharactersMock = vi.fn();
const startImmersionSessionMock = vi.fn();
const sendImmersionTurnMock = vi.fn();
const finishImmersionSessionMock = vi.fn();
const claimImmersionMissionMock = vi.fn();
const startRealLifeSessionMock = vi.fn();
const sendChatMessageMock = vi.fn();

vi.mock('../api/auth', () => ({
  fetchChatHistory: (...args: unknown[]) => fetchChatHistoryMock(...args),
  startLessonSession: (...args: unknown[]) => startLessonSessionMock(...args),
  finishLessonSession: (...args: unknown[]) => finishLessonSessionMock(...args),
  fetchDailyChallenge: (...args: unknown[]) => fetchDailyChallengeMock(...args),
  startDailyChallenge: (...args: unknown[]) => startDailyChallengeMock(...args),
  sendRealLifeMessage: (...args: unknown[]) => sendRealLifeMessageMock(...args),
  submitDailyChallenge: (...args: unknown[]) => submitDailyChallengeMock(...args),
  fetchImmersionScenarios: (...args: unknown[]) => fetchImmersionScenariosMock(...args),
  fetchImmersionMissions: (...args: unknown[]) => fetchImmersionMissionsMock(...args),
  fetchImmersionDashboard: (...args: unknown[]) => fetchImmersionDashboardMock(...args),
  fetchScenarioCharacters: (...args: unknown[]) => fetchScenarioCharactersMock(...args),
  startImmersionSession: (...args: unknown[]) => startImmersionSessionMock(...args),
  sendImmersionTurn: (...args: unknown[]) => sendImmersionTurnMock(...args),
  finishImmersionSession: (...args: unknown[]) => finishImmersionSessionMock(...args),
  claimImmersionMission: (...args: unknown[]) => claimImmersionMissionMock(...args),
  startRealLifeSession: (...args: unknown[]) => startRealLifeSessionMock(...args),
  sendChatMessage: (...args: unknown[]) => sendChatMessageMock(...args),
}));

const authUser = {
  id: 1,
  name: 'Maria',
  email: 'maria@example.com',
  plan: 'FREE' as const,
  xp_total: 100,
  level: 1,
  timezone: 'America/Sao_Paulo',
  onboarding_completed: true,
  target_language_code: 'en',
};

describe('Button click coverage', () => {
  beforeEach(() => {
    vi.useRealTimers();
    fetchChatHistoryMock.mockReset();
    startLessonSessionMock.mockReset();
    finishLessonSessionMock.mockReset();
    fetchDailyChallengeMock.mockReset();
    startDailyChallengeMock.mockReset();
    sendRealLifeMessageMock.mockReset();
    submitDailyChallengeMock.mockReset();
    fetchImmersionScenariosMock.mockReset();
    fetchImmersionMissionsMock.mockReset();
    fetchImmersionDashboardMock.mockReset();
    fetchScenarioCharactersMock.mockReset();
    startImmersionSessionMock.mockReset();
    sendImmersionTurnMock.mockReset();
    finishImmersionSessionMock.mockReset();
    claimImmersionMissionMock.mockReset();
    startRealLifeSessionMock.mockReset();
    sendChatMessageMock.mockReset();
  });

  it('onboarding screens respond to button clicks', async () => {
    const user = userEvent.setup();
    const onStart = vi.fn();
    const onBack = vi.fn();
    const onNext = vi.fn();

    const welcomeView = render(<WelcomeScreen onStart={onStart} />);
    const welcomeButtons = screen.getAllByRole('button');
    for (const button of welcomeButtons) await user.click(button);
    expect(onStart).toHaveBeenCalled();
    welcomeView.unmount();

    const languageView = render(<LanguageSelectScreen onBack={onBack} onNext={onNext} />);
    const languageButtons = screen.getAllByRole('button');
    await user.click(languageButtons[0]);
    await user.click(screen.getByRole('button', { name: /continuar/i }));
    expect(onNext).not.toHaveBeenCalled();
    await user.click(screen.getByText('Inglês'));
    await user.click(screen.getByRole('button', { name: /continuar/i }));
    expect(onBack).toHaveBeenCalled();
    expect(onNext).toHaveBeenCalledWith('ingles');
    languageView.unmount();

    const proficiencyView = render(<ProficiencyLevelScreen onBack={onBack} onNext={onNext} />);
    await user.click(screen.getByRole('button', { name: /continuar/i }));
    await user.click(screen.getByText('Intermediário'));
    await user.click(screen.getByRole('button', { name: /continuar/i }));
    expect(onNext).toHaveBeenCalledWith('intermediario');
    proficiencyView.unmount();

    const goalView = render(<LearningGoalScreen onBack={onBack} onNext={onNext} />);
    await user.click(screen.getByRole('button', { name: /continuar/i }));
    await user.click(screen.getByRole('button', { name: /Viagens/i }));
    await user.click(screen.getByRole('button', { name: /continuar/i }));
    expect(onNext).toHaveBeenCalledWith('viagens');
    goalView.unmount();

    cleanup();
  });

  it('creating plan button unlocks and handles click', async () => {
    vi.useRealTimers();
    const user = userEvent.setup();
    const onComplete = vi.fn();
    const randomSpy = vi.spyOn(Math, 'random').mockReturnValue(1);
    const planView = render(<CreatingPlanScreen profile={{ language: 'ingles', level: 'intermediario', goal: 'viagens' }} onComplete={onComplete} />);
    const finishBtn = await screen.findByRole('button', { name: /ver meu plano/i }, { timeout: 8000 });
    await waitFor(() => expect(finishBtn).not.toBeDisabled(), { timeout: 8000 });
    await user.click(finishBtn);
    expect(onComplete).toHaveBeenCalled();
    randomSpy.mockRestore();
    planView.unmount();
    cleanup();
  }, 12000);

  it('chat and lesson buttons are clickable and trigger expected actions', async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    const onFinish = vi.fn();

    fetchChatHistoryMock.mockResolvedValue([{ id: 1, feature: 'writing', created_at: '2026-03-18', preview: 'historico' }]);
    sendChatMessageMock.mockResolvedValue({ reply: 'Resposta da IA' });

    const chatView = render(<ChatScreen user={authUser} onBack={onBack} />);
    await user.click(screen.getByRole('button', { name: /voltar ao dashboard/i }));
    expect(onBack).toHaveBeenCalled();
    await user.type(screen.getByPlaceholderText(/digite sua mensagem/i), 'hello');
    const sendButtons = screen.getAllByRole('button').filter((button) => button.className.includes('absolute right-2'));
    await user.click(sendButtons[0]);
    expect(await screen.findByText('Resposta da IA')).toBeInTheDocument();
    chatView.unmount();

    startLessonSessionMock.mockResolvedValue({ session_id: 33 });
    finishLessonSessionMock.mockResolvedValue({ session_id: 33 });
    const lessonView = render(<LessonScreen onFinish={onFinish} />);
    await screen.findByText(/Sessao #33/i);
    await user.click(screen.getByRole('button', { name: 'sobre a' }));
    await user.click(screen.getByRole('button', { name: /verificar/i }));
    await user.click(screen.getByRole('button', { name: /continuar/i }));
    await waitFor(() => expect(finishLessonSessionMock).toHaveBeenCalled());
    lessonView.unmount();
    cleanup();
  });

  it('daily challenge and real life screens handle button clicks', async () => {
    const user = userEvent.setup();
    fetchDailyChallengeMock.mockResolvedValue({
      day_date: '2026-03-18',
      challenge_title: 'Desafio',
      scenario: 'restaurante',
      difficulty_level: 2,
      attempts_today: 0,
      best_score_today: 0,
      can_play_without_penalty: true,
      daily_badge_earned: false,
    });
    startDailyChallengeMock.mockResolvedValue({
      challenge_id: 8,
      day_date: '2026-03-18',
      challenge_title: 'Desafio',
      scenario: 'restaurante',
      attempt_number: 1,
      penalty_percent: 0,
      session_id: 90,
      character_role: 'Waiter',
      difficulty_level: 2,
      pressure_seconds: 30,
      opening_message: 'Hello!',
      started_at: '2026-03-18T10:00:00Z',
    });
    sendRealLifeMessageMock.mockResolvedValue({
      session_id: 90,
      status: 'active',
      ai_question: 'What do you want?',
      feedback: { correction: 'ok', better_response: 'I would like...', pressure_note: 'good', level_adaptation: 'up' },
      difficulty_level: 2,
      pressure_seconds: 25,
      turns_count: 1,
      xp_awarded: 20,
      bonus_breakdown: {},
      total_xp_session: 20,
      updated_at: '2026-03-18T10:00:10Z',
    });
    submitDailyChallengeMock.mockResolvedValue({
      challenge_id: 8,
      status: 'completed',
      score: 88,
      xp_awarded: 50,
      bonus_breakdown: {},
      badge_awarded: true,
      attempts_today: 1,
      best_score_today: 88,
      finished_at: '2026-03-18T10:01:00Z',
    });

    const challengeView = render(<DailyChallengeScreen onBack={() => undefined} />);
    await user.click(screen.getByRole('button', { name: /jogar agora/i }));
    await user.type(screen.getByPlaceholderText(/responda em ingles/i), 'I want pasta');
    const challengeSend = screen.getAllByRole('button').find((button) => button.className.includes('rounded-lg bg-primary'));
    if (!challengeSend) throw new Error('challenge send button not found');
    await user.click(challengeSend);
    await user.click(screen.getByRole('button', { name: /finalizar desafio/i }));
    expect(await screen.findByText(/resultado do desafio/i)).toBeInTheDocument();
    challengeView.unmount();

    startRealLifeSessionMock.mockResolvedValue({
      session_id: 100,
      scenario: 'Restaurante',
      character_role: 'Waiter',
      difficulty_level: 1,
      pressure_seconds: 20,
      opening_message: 'Welcome',
    });
    sendRealLifeMessageMock.mockResolvedValue({
      session_id: 100,
      status: 'active',
      ai_question: 'Anything else?',
      feedback: { correction: 'ok', better_response: 'Could I have...', pressure_note: 'fast', level_adaptation: 'steady' },
      difficulty_level: 1,
      pressure_seconds: 18,
      turns_count: 1,
      xp_awarded: 10,
      bonus_breakdown: {},
      total_xp_session: 10,
      updated_at: '2026-03-18T10:02:00Z',
    });
    const realLifeView = render(<RealLifeScreen onBack={() => undefined} />);
    await user.click(screen.getByRole('button', { name: /aeroporto/i }));
    await user.click(screen.getByRole('button', { name: /iniciar simulacao/i }));
    await user.type(screen.getByPlaceholderText(/responda rapido/i), 'Hi');
    const realLifeSend = screen.getAllByRole('button').find((button) => button.className.includes('rounded-lg bg-primary'));
    if (!realLifeSend) throw new Error('real life send button not found');
    await user.click(realLifeSend);
    await user.click(screen.getByRole('button', { name: /tentar novamente/i }));
    await user.click(screen.getByRole('button', { name: /mudar cenario/i }));
    realLifeView.unmount();
    cleanup();
  });

  it('immersion, referral modal and mentor picker buttons are clickable', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const onCopy = vi.fn();
    const onSend = vi.fn();
    const onOpenReferral = vi.fn();

    fetchImmersionScenariosMock.mockResolvedValue([{ id: 1, slug: 'airport', title: 'Aeroporto', category: 'travel', difficulty: 'medium' }]);
    fetchImmersionMissionsMock.mockResolvedValue([{ id: 7, slug: 'm1', title: 'Missao', description: 'desc', scenario_slug: 'airport', xp_reward: 50, status: 'active' }]);
    fetchImmersionDashboardMock.mockResolvedValue({
      fluency_level: 'Explorer',
      latest_fluency_score: 55,
      tutor_insights: {
        frequent_errors: [],
        weak_vocabulary: [],
        pronunciation_gaps: [],
        confidence_score: 50,
        avg_speaking_speed_wpm: 90,
        adaptation_plan: [],
      },
      recommended_scenarios: [],
      missions: [],
      growth_loops: [],
    });
    fetchScenarioCharactersMock.mockResolvedValue([{ id: 3, name: 'Alex', personality: 'calm', accent: 'US', objective: 'help', difficulty: 'medium' }]);
    startImmersionSessionMock.mockResolvedValue({ session_id: 10, scenario_slug: 'airport', opening_message: 'Welcome', character: null });
    sendImmersionTurnMock.mockResolvedValue({ session_id: 10, ai_reply: 'Tell me more', hints: ['hint 1'], turn_number: 1 });
    finishImmersionSessionMock.mockResolvedValue({
      session_id: 10,
      fluency_score: 60,
      confidence_score: 58,
      speaking_speed_wpm: 92,
      filler_words_count: 2,
      grammar_mistakes: 1,
      pronunciation_score: 75,
      fluency_level: 'Explorer',
      recommended_focus: ['phrases'],
      share_token: null,
    });
    claimImmersionMissionMock.mockResolvedValue({ mission_id: 7, status: 'completed', xp_reward: 50, new_xp_total: 500, new_level: 5 });

    const immersionView = render(<ImmersionScreen onBack={() => undefined} />);
    await screen.findByText(/IMMERSION ENGINE/i);
    await user.click(screen.getByRole('button', { name: /aeroporto/i }));
    await user.click(screen.getByRole('button', { name: /iniciar roleplay/i }));
    await user.type(screen.getByPlaceholderText(/digite sua resposta/i), 'Hi there');
    await user.click(screen.getByRole('button', { name: /enviar/i }));
    await user.click(screen.getByRole('button', { name: /finalizar e analisar fluencia/i }));
    expect(await screen.findByText(/Analise de fluencia/i)).toBeInTheDocument();
    immersionView.unmount();

    const modalView = render(
      <ReferralPromptModal
        open
        trigger="xp_gained"
        onClose={onClose}
        onCopy={onCopy}
        onSend={onSend}
        onOpenReferral={onOpenReferral}
      />,
    );
    const modal = screen.getByText(/Referral Boost/i).closest('div')?.parentElement?.parentElement;
    if (!modal) throw new Error('modal not found');
    const modalScope = within(modal);
    await user.click(screen.getByRole('button', { name: /copiar link/i }));
    await user.click(screen.getByRole('button', { name: /enviar convite/i }));
    await user.click(screen.getByRole('button', { name: /ver painel completo de indicacoes/i }));
    await user.click(modalScope.getAllByRole('button')[0]);
    expect(onCopy).toHaveBeenCalled();
    expect(onSend).toHaveBeenCalled();
    expect(onOpenReferral).toHaveBeenCalled();
    expect(onClose).toHaveBeenCalled();
    modalView.unmount();

    const onSelect = vi.fn();
    const pickerView = render(
      <MemoryRouter>
        <VoiceMentorPicker
          mentors={[
            { id: 'clara', name: 'Clara', avatar: 'a', description: 'd', speaking_style: 's', pedagogical_focus: 'f' },
            { id: 'maya', name: 'Maya', avatar: 'b', description: 'd2', speaking_style: 's2', pedagogical_focus: 'f2' },
          ]}
          selectedMentorId="clara"
          onSelect={onSelect}
        />
      </MemoryRouter>,
    );
    await user.click(screen.getByRole('button', { name: /Maya/i }));
    expect(onSelect).toHaveBeenCalledWith('maya');
    pickerView.unmount();
    cleanup();
  });
});
