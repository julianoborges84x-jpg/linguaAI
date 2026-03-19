import { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

import { oauthLogin } from '../api/auth';

interface Props {
  onAuthenticated: (token: string) => Promise<void> | void;
}

export default function OAuthCallbackScreen({ onAuthenticated }: Props) {
  const navigate = useNavigate();
  const { provider } = useParams();
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState('Validando login social...');

  useEffect(() => {
    const run = async () => {
      const resolvedProvider = provider === 'google' || provider === 'apple' ? provider : null;
      if (!resolvedProvider) {
        navigate('/login', { replace: true });
        return;
      }

      const error = searchParams.get('error');
      if (error) {
        navigate('/login', {
          replace: true,
          state: { oauthError: `Login com ${resolvedProvider} foi cancelado ou negado.` },
        });
        return;
      }

      const code = searchParams.get('code') || '';
      const state = searchParams.get('state') || '';
      if (!code || !state) {
        navigate('/login', {
          replace: true,
          state: { oauthError: 'Dados de autenticacao social ausentes. Tente novamente.' },
        });
        return;
      }

      try {
        setMessage('Conectando sua conta...');
        const payload = await oauthLogin(resolvedProvider, code, state);
        await onAuthenticated(payload.access_token);
      } catch (err) {
        navigate('/login', {
          replace: true,
          state: { oauthError: err instanceof Error ? err.message : 'Falha ao concluir login social.' },
        });
      }
    };

    void run();
  }, [navigate, onAuthenticated, provider, searchParams]);

  return (
    <div className="min-h-screen bg-background-light flex items-center justify-center px-4">
      <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary">OAuth</p>
        <p className="mt-2 text-lg font-black text-slate-900">{message}</p>
      </div>
    </div>
  );
}
