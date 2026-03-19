import { Bell, BookOpen, Crown, Flame, Home, Languages, LogOut, MessageSquare, Mic, Rocket, Send, Sparkles, User as UserIcon } from 'lucide-react';
import { useMemo, useState } from 'react';
import { AuthUser, DailyChallengeInfo, GrowthDashboardData, PedagogyDashboardData } from '../types';
import LearningProgressCard from './LearningProgressCard';
import SmartRecommendationCard from './SmartRecommendationCard';
import VocabularyReviewCard from './VocabularyReviewCard';
import WeaknessFocusCard from './WeaknessFocusCard';

interface Props {
  user: AuthUser;
  growthData: GrowthDashboardData | null;
  dailyChallenge: DailyChallengeInfo | null;
  pedagogyData?: PedagogyDashboardData | null;
  stripeConfigured: boolean;
  billingLoading: boolean;
  onStartLesson: () => void;
  onOpenChat: () => void;
  onOpenImmersion: () => void;
  onOpenRealLife: () => void;
  onOpenDailyChallenge: () => void;
  onOpenReferral: () => void;
  onOpenVoiceMentor: () => void;
  onOpenSettings: () => void;
  onReferralCopy: () => Promise<void> | void;
  onReferralSend: () => Promise<void> | void;
  onUpgrade: () => void;
  onOpenPedagogyRecommendation?: () => void;
  onOpenVocabularyReview?: () => void;
  onManageSubscription: () => void;
  onCancelSubscription: () => void;
  onLogout: () => void;
  appError?: string;
}

