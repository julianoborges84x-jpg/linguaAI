import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, Eye, EyeOff, Apple, Loader2 } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { login, register, fetchOAuthProviders } from '../api/auth';
import { API_URL } from '../api/client';

const REFERRAL_STORAGE_KEY = 'lingua_referral_code';

interface Props {
  onBack: () => void;
  onAuthenticated: (token: string) => Promise<void> | void;
  defaultMode?: 'login' | 'register';
}

export default function LoginScreen({ onBack, onAuthenticated, defaultMode = 'login' }: Props) {
  const location = useLocation();
  const [mode, setMode] = useState<'login' | 'register'>(defaultMode);
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [isSuccessFeedback, setIsSuccessFeedback] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<'google' | 'apple' | null>(null);
  const [oauthStatus, setOauthStatus] = useState<{ google: boolean; apple: boolean }>({ google: true, apple: true });
  const referralCodeFromQuery = new URLSearchParams(window.location.search).get('ref');
  const referralCodeFromStorage = localStorage.getItem(REFERRAL_STORAGE_KEY);
  const referralCode = (referralCodeFromQuery || referralCodeFromStorage || '').trim() || null;

  useEffect(() => {
    const loadProviders = async () => {
      try {
        const providers = await fetchOAuthProviders();
        const google = providers.find((item) => item.provider === 'google')?.enabled ?? false;
        const apple = providers.find((item) => item.provider === 'apple')?.enabled ?? false;
        setOauthStatus({ google, apple });
      } catch {
        setOauthStatus({ google: true, apple: true });
      }
    };
    void loadProviders();
  }, []);

  useEffect(() => {
    const oauthError = (location.state as { oauthError?: string } | null)?.oauthError;
    if (!oauthError) return;
    setFeedback(oauthError);
    setIsSuccessFeedback(false);
  }, [location.state]);

  const handleSignIn = async () => {
    if (!email.trim() || !password.trim()) {
      setFeedback('Preencha email e senha.');
      setIsSuccessFeedback(false);
      return;
    }

    setLoading(true);
    setFeedback('');
    try {
      const result = await login(email.trim(), password);
      await onAuthenticated(result.access_token);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Erro ao entrar.');
      setIsSuccessFeedback(false);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    if (!name.trim()) {
      setFeedback('Preencha seu nome.');
      setIsSuccessFeedback(false);
      return;
    }

    if (!email.trim() || !password.trim()) {
      setFeedback('Preencha nome, email e senha.');
      setIsSuccessFeedback(false);
      return;
    }

    setLoading(true);
    setFeedback('');
    try {
      await register(name.trim(), email.trim(), password, referralCode);
      if (referralCodeFromStorage) {
        localStorage.removeItem(REFERRAL_STORAGE_KEY);
      }
      setMode('login');
      setPassword('');
      setFeedback('Conta criada com sucesso. Agora faca login.');
      setIsSuccessFeedback(true);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Erro ao criar conta.');
      setIsSuccessFeedback(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (mode === 'login') {
      await handleSignIn();
      return;
    }
    await handleRegister();
  };

  const handleOAuth = (provider: 'google' | 'apple') => {
    setOauthLoading(provider);
    setFeedback('');
    const redirectOrigin = encodeURIComponent(window.location.origin);
    window.location.assign(`${API_URL}/auth/oauth/${provider}/start?redirect_origin=${redirectOrigin}`);
  };

  return (
    <div className="min-h-screen flex flex-col bg-background-light antialiased">
      <div className="flex items-center bg-transparent p-4 pb-2 justify-between">
        <button onClick={onBack} className="text-slate-900 flex size-12 items-center justify-center">
          <ArrowLeft size={24} />
        </button>

        <h2 className="text-slate-900 text-lg font-bold flex-1 text-center pr-12">Mentor Lingua</h2>

        <div className="flex justify-center gap-2">
          <span className="px-2 py-0.5 rounded bg-green-100 text-green-700 text-[10px] font-bold uppercase tracking-wider">
            Auth API
          </span>
        </div>
      </div>

      <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
        <div className="w-full max-w-[400px]">
          <div
            className="w-full bg-center bg-no-repeat bg-cover flex flex-col justify-end overflow-hidden bg-primary/10 rounded-xl min-h-[200px]"
            style={{
              backgroundImage:
                "url('https://lh3.googleusercontent.com/aida-public/AB6AXuC3GQVa80809pss_ViMtjoDuVCG4bwV14h8O38otuoKIBEYksUurngj38endfW2sjiMo_wPsB2niP-8nb7Gwqm1KaZbDzxpprC_Oos6iKklL_yKLTstW9IA_kLqGJ_tTZaPSXwQ0hZcvZWntmgB2erc6HRGDnGfFhnM6c1DKO2lvc8FWQoexOeh6UY8I-GaaGWz2ToZvxhME8HYj4LZVJPK0KfNKv0d8zCtxb5EILq7ZnB4CTQyeKQlMblCSUZ_kE1TGud5lClmda44')",
            }}
          />
        </div>

        <div className="w-full max-w-[400px] text-center mt-8 mb-8">
          <h1 className="text-slate-900 tracking-tight text-[32px] font-bold leading-tight">
            {mode === 'login' ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-slate-600 mt-2">
            {mode === 'login'
              ? 'Entre para continuar sua jornada de idiomas.'
              : 'Crie sua conta e conecte seu plano ao backend real.'}
          </p>
        </div>

        <div className="w-full max-w-[400px] space-y-4">
          {mode === 'register' && (
            <div className="flex flex-col w-full">
              <p className="text-slate-900 text-sm font-semibold pb-2">Full Name</p>
              <input
                className="flex w-full rounded-xl text-slate-900 focus:outline-0 focus:ring-2 focus:ring-primary border border-slate-200 bg-white h-14 p-[15px] text-base"
                placeholder="Juliano Borges"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          )}

          <div className="flex flex-col w-full">
            <p className="text-slate-900 text-sm font-semibold pb-2">Email Address</p>
            <input
              className="flex w-full rounded-xl text-slate-900 focus:outline-0 focus:ring-2 focus:ring-primary border border-slate-200 bg-white h-14 p-[15px] text-base"
              placeholder="m@example.com"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="flex flex-col w-full">
            <div className="flex justify-between items-center pb-2">
              <p className="text-slate-900 text-sm font-semibold">Password</p>
              {mode === 'login' && <span className="text-sm font-semibold text-slate-400">JWT session</span>}
            </div>

            <div className="relative flex w-full">
              <input
                className="flex w-full rounded-xl text-slate-900 focus:outline-0 focus:ring-2 focus:ring-primary border border-slate-200 bg-white h-14 p-[15px] text-base"
                placeholder="Enter your password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />

              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {feedback && (
            <div
              className={`rounded-xl px-4 py-3 text-sm font-medium ${
                isSuccessFeedback ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
              }`}
            >
              {feedback}
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full h-14 bg-primary hover:bg-primary/90 text-white font-bold rounded-xl transition-colors mt-4 flex items-center justify-center disabled:opacity-70"
          >
            {loading ? (
              <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
                <Loader2 size={24} />
              </motion.div>
            ) : mode === 'login' ? (
              'Sign In'
            ) : (
              'Create Account'
            )}
          </button>
        </div>

        <div className="w-full max-w-[400px] flex items-center gap-4 my-8">
          <div className="h-[1px] flex-1 bg-slate-200"></div>
          <span className="text-slate-400 text-sm font-medium">or continue with</span>
          <div className="h-[1px] flex-1 bg-slate-200"></div>
        </div>

        <div className="w-full max-w-[400px] grid grid-cols-2 gap-4">
          <button
            type="button"
            onClick={() => handleOAuth('google')}
            disabled={Boolean(oauthLoading)}
            className="flex items-center justify-center gap-2 h-14 bg-white border border-slate-200 rounded-xl disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <img
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuAgnXyEw_HwziqzWLOqWQ9qsbVR6-7V3D9NymDxBgz5E8cVhddBWLBiZ_L2cy-5vrTXQaJWnOsUC1vEhmFSb6poYcCC4ve2abpN3qLOAh6tZwMk2zL4kNP6QLr4cLMkUthkxnywMycquNAL2nbve6-zhvKaKk_WaYadQuKs0-ONU-VEgPXjgupNEyqpubQbGss7Adcf0Gk75y0FJDbTK8iM80W9P98BM-z2ZZmFtkCTIwQFqrId5xfyknaiRbFCzs1WddRzzdcE6eX6"
              className="w-5 h-5"
              alt="Google"
            />
            <span className="text-slate-900 font-semibold">{oauthLoading === 'google' ? 'Conectando...' : 'Google'}</span>
          </button>

          <button
            type="button"
            onClick={() => handleOAuth('apple')}
            disabled={Boolean(oauthLoading)}
            className="flex items-center justify-center gap-2 h-14 bg-white border border-slate-200 rounded-xl disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <Apple size={20} />
            <span className="text-slate-900 font-semibold">{oauthLoading === 'apple' ? 'Conectando...' : 'Apple'}</span>
          </button>
        </div>
        {!oauthStatus.google || !oauthStatus.apple ? (
          <p className="w-full max-w-[400px] mt-2 text-center text-xs text-amber-700">
            Google/Apple precisam estar configurados no servidor para concluir o login social.
          </p>
        ) : null}
        <p className="w-full max-w-[400px] mt-2 text-center text-xs text-slate-500">
          {mode === 'register' ? 'Atalho rapido para criar conta' : 'Atalho rapido para entrar'}
          {' '}com Google ou Apple.
        </p>

        <div className="mt-auto pt-8 pb-4 text-center">
          {mode === 'login' ? (
            <p className="text-slate-600 font-medium">
              Don&apos;t have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setFeedback('');
                  setIsSuccessFeedback(false);
                  setMode('register');
                }}
                className="font-bold hover:underline text-primary"
              >
                Create Account
              </button>
            </p>
          ) : (
            <p className="text-slate-600 font-medium">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => {
                  setFeedback('');
                  setIsSuccessFeedback(false);
                  setMode('login');
                }}
                className="font-bold hover:underline text-primary"
              >
                Sign In
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
