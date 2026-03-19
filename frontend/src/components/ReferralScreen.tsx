import { ArrowLeft, Copy, Gift, Rocket } from 'lucide-react';
import { useEffect, useState } from 'react';

import { fetchReferralMe, fetchReferralStats, trackGrowthEvent } from '../api/auth';
import { ReferralMe, ReferralStats } from '../types';

interface Props {
  onBack: () => void;
}

export default function ReferralScreen({ onBack }: Props) {
  const [me, setMe] = useState<ReferralMe | null>(null);
  const [stats, setStats] = useState<ReferralStats | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const [mePayload, statsPayload] = await Promise.all([fetchReferralMe(), fetchReferralStats()]);
        setMe(mePayload);
        setStats(statsPayload);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Falha ao carregar referral.');
      }
    };
    load();
  }, []);

  const handleCopy = async () => {
    if (!me?.invite_link) return;
    await navigator.clipboard.writeText(me.invite_link);
    try {
      await trackGrowthEvent('referral_link_copied', { source: 'referral_screen' });
    } catch {
      // non-blocking analytics
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const handleSend = async () => {
    if (!me?.invite_link) return;
    try {
      await trackGrowthEvent('referral_sent', { source: 'referral_screen' });
    } catch {
      // non-blocking analytics
    }
    const text = encodeURIComponent(`Vamos praticar ingles com IA no LinguaAI: ${me.invite_link}`);
    window.open(`https://wa.me/?text=${text}`, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="min-h-screen bg-background-light pb-8">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-md items-center justify-between px-4">
          <button onClick={onBack} className="rounded-full p-2 hover:bg-slate-100">
            <ArrowLeft size={20} />
          </button>
          <p className="text-sm font-black tracking-wide">🚀 Convide amigos</p>
          <Gift size={18} className="text-amber-500" />
        </div>
      </header>

      <main className="mx-auto max-w-md space-y-4 px-4 pt-5">
        {error && <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h2 className="text-lg font-black">Seu link de convite</h2>
          <p className="mt-1 text-xs text-slate-500">Compartilhe e ganhe XP + bonus de acesso PRO para ambos.</p>
          <div className="mt-3 rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs font-semibold text-primary break-all">
            {me?.invite_link || 'Carregando link...'}
          </div>
          <button onClick={handleCopy} className="mt-3 w-full inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white">
            <Copy size={16} />
            {copied ? 'Copiado!' : 'Copiar link'}
          </button>
          <button onClick={handleSend} className="mt-2 w-full rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm font-bold text-primary">
            Enviar convite
          </button>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="text-sm font-black">Resumo de recompensas</h3>
          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-slate-500">Convites</p>
              <p className="mt-1 text-lg font-black">{stats?.referral_count ?? 0}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-slate-500">XP ganho</p>
              <p className="mt-1 text-lg font-black">{stats?.reward_xp_total ?? 0}</p>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-600">
            Bonus PRO ate: <span className="font-semibold">{stats?.pro_access_until || me?.pro_access_until || 'nao ativo'}</span>
          </p>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="text-sm font-black">Amigos convidados</h3>
          <div className="mt-3 space-y-2">
            {(stats?.invited_users || []).length === 0 ? (
              <p className="text-sm text-slate-500">Nenhum amigo convidado ainda.</p>
            ) : (
              stats?.invited_users.map((item) => (
                <div key={item.user_id} className="rounded-lg border border-slate-200 px-3 py-2">
                  <p className="text-sm font-semibold">{item.name}</p>
                  <p className="text-xs text-slate-500">{item.email}</p>
                </div>
              ))
            )}
          </div>
          <div className="mt-4 rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-slate-700">
            <p className="font-semibold">Beneficios:</p>
            <p className="mt-1">• +XP para quem convida e para quem entra</p>
            <p>• 1 dia de bonus PRO para ambos</p>
            <p>• Sistema anti-autoindicacao e codigo unico</p>
          </div>
          <button onClick={onBack} className="mt-3 inline-flex items-center gap-2 text-xs font-bold text-primary">
            <Rocket size={14} />
            Voltar ao dashboard
          </button>
        </section>
      </main>
    </div>
  );
}