export default function DashboardScreen({
  user,
  growthData,
  dailyChallenge,
  pedagogyData,
  stripeConfigured,
  billingLoading,
  onStartLesson,
  onOpenChat,
  onOpenImmersion,
  onOpenRealLife,
  onOpenDailyChallenge,
  onOpenReferral,
  onOpenVoiceMentor,
  onOpenSettings,
  onReferralCopy,
  onReferralSend,
  onUpgrade,
  onOpenPedagogyRecommendation,
  onOpenVocabularyReview,
  onManageSubscription,
  onCancelSubscription,
  onLogout,
  appError,
}: Props) {
  const [copied, setCopied] = useState(false);
  const targetLanguage = user.target_language_code || user.target_language || 'pending';
  const progressPercent = growthData
    ? Math.min(100, Math.max(5, Math.round((growthData.xp_in_level / Math.max(1, growthData.xp_in_level + growthData.xp_to_next_level)) * 100)))
    : Math.min(100, Math.max(10, user.xp_total > 0 ? Math.round((user.xp_total % 100) || 100) : 18));
  const missionPercent = growthData
    ? Math.min(100, Math.round((growthData.mission_today.completed_sessions / Math.max(1, growthData.mission_today.target_sessions)) * 100))
    : 0;

  const referralCode = growthData?.referral.referral_code || user.referral_code || '';
  const inviteLink = referralCode ? `${window.location.origin}/invite/${referralCode}` : '';
  const referralCount = growthData?.referral.referred_count || 0;
  const referralGoal = 3;
  const referralProgress = Math.min(100, Math.round((referralCount / referralGoal) * 100));
  const hasReferralBadge = referralCount >= referralGoal;

  const handleCopyInviteLink = async () => {
    await onReferralCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="bg-background-light min-h-screen pb-24">
      <header className="sticky top-0 z-50 bg-background-light/80 backdrop-blur-md border-b border-primary/10">
        <div className="max-w-md mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="size-10 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
              <UserIcon size={18} className="text-primary" />
            </div>
            <div>
              <h1 className="text-sm font-bold leading-tight">{user.name}</h1>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 uppercase tracking-wider">
                  <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  Sessao ativa
                </span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button type="button" onClick={onOpenSettings} aria-label="Abrir configuracoes" className="p-2 rounded-full transition-colors hover:bg-slate-100">
              <Bell size={20} className="text-slate-600" />
            </button>
            <button type="button" onClick={onLogout} aria-label="Sair da conta" className="p-2 hover:bg-red-50 rounded-full transition-colors">
              <LogOut size={20} className="text-red-500" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-md mx-auto px-4 pt-6 space-y-6">
        {appError && <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{appError}</div>}

        <section className="grid grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-xl border border-primary/10 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <Flame size={16} className="text-orange-500 fill-orange-500" />
              <p className="text-xs font-medium text-slate-500">Streak</p>
            </div>
            <div className="flex items-baseline gap-2">
              <p className="text-2xl font-bold">{growthData?.current_streak ?? user.current_streak ?? 0}</p>
              <p className="text-xs font-bold text-orange-500">max {growthData?.longest_streak ?? user.longest_streak ?? 0}</p>
            </div>
          </div>
          <div className="bg-white p-4 rounded-xl border border-primary/10 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles size={16} className="text-yellow-500" />
              <p className="text-xs font-medium text-slate-500">XP Total</p>
            </div>
            <div className="flex items-baseline gap-2">
              <p className="text-2xl font-bold">{user.xp_total}</p>
              <p className="text-xs font-bold text-emerald-500">Level {user.level}</p>
            </div>
          </div>
        </section>

        {pedagogyData ? (
          <section className="space-y-3">
            <LearningProgressCard data={pedagogyData} />
            <WeaknessFocusCard data={pedagogyData} />
            <SmartRecommendationCard
              data={pedagogyData}
              onAction={onOpenPedagogyRecommendation || onOpenChat}
            />
            <VocabularyReviewCard
              data={pedagogyData}
              onReview={onOpenVocabularyReview || onOpenChat}
            />
          </section>
        ) : null}

        {growthData && (
          <section className="rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/10 via-white to-amber-50 p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-black">🚀 Convide amigos</h2>
              <button type="button" onClick={onOpenReferral} className="text-xs font-bold text-primary">Abrir painel</button>
            </div>
            <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-bold text-amber-700">
              🔥 Convide hoje e ganhe bonus dobrado
            </p>
            <p className="text-sm text-slate-700">Recompensa: <span className="font-black">+XP para ambos + 1 dia PRO</span></p>
            <div className="rounded-lg border border-primary/20 bg-white px-3 py-2 text-xs font-semibold text-primary break-all">{inviteLink || 'Link indisponivel'}</div>
            <div className="grid grid-cols-2 gap-2">
              <button type="button" onClick={handleCopyInviteLink} className="rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white">
                {copied ? 'Copiado!' : 'Copiar link'}
              </button>
              <button type="button" onClick={onReferralSend} className="inline-flex items-center justify-center gap-2 rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm font-bold text-primary">
                <Send size={14} />
                Enviar convite
              </button>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="rounded-lg bg-white p-3 border border-slate-200">
                <p className="text-slate-500">Codigo</p>
                <p className="mt-1 font-black">{referralCode || '--'}</p>
              </div>
              <div className="rounded-lg bg-white p-3 border border-slate-200">
                <p className="text-slate-500">Convites</p>
                <p className="mt-1 font-black">{referralCount}</p>
              </div>
              <div className="rounded-lg bg-white p-3 border border-slate-200">
                <p className="text-slate-500">Badge</p>
                <p className="mt-1 font-black">{hasReferralBadge ? 'Ativa' : 'Em progresso'}</p>
              </div>
            </div>
            <div>
              <div className="mb-1 flex items-center justify-between text-xs text-slate-600">
                <span>Meta: convide 3 amigos</span>
                <span className="font-bold">{referralCount}/{referralGoal}</span>
              </div>
              <div className="h-2.5 overflow-hidden rounded-full bg-slate-200">
                <div className="h-full rounded-full bg-emerald-500" style={{ width: `${referralProgress}%` }}></div>
              </div>
            </div>
          </section>
        )}

        {growthData && (
          <section className="bg-white p-5 rounded-xl border border-primary/10 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Missoes diarias</h2>
              <span className="text-xs font-bold text-primary">{missionPercent}%</span>
            </div>
            <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${missionPercent}%` }}></div>
            </div>
            <p className="text-sm text-slate-600">
              Sessoes: <span className="font-bold">{growthData.mission_today.completed_sessions}/{growthData.mission_today.target_sessions}</span>
              {' '}• Bonus XP: <span className="font-bold">{growthData.mission_today.bonus_xp_awarded ? 'desbloqueado' : 'pendente'}</span>
            </p>
          </section>
        )}

        <section className="bg-white p-5 rounded-xl border border-primary/10 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">🔥 Desafio do Dia</h2>
            {dailyChallenge?.daily_badge_earned ? (
              <span className="rounded-full bg-emerald-100 px-2 py-1 text-[10px] font-bold uppercase text-emerald-700">badge</span>
            ) : (
              <span className="rounded-full bg-amber-100 px-2 py-1 text-[10px] font-bold uppercase text-amber-700">ativo</span>
            )}
          </div>
          <p className="text-sm text-slate-700">{dailyChallenge?.challenge_title || 'Carregando desafio...'}</p>
          <p className="text-xs text-slate-500">
            Cenario: <span className="font-semibold capitalize">{dailyChallenge?.scenario || '--'}</span>
            {' '}• Score hoje: <span className="font-semibold">{dailyChallenge?.best_score_today ?? 0}</span>
          </p>
          <button type="button" onClick={onOpenDailyChallenge} className="w-full rounded-xl bg-slate-900 text-white px-4 py-3 text-sm font-bold">
            Jogar agora
          </button>
        </section>

        <section className="rounded-xl border border-indigo-200 bg-indigo-50/60 p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-black">🎙️ Falar com mentor por voz</h2>
            <span className={`rounded-full px-2 py-1 text-[10px] font-bold uppercase ${user.plan === 'PRO' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
              {user.plan === 'PRO' ? 'PRO ativo' : 'premium'}
            </span>
          </div>
          <p className="text-sm text-slate-700">
            {user.plan === 'PRO'
              ? 'Escolha um mentor de voz e pratique com resposta em texto + audio.'
              : 'Teste 6 interacoes gratis por voz e desbloqueie o PRO para ilimitado.'}
          </p>
          <button
            type="button"
            onClick={onOpenVoiceMentor}
            className="w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white"
          >
            {user.plan === 'PRO' ? 'Abrir mentores de voz' : 'Experimentar voz gratis'}
          </button>
        </section>

        {growthData && (
          <section className="bg-white p-5 rounded-xl border border-primary/10 shadow-sm space-y-3">
            <h2 className="text-lg font-bold">Resumo semanal</h2>
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-[11px] text-slate-500">Sessoes</p>
                <p className="text-lg font-bold">{growthData.weekly_sessions_total}</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-[11px] text-slate-500">Minutos</p>
                <p className="text-lg font-bold">{growthData.weekly_minutes_total}</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-[11px] text-slate-500">XP</p>
                <p className="text-lg font-bold">{growthData.weekly_xp_total}</p>
              </div>
            </div>
          </section>
        )}

        <section className="bg-white p-5 rounded-xl border border-primary/10 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold">Progresso diario</h2>
            <span className="text-primary font-bold text-sm">{progressPercent}%</span>
          </div>
          <div className="w-full bg-slate-200 h-3 rounded-full overflow-hidden mb-3">
            <div className="bg-primary h-full rounded-full" style={{ width: `${progressPercent}%` }}></div>
          </div>
          <p className="text-sm text-slate-500 font-medium">
            Idioma alvo: <span className="font-bold uppercase text-slate-700">{targetLanguage}</span>
          </p>
        </section>

        <section className="relative overflow-hidden bg-primary rounded-xl p-6 text-white shadow-lg shadow-primary/30">
          <div className="absolute top-0 right-0 -mr-8 -mt-8 size-32 bg-white/10 rounded-full blur-2xl"></div>
          <div className="relative z-10">
            <span className="inline-block px-2 py-1 bg-white/20 rounded text-[10px] font-bold uppercase tracking-widest mb-3">
              recomendado
            </span>
            <h3 className="text-xl font-bold mb-1">Licao guiada com XP real</h3>
            <p className="text-sm opacity-90 mb-6">Sessao persistida no backend • onboarding {user.onboarding_completed ? 'ok' : 'pendente'}</p>
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] opacity-70">Timezone</p>
                <p className="text-sm font-semibold">{user.timezone}</p>
              </div>
              <button
                type="button"
                onClick={onStartLesson}
                className="bg-white text-primary font-bold px-6 py-2.5 rounded-lg text-sm hover:bg-slate-50 transition-colors shadow-md"
              >
                Comecar agora
              </button>
            </div>
          </div>
        </section>

        <section className="bg-white p-5 rounded-xl border border-primary/10 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold">Monetizacao</h2>
              <p className="text-sm text-slate-500">Stripe {stripeConfigured ? 'configurado' : 'nao configurado'}</p>
            </div>
            <Crown className={user.plan === 'PRO' ? 'text-yellow-500' : 'text-slate-300'} size={24} />
          </div>

          {user.plan === 'PRO' ? (
            <div className="space-y-3">
              <div className="rounded-xl bg-emerald-50 border border-emerald-200 px-4 py-3 text-sm text-emerald-700">
                Seu acesso PRO esta ativo com status {user.subscription_status || 'active'}.
              </div>
              <button
                type="button"
                onClick={onManageSubscription}
                disabled={billingLoading || !stripeConfigured}
                className="w-full rounded-xl bg-slate-900 text-white px-4 py-3 font-bold disabled:opacity-50"
              >
                {billingLoading ? 'Abrindo portal...' : 'Gerenciar assinatura PRO'}
              </button>
              <button
                type="button"
                onClick={onCancelSubscription}
                disabled={billingLoading || !stripeConfigured}
                className="w-full rounded-xl border border-red-200 bg-red-50 text-red-700 px-4 py-3 font-bold disabled:opacity-50"
              >
                {billingLoading ? 'Processando...' : 'Cancelar assinatura PRO'}
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
                Plano FREE: mentor premium, ranking completo e bonus ampliados liberados no PRO.
              </div>
              <button
                type="button"
                onClick={onUpgrade}
                disabled={billingLoading || !stripeConfigured}
                className="w-full flex items-center justify-center gap-2 rounded-xl bg-slate-900 text-white px-4 py-3 font-bold disabled:opacity-50"
              >
                <Rocket size={18} />
                {billingLoading ? 'Abrindo checkout...' : stripeConfigured ? 'Assinar plano PRO' : 'Stripe indisponivel'}
              </button>
            </div>
          )}
        </section>

        {growthData && (
          <section className="bg-white p-5 rounded-xl border border-primary/10 shadow-sm space-y-3">
            <h2 className="text-lg font-bold">Ranking semanal</h2>
            {growthData.leaderboard_top.length === 0 ? (
              <p className="text-sm text-slate-500">Seja o primeiro a pontuar nesta semana.</p>
            ) : (
              <div className="space-y-2">
                {growthData.leaderboard_top.slice(0, 5).map((item) => (
                  <div key={item.user_id} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2">
                    <p className="text-sm font-semibold">#{item.rank} {item.name}</p>
                    <p className="text-sm font-bold text-primary">{item.xp_week} XP</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        <section className="space-y-3">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold">Atalhos</h2>
            <span className="text-sm font-semibold text-primary">Backend ao vivo</span>
          </div>
          <div className="space-y-3">
            <button type="button" onClick={onStartLesson} className="w-full flex items-center gap-4 p-4 bg-white rounded-xl border border-primary/10 text-left">
              <div className="size-12 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600">
                <BookOpen size={24} />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-sm">Iniciar lesson</h4>
                <p className="text-xs text-slate-500">Cria e conclui study session com XP.</p>
              </div>
            </button>
            <button type="button" onClick={onOpenChat} className="w-full flex items-center gap-4 p-4 bg-white rounded-xl border border-primary/10 text-left">
              <div className="size-12 rounded-lg bg-purple-100 flex items-center justify-center text-purple-600">
                <Languages size={24} />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-sm">Abrir mentor chat</h4>
                <p className="text-xs text-slate-500">Usa `/mentor/chat` com historico persistido.</p>
              </div>
            </button>
            <button type="button" onClick={onOpenImmersion} className="w-full flex items-center gap-4 p-4 bg-white rounded-xl border border-primary/10 text-left">
              <div className="size-12 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-600">
                <Rocket size={24} />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-sm">Abrir Immersion Engine</h4>
                <p className="text-xs text-slate-500">Roleplay de vida real + analise de fluencia.</p>
              </div>
            </button>
            <button type="button" onClick={onOpenRealLife} className="w-full flex items-center gap-4 p-4 bg-white rounded-xl border border-primary/10 text-left">
              <div className="size-12 rounded-lg bg-rose-100 flex items-center justify-center text-rose-600">
                <Flame size={24} />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-sm">🔥 Modo Vida Real</h4>
                <p className="text-xs text-slate-500">Simulacoes com pressao, feedback e bonus de XP.</p>
              </div>
            </button>
            <button type="button" onClick={onOpenVoiceMentor} className="w-full flex items-center gap-4 p-4 bg-white rounded-xl border border-primary/10 text-left">
              <div className="size-12 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-600">
                <Mic size={24} />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-sm">🎙️ Falar com mentor por voz</h4>
                <p className="text-xs text-slate-500">
                  {user.plan === 'PRO' ? 'Conversa por voz com mentores e replay de respostas.' : 'Premium PRO: desbloqueie mentores de voz naturais.'}
                </p>
              </div>
            </button>
            <button type="button" onClick={onOpenReferral} className="w-full flex items-center gap-4 p-4 bg-white rounded-xl border border-primary/10 text-left">
              <div className="size-12 rounded-lg bg-amber-100 flex items-center justify-center text-amber-600">
                <Rocket size={24} />
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-sm">🚀 Convide amigos</h4>
                <p className="text-xs text-slate-500">Compartilhe seu link e ganhe XP + bonus PRO.</p>
              </div>
            </button>
          </div>
        </section>
      </main>

      <nav className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-lg border-t border-slate-200 px-4 pb-6 pt-2 z-50">
        <div className="max-w-md mx-auto flex justify-between items-center">
          <button type="button" aria-label="Tela atual inicio" disabled className="flex flex-col items-center gap-1 flex-1 text-primary cursor-default">
            <Home size={24} className="fill-primary" />
            <span className="text-[10px] font-bold">Inicio</span>
          </button>
          <button type="button" onClick={onStartLesson} className="flex flex-col items-center gap-1 flex-1 text-slate-400">
            <BookOpen size={24} />
            <span className="text-[10px] font-bold">Licoes</span>
          </button>
          <button type="button" onClick={onUpgrade} className="flex flex-col items-center gap-1 flex-1 text-slate-400">
            <Crown size={24} />
            <span className="text-[10px] font-bold">Billing</span>
          </button>
          <button type="button" onClick={onOpenImmersion} className="flex flex-col items-center gap-1 flex-1 text-slate-400">
            <Rocket size={24} />
            <span className="text-[10px] font-bold">Imersao</span>
          </button>
          <button type="button" onClick={onOpenSettings} aria-label="Abrir configuracoes" className="flex flex-col items-center gap-1 flex-1 text-slate-400">
            <UserIcon size={24} />
            <span className="text-[10px] font-bold">Config</span>
          </button>
        </div>
      </nav>

      <button
        type="button"
        onClick={onOpenChat}
        className="fixed bottom-28 right-6 size-14 bg-primary text-white rounded-full shadow-xl flex items-center justify-center hover:scale-110 transition-transform z-40"
      >
        <MessageSquare size={28} />
      </button>
    </div>
  );
}
