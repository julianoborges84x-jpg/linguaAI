import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import VoiceChatScreen from './VoiceChatScreen';

const fetchVoiceMentorsMock = vi.fn();
const fetchVoiceUsageMock = vi.fn();
const sendVoiceMentorMessageMock = vi.fn();
const trackGrowthEventMock = vi.fn();

vi.mock('../api/auth', () => ({
  fetchVoiceMentors: (...args: unknown[]) => fetchVoiceMentorsMock(...args),
  fetchVoiceUsage: (...args: unknown[]) => fetchVoiceUsageMock(...args),
  sendVoiceMentorMessage: (...args: unknown[]) => sendVoiceMentorMessageMock(...args),
  trackGrowthEvent: (...args: unknown[]) => trackGrowthEventMock(...args),
}));

const freeUser = {
  id: 10,
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
  id: 11,
  name: 'Pro User',
  email: 'pro@example.com',
  plan: 'PRO' as const,
};

describe('VoiceChatScreen', () => {
  beforeEach(() => {
    fetchVoiceMentorsMock.mockReset();
    fetchVoiceUsageMock.mockReset();
    sendVoiceMentorMessageMock.mockReset();
    trackGrowthEventMock.mockReset();
    fetchVoiceMentorsMock.mockResolvedValue([
      { id: 'clara', name: 'Clara', avatar: 'a', description: 'd', speaking_style: 's', pedagogical_focus: 'f' },
    ]);
    fetchVoiceUsageMock.mockResolvedValue({
      plan: 'PRO',
      used: 0,
      limit: null,
      remaining: null,
      blocked: false,
    });
  });

  it('mostra contador FREE e permite trial de voz', async () => {
    fetchVoiceUsageMock.mockResolvedValue({
      plan: 'FREE',
      used: 2,
      limit: 6,
      remaining: 4,
      blocked: false,
    });
    sendVoiceMentorMessageMock.mockResolvedValue({
      mentor_id: 'clara',
      mentor_name: 'Clara',
      transcript: 'hello',
      reply: 'Hi there',
      tts_text: 'Hi there',
      audio_available: false,
      voice_usage: { plan: 'FREE', used: 3, limit: 6, remaining: 3, blocked: false },
    });

    const user = userEvent.setup();
    render(<VoiceChatScreen user={freeUser} onBack={() => undefined} onUpgrade={() => undefined} />);
    expect(await screen.findByText('2/6 usados')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Iniciar conversa/i }));
    await user.type(screen.getByPlaceholderText(/Ou digite sua frase/i), 'hello');
    await user.click(screen.getByRole('button', { name: /Enviar mensagem de voz/i }));
    await screen.findByText('Hi there');
  });

  it('bloqueia FREE ao atingir limite e mostra CTA de upgrade', async () => {
    fetchVoiceUsageMock.mockResolvedValue({
      plan: 'FREE',
      used: 6,
      limit: 6,
      remaining: 0,
      blocked: true,
    });
    const onUpgrade = vi.fn();
    const user = userEvent.setup();
    render(<VoiceChatScreen user={freeUser} onBack={() => undefined} onUpgrade={onUpgrade} />);
    expect(await screen.findByText(/Você atingiu o limite gratuito/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Desbloquear agora/i }));
    expect(onUpgrade).toHaveBeenCalled();
    expect(trackGrowthEventMock).toHaveBeenCalledWith('voice_upgrade_cta_clicked');
  });

  it('permite PRO selecionar mentor e conversar', async () => {
    fetchVoiceMentorsMock.mockResolvedValue([
      { id: 'clara', name: 'Clara', avatar: 'a', description: 'd', speaking_style: 's', pedagogical_focus: 'f' },
      { id: 'maya', name: 'Maya', avatar: 'b', description: 'd2', speaking_style: 's2', pedagogical_focus: 'f2' },
    ]);
    sendVoiceMentorMessageMock.mockResolvedValue({
      mentor_id: 'maya',
      mentor_name: 'Maya',
      transcript: 'hello',
      reply: 'Hi there',
      tts_text: 'Hi there',
      audio_available: false,
      voice_usage: { plan: 'PRO', used: 0, limit: null, remaining: null, blocked: false },
    });

    const user = userEvent.setup();
    render(<VoiceChatScreen user={proUser} onBack={() => undefined} onUpgrade={() => undefined} />);

    expect(await screen.findByRole('button', { name: /Clara/i })).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Maya/i }));
    await waitFor(() => expect(trackGrowthEventMock).toHaveBeenCalledWith('voice_mentor_selected', { mentor_id: 'maya' }));

    await user.click(screen.getByRole('button', { name: /Iniciar conversa/i }));
    await user.type(screen.getByPlaceholderText(/Ou digite sua frase/i), 'hello');
    await user.click(screen.getByRole('button', { name: /Enviar mensagem de voz/i }));

    await waitFor(() => expect(sendVoiceMentorMessageMock).toHaveBeenCalledWith('maya', 'hello'));
    expect(await screen.findByText('Hi there')).toBeInTheDocument();
  });

  it('permite replay da ultima resposta e fallback sem audio', async () => {
    const speak = vi.fn();
    const cancel = vi.fn();
    vi.stubGlobal('speechSynthesis', { speak, cancel });

    fetchVoiceMentorsMock.mockResolvedValue([
      { id: 'ethan', name: 'Ethan', avatar: 'a', description: 'd', speaking_style: 's', pedagogical_focus: 'f' },
    ]);
    sendVoiceMentorMessageMock.mockResolvedValue({
      mentor_id: 'ethan',
      mentor_name: 'Ethan',
      transcript: 'test',
      reply: 'Business reply',
      tts_text: 'Business reply',
      audio_available: true,
      voice_usage: { plan: 'PRO', used: 0, limit: null, remaining: null, blocked: false },
    });

    const user = userEvent.setup();
    render(<VoiceChatScreen user={proUser} onBack={() => undefined} onUpgrade={() => undefined} />);

    await screen.findByRole('button', { name: /Ethan/i });
    await user.click(screen.getByRole('button', { name: /Iniciar conversa/i }));
    await user.type(screen.getByPlaceholderText(/Ou digite sua frase/i), 'test');
    await user.click(screen.getByRole('button', { name: /Enviar mensagem de voz/i }));
    await screen.findByText('Business reply');

    await user.click(screen.getByRole('button', { name: /Repetir ultima resposta/i }));
    await waitFor(() => expect(trackGrowthEventMock).toHaveBeenCalledWith('voice_reply_replayed', { mentor_id: 'ethan' }));
  });

  it('mostra fallback quando audio nao esta disponivel', async () => {
    vi.stubGlobal('speechSynthesis', undefined);
    fetchVoiceMentorsMock.mockResolvedValue([
      { id: 'noah', name: 'Noah', avatar: 'a', description: 'd', speaking_style: 's', pedagogical_focus: 'f' },
    ]);

    render(<VoiceChatScreen user={proUser} onBack={() => undefined} onUpgrade={() => undefined} />);
    expect(await screen.findByText(/Audio indisponivel/i)).toBeInTheDocument();
  });
});
