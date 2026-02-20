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
import Input from "../../shared/ui/Input.jsx";
import { useAuth } from "../../hooks/useAuth.js";
import {
  getCurrentUser,
  updateUser
} from "../../services/userService.js";
import {
  getDailyMessage,
  getStreak
} from "../../services/dailyMessageService.js";
import {
  getMentorHistory,
  getWeeklyProgress
} from "../../services/mentorService.js";
import {
  subscribePro,
  cancelSubscription,
  openCustomerPortal
} from "../../services/billingService.js";

export default function Dashboard() {
  const { user, setUser, logout } = useAuth();
  const [dailyMessage, setDailyMessage] = useState(null);
  const [history, setHistory] = useState([]);
  const [streak, setStreak] = useState(null);
  const [progress, setProgress] = useState([]);
  const [error, setError] = useState("");
  const [settings, setSettings] = useState({ target_language_code: "", timezone: "" });
  const [billingLoading, setBillingLoading] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const profile = await getCurrentUser();
        if (profile) {
          setUser(profile);
          setSettings({
            target_language_code: profile.target_language_code || "",
            timezone: profile.timezone || "UTC"
          });
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
      } catch (err) {
        setError(err.message || "Erro ao carregar");
      }
    })();
  }, [setUser]);

  const onSaveSettings = async (e) => {
    e.preventDefault();
    if (!user) return;
    try {
      const updated = await updateUser(user.id, {
        target_language_code: settings.target_language_code || null,
        timezone: settings.timezone || "UTC"
      });
      setUser(updated);
    } catch (err) {
      setError(err.message || "Falha ao salvar");
    }
  };

  const handleSubscribe = async () => {
    setBillingLoading(true);
    try {
      const { checkout_url } = await subscribePro();
      if (checkout_url) {
        window.location.href = checkout_url;
      }
    } catch (err) {
      setError(err.message || "Falha ao iniciar assinatura");
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
    } catch (err) {
      setError(err.message || "Falha ao cancelar assinatura");
    } finally {
      setBillingLoading(false);
    }
  };

  const handlePortal = async () => {
    setBillingLoading(true);
    try {
      const { portal_url } = await openCustomerPortal();
      if (portal_url) {
        window.location.href = portal_url;
      }
    } catch (err) {
      setError(err.message || "Falha ao abrir portal");
    } finally {
      setBillingLoading(false);
    }
  };

  if (!user) return null;

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
              Plano {user.plan} · Nível {user.level}
            </p>
          </Card>

          <StreakBadge streak={streak} />
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
            <h3 className="font-display text-xl">Configurações rápidas</h3>
            <form onSubmit={onSaveSettings} className="mt-4 space-y-4">
              <Input
                label="Idioma alvo (ISO 639-3)"
                value={settings.target_language_code}
                onChange={(e) => setSettings({ ...settings, target_language_code: e.target.value })}
                placeholder="por"
              />
              <Input
                label="Fuso horário"
                value={settings.timezone}
                onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                placeholder="America/Sao_Paulo"
              />
              <Button type="submit">Salvar</Button>
            </form>
          </Card>

          <Card>
            <h3 className="font-display text-xl">Assinatura PRO</h3>
            <p className="text-slate-600 mt-2">Status Stripe: {user.subscription_status || "não configurado"}</p>
            {user.plan === "FREE" ? (
              <Button className="mt-4" onClick={handleSubscribe} disabled={billingLoading}>
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

          <AdsPanel visible={user.plan === "FREE"} placement="home" />
        </div>
      </div>
    </PageShell>
  );
}
