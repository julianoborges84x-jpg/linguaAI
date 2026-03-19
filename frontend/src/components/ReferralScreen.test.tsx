import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import ReferralScreen from './ReferralScreen';

const fetchReferralMeMock = vi.fn();
const fetchReferralStatsMock = vi.fn();
const trackGrowthEventMock = vi.fn();

vi.mock('../api/auth', () => ({
  fetchReferralMe: (...args: unknown[]) => fetchReferralMeMock(...args),
  fetchReferralStats: (...args: unknown[]) => fetchReferralStatsMock(...args),
  trackGrowthEvent: (...args: unknown[]) => trackGrowthEventMock(...args),
}));

describe('ReferralScreen', () => {
  beforeEach(() => {
    fetchReferralMeMock.mockReset();
    fetchReferralStatsMock.mockReset();
    trackGrowthEventMock.mockReset();
    vi.stubGlobal('navigator', {
      clipboard: {
        writeText: vi.fn(),
      },
    });
  });

  it('carrega dados e renderiza link, contagem e convidados', async () => {
    fetchReferralMeMock.mockResolvedValue({
      referral_code: 'lingua12345',
      invite_link: 'http://localhost:3000/invite/lingua12345',
      pro_access_until: '2026-03-18',
    });
    fetchReferralStatsMock.mockResolvedValue({
      referral_count: 2,
      reward_xp_total: 300,
      pro_access_until: '2026-03-18',
      invited_users: [
        { user_id: 2, name: 'Bruno', email: 'bruno@example.com' },
      ],
    });

    render(<ReferralScreen onBack={() => undefined} />);

    expect(screen.getByText(/Carregando link/i)).toBeInTheDocument();
    expect(await screen.findByText('http://localhost:3000/invite/lingua12345')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('300')).toBeInTheDocument();
    expect(screen.getByText('Bruno')).toBeInTheDocument();
  });

  it('copia o link ao clicar em "Copiar link"', async () => {
    const user = userEvent.setup();
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', {
      clipboard: {
        writeText,
      },
    });

    fetchReferralMeMock.mockResolvedValue({
      referral_code: 'lingua12345',
      invite_link: 'http://localhost:3000/invite/lingua12345',
      pro_access_until: null,
    });
    fetchReferralStatsMock.mockResolvedValue({
      referral_count: 0,
      reward_xp_total: 0,
      pro_access_until: null,
      invited_users: [],
    });

    render(<ReferralScreen onBack={() => undefined} />);
    await screen.findByText('http://localhost:3000/invite/lingua12345');

    await user.click(screen.getByRole('button', { name: /Copiar link/i }));
    expect(writeText).toHaveBeenCalledWith('http://localhost:3000/invite/lingua12345');
    await waitFor(() => expect(screen.getByRole('button', { name: /Copiado!/i })).toBeInTheDocument());
  });

  it('mostra erro quando falha ao carregar dados', async () => {
    fetchReferralMeMock.mockRejectedValue(new Error('Falha de API'));
    fetchReferralStatsMock.mockRejectedValue(new Error('Falha de API'));

    render(<ReferralScreen onBack={() => undefined} />);

    expect(await screen.findByText(/Falha de API/i)).toBeInTheDocument();
  });
});
