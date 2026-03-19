import { render, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

import OAuthCallbackScreen from './OAuthCallbackScreen';

const oauthLoginMock = vi.fn();

vi.mock('../api/auth', () => ({
  oauthLogin: (...args: unknown[]) => oauthLoginMock(...args),
}));

describe('OAuthCallbackScreen', () => {
  beforeEach(() => {
    oauthLoginMock.mockReset();
  });

  it('conclui callback do Google e chama onAuthenticated', async () => {
    oauthLoginMock.mockResolvedValue({ access_token: 'jwt-oauth', token_type: 'bearer' });
    const onAuthenticated = vi.fn();

    render(
      <MemoryRouter initialEntries={['/login/oauth/google/callback?code=abc&state=xyz']}>
        <Routes>
          <Route path="/login/oauth/:provider/callback" element={<OAuthCallbackScreen onAuthenticated={onAuthenticated} />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => expect(oauthLoginMock).toHaveBeenCalledWith('google', 'abc', 'xyz'));
    await waitFor(() => expect(onAuthenticated).toHaveBeenCalledWith('jwt-oauth'));
  });
});
