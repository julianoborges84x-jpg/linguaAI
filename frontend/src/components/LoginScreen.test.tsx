import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import type { ReactElement } from 'react';
import LoginScreen from './LoginScreen';

const loginMock = vi.fn();
const registerMock = vi.fn();
const fetchOAuthProvidersMock = vi.fn();

vi.mock('../api/auth', () => ({
  login: (...args: unknown[]) => loginMock(...args),
  register: (...args: unknown[]) => registerMock(...args),
  fetchOAuthProviders: (...args: unknown[]) => fetchOAuthProvidersMock(...args),
}));

vi.mock('../api/client', () => ({
  API_URL: 'http://127.0.0.1:8000',
}));

describe('LoginScreen', () => {
  beforeEach(() => {
    loginMock.mockReset();
    registerMock.mockReset();
    fetchOAuthProvidersMock.mockReset();
    fetchOAuthProvidersMock.mockResolvedValue([
      { provider: 'google', enabled: true },
      { provider: 'apple', enabled: true },
    ]);
  });

  const renderScreen = (ui: ReactElement) => render(<MemoryRouter>{ui}</MemoryRouter>);

  it('faz login real via callback autenticado', async () => {
    loginMock.mockResolvedValue({ access_token: 'jwt-123' });
    const onAuthenticated = vi.fn();
    const user = userEvent.setup();

    renderScreen(<LoginScreen onBack={() => undefined} onAuthenticated={onAuthenticated} defaultMode="login" />);

    await user.click(screen.getByPlaceholderText('m@example.com'));
    await user.keyboard('user@example.com');
    await user.click(screen.getByPlaceholderText('Enter your password'));
    await user.keyboard('123456');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => expect(loginMock).toHaveBeenCalledWith('user@example.com', '123456'));
    await waitFor(() => expect(onAuthenticated).toHaveBeenCalledWith('jwt-123'));
  });

  it('permite cadastro e mostra feedback de sucesso', async () => {
    registerMock.mockResolvedValue({ id: 1 });
    const user = userEvent.setup();

    renderScreen(<LoginScreen onBack={() => undefined} onAuthenticated={() => undefined} defaultMode="register" />);

    await user.click(screen.getByPlaceholderText('Juliano Borges'));
    await user.keyboard('Maria');
    await user.click(screen.getByPlaceholderText('m@example.com'));
    await user.keyboard('maria@example.com');
    await user.click(screen.getByPlaceholderText('Enter your password'));
    await user.keyboard('abc12345');
    await user.click(screen.getByRole('button', { name: 'Create Account' }));

    await waitFor(() => expect(registerMock).toHaveBeenCalledWith('Maria', 'maria@example.com', 'abc12345', null));
    expect(await screen.findByText('Conta criada com sucesso. Agora faca login.')).toBeInTheDocument();
  });

  it('aciona redirecionamento OAuth no botao Google', async () => {
    const user = userEvent.setup();
    const assignSpy = vi.spyOn(window.location, 'assign').mockImplementation(() => undefined);
    renderScreen(<LoginScreen onBack={() => undefined} onAuthenticated={() => undefined} defaultMode="login" />);

    const googleButton = await screen.findByRole('button', { name: /Google/i });
    await user.click(googleButton);
    expect(assignSpy).toHaveBeenCalledWith('http://127.0.0.1:8000/auth/oauth/google/start');
    assignSpy.mockRestore();
  });
});
