import React, { useEffect, useState } from "react";
import PageShell from "../../shared/layouts/PageShell.jsx";
import NavBar from "../../shared/components/NavBar.jsx";
import DailyMessage from "../../shared/components/DailyMessage.jsx";
import AdsPanel from "../../shared/components/AdsPanel.jsx";
import ProgressChart from "../../shared/components/ProgressChart.jsx";
import HistoryList from "../../shared/components/HistoryList.jsx";
import StreakBadge from "../../shared/components/StreakBadge.jsx";
import Card from "../../shared/ui/Card.jsx";
import Button from "../../shared/ui/Button.jsx";
import { useAuth } from "../../hooks/useAuth.jsx";
import {
  getCurrentUser,
} from "../../services/userService.js";
import {
  getDailyMessage,
  getStreak
} from "../../services/dailyMessageService.js";
import {
  getMentorHistory,
  getWeeklyProgress
} from "../../services/mentorService.js";
import { getProgressSummary } from "../../services/learnaService.js";
import {
  getBillingStatus,
  subscribePro,
  cancelSubscription,
  openCustomerPortal
} from "../../services/billingService.js";
import { startProCheckout } from "./checkoutFlow.js";

export default function Dashboard() {
  const { user, setUser, logout } = useAuth();
  const [dailyMessage, setDailyMessage] = useState(null);
  const [history, setHistory] = useState([]);
  const [streak, setStreak] = useState(null);
  const [progress, setProgress] = useState([]);
  const [summary, setSummary] = useState({ xp_total: 0, level: 0, streak_days: 0, weekly_minutes: 0 });
  const [error, setError] = useState("");
  const [billingLoading, setBillingLoading] = useState(false);
  const [billingStatus, setBillingStatus] = useState({ stripe_configured: false, plan: "FREE", subscription_status: null });

  useEffect(() => {
    (async () => {
      try {
        setError("");
        const profile = await getCurrentUser();
        if (profile) {
          setUser(profile);
        }

        const todayKey = new Date().toISOString().slice(0, 10);
        const seenKey = `daily_message_${todayKey}`;
        if (!localStorage.getItem(seenKey)) {
          const msg = await getDailyMessage();
          setDailyMessage(msg);
          localStorage.setItem(seenKey, "true");
        }

        const historyData = await getMentorHistory();
        setHistory(historyData || []);
        const streakData = await getStreak();
        setStreak(streakData?.streak || 0);
        const progressData = await getWeeklyProgress();
        setProgress(progressData || []);
        const summaryData = await getProgressSummary();
        setSummary(summaryData || { xp_total: 0, level: profile?.level || 0, streak_days: 0, weekly_minutes: 0 });

        const billing = await getBillingStatus();
        setBillingStatus(
          billing || {
            stripe_configured: false,
            plan: profile?.plan || "FREE",
            subscription_status: profile?.subscription_status || null,
          }
        );
      } catch (err) {
        setError(err.message || "Erro ao carregar");
      }
    })();
  }, [setUser]);

const handleSubscribe = async () => {
  setBillingLoading(true);
  try {
    const data = await subscribePro();
    const url = data?.checkout_url || data?.url;

    if (url) {
      window.location.href = url;
    } else {
      setError("Checkout indisponível no momento.");
    }
  } catch (err) {
    setError(err.message || "Checkout indisponível no momento.");
  } finally {
    setBillingLoading(false);
  }
};

  const handleCancel = async () => {
    setBillingLoading(true);
    try {
      await cancelSubscription();
      const refreshed = await getCurrentUser();
      setUser(refreshed);
      const billing = await getBillingStatus();
      setBillingStatus(
        billing || {
          stripe_configured: false,
          plan: refreshed?.plan || "FREE",
          subscription_status: refreshed?.subscription_status || null,
        }
      );
    } catch (err) {
      setError(err.message || "Stripe não configurado para cancelamento");
    } finally {
      setBillingLoading(false);
    }
  };

const handlePortal = async () => {
  setBillingLoading(true);
  try {
    const data = await openCustomerPortal();
    const url = data?.portal_url || data?.url;

    if (url) {
      window.location.href = url;
    } else {
      setError("Portal indisponível no momento.");
    }
  } catch (err) {
    setError(err.message || "Portal indisponível no momento.");
  } finally {
    setBillingLoading(false);
  }
};

  if (!user) return null;
  const currentPlan = billingStatus.plan || user.plan || "FREE";
  const chosenLanguage = user.target_language || user.language || user.target_language_code;
  const currentLevel = Math.max(Number(user.level || 0), Number(summary.level || 0));

  const progressData = progress.map((item) => ({
    label: item.label,
    value: item.count
  }));

  return (
    <PageShell>
      <NavBar user={user} onLogout={logout} />
      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <Card>
            <p className="text-xs uppercase tracking-[0.2em] text-lagoon">Seu painel</p>
            <h2 className="font-display text-3xl mt-2">Olá, {user.name}</h2>
            <p className="text-slate-600 mt-2">
              Plano {currentPlan} · Nivel {currentLevel}
            </p>
            <p className="text-slate-600 mt-1">XP total: {summary.xp_total}</p>
          </Card>

          <StreakBadge streak={streak ?? summary.streak_days} />
          <DailyMessage message={dailyMessage} />

          <Card>
            <h3 className="font-display text-xl">Progresso semanal</h3>
            <p className="text-slate-600 mt-2">Seu ritmo de estudo nos últimos 7 dias.</p>
            <div className="mt-4">
              <ProgressChart data={progressData} />
            </div>
          </Card>

          <Card>
            <h3 className="font-display text-xl">Histórico recente</h3>
            <HistoryList items={history} />
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <h3 className="font-display text-xl">Preferências</h3>
            <p className="text-slate-600 mt-2">Idioma alvo: {chosenLanguage || "não definido"}</p>
            <p className="text-slate-600 mt-1">Fuso horário: {user.timezone}</p>
          </Card>

          <Card>
            <h3 className="font-display text-xl">Assinatura PRO</h3>
            <p className="text-slate-600 mt-2">
              Stripe: {billingStatus.stripe_configured ? "configurado" : "não configurado"}
            </p>
            <p className="text-slate-600 mt-1">Status assinatura: {billingStatus.subscription_status || user.subscription_status || "nenhuma"}</p>
            {currentPlan === "FREE" ? (
              <Button type="button" className="mt-4" onClick={handleSubscribe} disabled={billingLoading}>
                {billingLoading ? "Abrindo..." : "Assinar PRO"}
              </Button>
            ) : (
              <div className="mt-4 flex flex-wrap gap-3">
                <Button variant="secondary" onClick={handlePortal} disabled={billingLoading}>
                  Gerenciar assinatura
                </Button>
                <Button variant="secondary" onClick={handleCancel} disabled={billingLoading}>
                  {billingLoading ? "Cancelando..." : "Cancelar assinatura"}
                </Button>
              </div>
            )}
          </Card>

          <AdsPanel visible={currentPlan === "FREE"} placement="home" />
        </div>
      </div>
    </PageShell>
  );
}
