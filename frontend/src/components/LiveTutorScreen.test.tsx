import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import LiveTutorScreen from './LiveTutorScreen';

const fetchVoiceMentorsMock = vi.fn();
const fetchVoiceUsageMock = vi.fn();
const sendVoiceMentorMessageMock = vi.fn();
const sendChatMessageMock = vi.fn();
const trackGrowthEventMock = vi.fn();

vi.mock('../api/auth', () => ({
  fetchVoiceMentors: (...args: unknown[]) => fetchVoiceMentorsMock(...args),
  fetchVoiceUsage: (...args: unknown[]) => fetchVoiceUsageMock(...args),
  sendVoiceMentorMessage: (...args: unknown[]) => sendVoiceMentorMessageMock(...args),
  sendChatMessage: (...args: unknown[]) => sendChatMessageMock(...args),
  trackGrowthEvent: (...args: unknown[]) => trackGrowthEventMock(...args),
}));

const freeUser = {
  id: 12,
  name: 'Free User',
  email: 'free@example.com',
  plan: 'FREE' as const,
  xp_total: 0,
  level: 0,
  timezone: 'America/Sao_Paulo',
  onboarding_completed: true,
};

const proUser = {
  ...freeUser,
  id: 13,
  name: 'Pro User',
  email: 'pro@example.com',
  plan: 'PRO' as const,
};

describe('LiveTutorScreen', () => {
  beforeEach(() => {
    fetchVoiceMentorsMock.mockReset();
    fetchVoiceUsageMock.mockReset();
    sendVoiceMentorMessageMock.mockReset();
    sendChatMessageMock.mockReset();
    trackGrowthEventMock.mockReset();

    fetchVoiceMentorsMock.mockResolvedValue([
      { id: 'clara', name: 'Clara', avatar: 'a', description: 'd', speaking_style: 's', pedagogical_focus: 'f' },
    ]);
    fetchVoiceUsageMock.mockResolvedValue({
      plan: 'FREE',
      used: 0,
      limit: 6,
      remaining: 6,
      blocked: false,
    });
  });

  it('mostra contador FREE com 6 interacoes', async () => {
    render(<LiveTutorScreen user={freeUser} onBack={() => undefined} onUpgrade={() => undefined} />);
    expect(await screen.findByText('0/6 usados')).toBeInTheDocument();
  });

  it('mostra bloqueio no FREE apos limite', async () => {
    fetchVoiceUsageMock.mockResolvedValue({
      plan: 'FREE',
      used: 6,
      limit: 6,
      remaining: 0,
      blocked: true,
    });
    render(<LiveTutorScreen user={freeUser} onBack={() => undefined} onUpgrade={() => undefined} />);
    expect(await screen.findByText(/atingiu o limite gratuito/i)).toBeInTheDocument();
  });

  it('permite PRO iniciar conversa e enviar mensagem', async () => {
    fetchVoiceUsageMock.mockResolvedValue({
      plan: 'PRO',
      used: 0,
      limit: null,
      remaining: null,
      blocked: false,
    });
    sendVoiceMentorMessageMock.mockResolvedValue({
      mentor_id: 'clara',
      mentor_name: 'Clara',
      transcript: 'hello',
      reply: 'Hi there',
      tts_text: 'Hi there',
      audio_available: false,
      voice_usage: { plan: 'PRO', used: 0, limit: null, remaining: null, blocked: false },
    });

    const user = userEvent.setup();
    render(<LiveTutorScreen user={proUser} onBack={() => undefined} onUpgrade={() => undefined} />);

    await user.click(await screen.findByRole('button', { name: /Iniciar conversa/i }));
    await user.type(screen.getByPlaceholderText(/Digite para enviar sem microfone/i), 'hello');
    await user.click(screen.getByRole('button', { name: /Enviar mensagem/i }));

    await waitFor(() => expect(sendVoiceMentorMessageMock).toHaveBeenCalledWith('clara', 'hello'));
  });
});
