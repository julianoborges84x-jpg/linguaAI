import { useEffect, useMemo, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom';

import {
  cancelSubscription,
  clearToken,
  createCheckoutSession,
  createPortalSession,
  fetchDailyChallenge,
  fetchBillingStatus,
  fetchCurrentUser,
  fetchGrowthDashboard,
  fetchAdaptiveRecommendations,
  fetchPedagogyDashboard,
  getToken,
  storeToken,
  trackGrowthEvent,
  updateOnboarding,
} from './api/auth';
import ChatScreen from './components/ChatScreen';
import DashboardScreen from './components/DashboardScreen';
import ImmersionScreen from './components/ImmersionScreen';
import LandingPage from './components/LandingPage';
import LessonScreen from './components/LessonScreen';
import LoginScreen from './components/LoginScreen';
import OAuthCallbackScreen from './components/OAuthCallbackScreen';
import PrivacyPage from './components/PrivacyPage';
import DailyChallengeScreen from './components/DailyChallengeScreen';
import InviteRedirectScreen from './components/InviteRedirectScreen';
import RealLifeScreen from './components/RealLifeScreen';
import ReferralPromptModal from './components/ReferralPromptModal';
import ReferralScreen from './components/ReferralScreen';
import SettingsScreen from './components/SettingsScreen';
import TermsPage from './components/TermsPage';
import LiveTutorScreen from './components/LiveTutorScreen';
import { AuthUser, DailyChallengeInfo, GrowthDashboardData, PedagogyDashboardData, UserProfile } from './types';

const STORAGE_KEYS = {
  profile: 'mentor_lingua_profile',
  referralPopupShownAt: 'lingua_referral_popup_shown_at',
};

const languageMap: Record<string, 'en' | 'es' | 'fr' | 'it'> = {
  ingles: 'en',
  espanhol: 'es',
  frances: 'fr',
  italiano: 'it',
};

type DashboardView = 'home' | 'lesson' | 'chat' | 'immersion' | 'real-life' | 'daily-challenge' | 'referral' | 'voice-mentor' | 'settings';
type ReferralTrigger = 'daily_challenge_completed' | 'xp_gained' | 'level_up';

function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile>({
    language: '',
    level: '',
    goal: '',
  });
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const [stripeConfigured, setStripeConfigured] = useState(false);
  const [booting, setBooting] = useState(true);
  const [appError, setAppError] = useState('');
  const [billingLoading, setBillingLoading] = useState(false);
  const [growthData, setGrowthData] = useState<GrowthDashboardData | null>(null);
  const [dailyChallenge, setDailyChallenge] = useState<DailyChallengeInfo | null>(null);
  const [pedagogyData, setPedagogyData] = useState<PedagogyDashboardData | null>(null);
  const [dashboardView, setDashboardView] = useState<DashboardView>('home');
  const [referralPopupOpen, setReferralPopupOpen] = useState(false);
  const [referralTrigger, setReferralTrigger] = useState<ReferralTrigger>('xp_gained');

  const hasOnboardingProfile = useMemo(
    () => Boolean(profile.language && profile.level && profile.goal),
    [profile.goal, profile.language, profile.level],
  );

  useEffect(() => {
    try {
      const savedProfile = localStorage.getItem(STORAGE_KEYS.profile);
      if (savedProfile) {
        setProfile(JSON.parse(savedProfile) as UserProfile);
      }
    } catch (error) {
      console.error('Erro ao restaurar perfil local:', error);
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.profile, JSON.stringify(profile));
    } catch (error) {
      console.error('Erro ao salvar perfil local:', error);
    }
  }, [profile]);

  const maybeOpenReferralPopup = async (trigger: ReferralTrigger) => {
    if (location.pathname !== '/dashboard' || dashboardView === 'referral') return;

    const now = Date.now();
    const lastShownRaw = localStorage.getItem(STORAGE_KEYS.referralPopupShownAt);
    const lastShown = lastShownRaw ? Number(lastShownRaw) : 0;
    const cooldownMs = 30 * 60 * 1000;
    if (now - lastShown < cooldownMs) return;

    setReferralTrigger(trigger);
    setReferralPopupOpen(true);
    localStorage.setItem(STORAGE_KEYS.referralPopupShownAt, String(now));
    try {
      await trackGrowthEvent('referral_popup_shown', { trigger });
    } catch {
      // non-blocking analytics
    }
  };

  const syncSession = async (options?: { detectGrowth?: boolean }) => {
    const previousUser = authUser;
    const user = await fetchCurrentUser();
    setAuthUser(user);
    const billing = await fetchBillingStatus();
    setStripeConfigured(Boolean(billing.stripe_configured));
    try {
      const growth = await fetchGrowthDashboard();
      setGrowthData(growth);
    } catch {
      setGrowthData(null);
    }
    try {
      const challenge = await fetchDailyChallenge();
      setDailyChallenge(challenge);
    } catch {
      setDailyChallenge(null);
    }
    try {
      const pedagogy = await fetchPedagogyDashboard();
      try {
        const recommendations = await fetchAdaptiveRecommendations();
        setPedagogyData({ ...pedagogy, recommendations });
      } catch {
        setPedagogyData(pedagogy);
      }
    } catch {
      setPedagogyData(null);
    }
    if (options?.detectGrowth && previousUser) {
      if (user.level > previousUser.level) {
        void maybeOpenReferralPopup('level_up');
      } else if (user.xp_total > previousUser.xp_total) {
        void maybeOpenReferralPopup('xp_gained');
      }
    }
    return user;
  };

  const ensureOnboarding = async (user: AuthUser) => {
    const targetLanguage = languageMap[profile.language];
    if (!user.onboarding_completed && targetLanguage && hasOnboardingProfile) {
      await updateOnboarding({
        target_language: targetLanguage,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'America/Sao_Paulo',
      });
      return syncSession({ detectGrowth: false });
    }
    return user;
  };

  useEffect(() => {
    const bootstrap = async () => {
      if (!getToken()) {
        setBooting(false);
        return;
      }

      try {
        await syncSession({ detectGrowth: false });
      } catch {
        clearToken();
        setAuthUser(null);
      } finally {
        setBooting(false);
      }
    };

    bootstrap();
  }, []);

  useEffect(() => {
    if (location.pathname !== '/dashboard') {
      setDashboardView('home');
    }
  }, [location.pathname]);

  useEffect(() => {
    if (!authUser || location.pathname !== '/dashboard') return;

    const checkout = new URLSearchParams(location.search).get('checkout');
    if (!checkout) return;

    const syncAfterCheckout = async () => {
      if (checkout === 'success') {
        try {
          await syncSession({ detectGrowth: false });
          setAppError('Assinatura PRO confirmada com sucesso.');
        } catch {
          setAppError('Pagamento confirmado, mas nao foi possivel atualizar o dashboard agora.');
        }
      }

      if (checkout === 'cancel') {
        setAppError('Assinatura cancelada. Voce pode tentar novamente quando quiser.');
      }

      navigate('/dashboard', { replace: true });
    };

    syncAfterCheckout();
  }, [authUser, location.pathname, location.search, navigate]);

  const handleAuthSuccess = async (token: string) => {
    setAppError('');
    storeToken(token);
    try {
      const user = await syncSession({ detectGrowth: false });
      const syncedUser = await ensureOnboarding(user);
      setAuthUser(syncedUser);
      setDashboardView('home');
      navigate('/dashboard', { replace: true });
    } catch (error) {
      clearToken();
      setAuthUser(null);
      setAppError(error instanceof Error ? error.message : 'Nao foi possivel carregar sua sessao.');
      navigate('/login', { replace: true });
    }
  };

  const handleLogout = () => {
    clearToken();
    setAuthUser(null);
    setStripeConfigured(false);
    setGrowthData(null);
    setPedagogyData(null);
    setDashboardView('home');
    navigate('/login', { replace: true });
  };

  const handleUpgrade = async () => {
    setBillingLoading(true);
    setAppError('');
    try {
      const payload = await createCheckoutSession();
      await trackGrowthEvent('pro_checkout_started_ui');
      window.location.href = payload.checkout_url;
    } catch (error) {
      setAppError(error instanceof Error ? error.message : 'Nao foi possivel iniciar o checkout.');
    } finally {
      setBillingLoading(false);
    }
  };

  const handleManageSubscription = async () => {
    setBillingLoading(true);
    setAppError('');
    try {
      const payload = await createPortalSession();
      await trackGrowthEvent('pro_manage_opened_ui');
      window.location.href = payload.portal_url || payload.url;
    } catch (error) {
      setAppError(error instanceof Error ? error.message : 'Nao foi possivel abrir o portal da assinatura.');
    } finally {
      setBillingLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    setBillingLoading(true);
    setAppError('');
    try {
      await cancelSubscription();
      await trackGrowthEvent('pro_canceled_ui');
      await syncSession({ detectGrowth: false });
      setAppError('Assinatura PRO cancelada com sucesso.');
    } catch (error) {
      setAppError(error instanceof Error ? error.message : 'Nao foi possivel cancelar sua assinatura.');
    } finally {
      setBillingLoading(false);
    }
  };

  const handleLessonFinished = async () => {
    try {
      const user = await syncSession({ detectGrowth: true });
      setAuthUser(user);
      await trackGrowthEvent('lesson_completed_ui');
    } catch (error) {
      setAppError(error instanceof Error ? error.message : 'Sua sessao foi atualizada com erro.');
    } finally {
      setDashboardView('home');
    }
  };

  const dashboardElement = () => {
    if (booting) {
      return (
        <div className="min-h-screen bg-background-light flex items-center justify-center">
          <div className="rounded-2xl bg-white px-6 py-5 shadow-sm border border-slate-200 text-center">
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-[0.2em]">LinguaAI</p>
            <p className="mt-2 text-lg font-bold text-slate-900">Carregando sua sessao...</p>
          </div>
        </div>
      );
    }

    if (!authUser) {
      return <Navigate to="/login" replace />;
    }

    if (dashboardView === 'lesson') {
      return <LessonScreen onFinish={handleLessonFinished} />;
    }

    if (dashboardView === 'chat') {
      return (
        <ChatScreen
          user={authUser}
          onBack={async () => {
            try {
              const user = await syncSession({ detectGrowth: true });
              setAuthUser(user);
            } catch {
              // keep previous state if refresh fails
            }
            setDashboardView('home');
          }}
        />
      );
    }

    if (dashboardView === 'immersion') {
      return <ImmersionScreen onBack={() => setDashboardView('home')} />;
    }
    if (dashboardView === 'real-life') {
      return <RealLifeScreen onBack={() => setDashboardView('home')} />;
    }
    if (dashboardView === 'daily-challenge') {
      return (
        <DailyChallengeScreen
          onBack={() => setDashboardView('home')}
          onRefresh={async () => {
            await syncSession({ detectGrowth: true });
          }}
          onCompleted={async () => {
            await maybeOpenReferralPopup('daily_challenge_completed');
          }}
        />
      );
    }
    if (dashboardView === 'referral') {
      return <ReferralScreen onBack={() => setDashboardView('home')} />;
    }
    if (dashboardView === 'voice-mentor') {
      return <LiveTutorScreen user={authUser} onBack={() => setDashboardView('home')} onUpgrade={handleUpgrade} />;
    }
    if (dashboardView === 'settings') {
      return <SettingsScreen onBack={() => setDashboardView('home')} onLogout={handleLogout} />;
    }

    const referralCode = growthData?.referral.referral_code || authUser.referral_code || '';
    const inviteLink = referralCode ? `${window.location.origin}/invite/${referralCode}` : '';

    const handleReferralCopy = async (source: string) => {
      if (!inviteLink) return;
      await navigator.clipboard.writeText(inviteLink);
      try {
        await trackGrowthEvent('referral_link_copied', { source });
      } catch {
        // non-blocking analytics
      }
    };

    const handleReferralSend = async (source: string) => {
      if (!inviteLink) return;
      try {
        await trackGrowthEvent('referral_sent', { source });
      } catch {
        // non-blocking analytics
      }
      const text = encodeURIComponent(`Vamos praticar ingles com IA no LinguaAI: ${inviteLink}`);
      window.open(`https://wa.me/?text=${text}`, '_blank', 'noopener,noreferrer');
    };

    return (
      <>
        <DashboardScreen
          user={authUser}
          growthData={growthData}
          dailyChallenge={dailyChallenge}
          pedagogyData={pedagogyData}
          stripeConfigured={stripeConfigured}
          billingLoading={billingLoading}
          onStartLesson={() => setDashboardView('lesson')}
          onOpenChat={() => setDashboardView('chat')}
          onOpenImmersion={() => setDashboardView('immersion')}
          onOpenRealLife={() => setDashboardView('real-life')}
          onOpenDailyChallenge={() => setDashboardView('daily-challenge')}
          onOpenReferral={() => setDashboardView('referral')}
          onOpenVoiceMentor={() => setDashboardView('voice-mentor')}
          onOpenSettings={() => setDashboardView('settings')}
          onReferralCopy={() => handleReferralCopy('dashboard_card')}
          onReferralSend={() => handleReferralSend('dashboard_card')}
          onUpgrade={handleUpgrade}
          onOpenPedagogyRecommendation={() => setDashboardView('chat')}
          onOpenVocabularyReview={() => setDashboardView('chat')}
          onManageSubscription={handleManageSubscription}
          onCancelSubscription={handleCancelSubscription}
          onLogout={handleLogout}
          appError={appError}
        />
        <ReferralPromptModal
          open={referralPopupOpen}
          trigger={referralTrigger}
          onClose={() => setReferralPopupOpen(false)}
          onCopy={async () => {
            await handleReferralCopy('referral_popup');
            setReferralPopupOpen(false);
          }}
          onSend={async () => {
            await handleReferralSend('referral_popup');
            setReferralPopupOpen(false);
          }}
          onOpenReferral={() => {
            setReferralPopupOpen(false);
            setDashboardView('referral');
          }}
        />
      </>
    );
  };

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/invite/:code" element={<InviteRedirectScreen />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route
        path="/login/oauth/:provider/callback"
        element={<OAuthCallbackScreen onAuthenticated={handleAuthSuccess} />}
      />
      <Route
        path="/login"
        element={
          <LoginScreen
            onBack={() => navigate('/')}
            onAuthenticated={handleAuthSuccess}
            defaultMode={hasOnboardingProfile ? 'register' : 'login'}
          />
        }
      />
      <Route path="/dashboard" element={dashboardElement()} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}
