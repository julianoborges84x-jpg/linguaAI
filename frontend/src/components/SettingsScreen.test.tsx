import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import SettingsScreen from './SettingsScreen';

describe('SettingsScreen', () => {
  it('permite salvar preferencias e fazer logout', async () => {
    const onLogout = vi.fn();
    const user = userEvent.setup();

    render(<SettingsScreen onBack={() => undefined} onLogout={onLogout} />);

    await user.selectOptions(screen.getByDisplayValue('English'), 'es');
    await user.click(screen.getByRole('button', { name: /Salvar configuracoes/i }));
    expect(await screen.findByText(/Configuracoes salvas/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Sair da conta/i }));
    expect(onLogout).toHaveBeenCalled();
  });
});
