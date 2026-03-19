import { ArrowLeft, BadgeCheck, Flame, RotateCcw, Send, Timer } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { fetchDailyChallenge, sendRealLifeMessage, startDailyChallenge, submitDailyChallenge } from '../api/auth';
import { DailyChallengeInfo, DailyChallengeStartResponse, DailyChallengeSubmitResponse, RealLifeFeedback } from '../types';

interface Props {
  onBack: () => void;
  onRefresh?: () => Promise<void> | void;
  onCompleted?: () => Promise<void> | void;
}

interface ChatLine {
  role: 'user' | 'ai';
  text: string;
}

const emptyFeedback: RealLifeFeedback = {
  correction: '',
  better_response: '',
  pressure_note: '',
  level_adaptation: '',
};

export default function DailyChallengeScreen({ onBack, onRefresh, onCompleted }: Props) {
  const [daily, setDaily] = useState<DailyChallengeInfo | null>(null);
  const [run, setRun] = useState<DailyChallengeStartResponse | null>(null);
  const [result, setResult] = useState<DailyChallengeSubmitResponse | null>(null);
  const [chat, setChat] = useState<ChatLine[]>([]);
  const [feedback, setFeedback] = useState<RealLifeFeedback>(emptyFeedback);
  const [message, setMessage] = useState('');
  const [questionStartedAt, setQuestionStartedAt] = useState<number | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const info = await fetchDailyChallenge();
        setDaily(info);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Falha ao carregar desafio diario.');
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (!questionStartedAt || !run) return;
    const timer = setInterval(() => {
      const sec = Math.max(0, Math.round((Date.now() - questionStartedAt) / 1000));
      setElapsed(sec);
    }, 1000);
    return () => clearInterval(timer);
  }, [questionStartedAt, run]);

  const pressureLeft = useMemo(() => {
    if (!run) return '--';
    return Math.max(0, run.pressure_seconds - elapsed);
  }, [run, elapsed]);

  const start = async () => {
    setLoading(true);
    setError('');
    try {
      const started = await startDailyChallenge();
      setRun(started);
      setChat([{ role: 'ai', text: started.opening_message }]);
      setResult(null);
      setFeedback(emptyFeedback);
      setMessage('');
      setQuestionStartedAt(Date.now());
      setElapsed(0);
      setDaily(await fetchDailyChallenge());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nao foi possivel iniciar o desafio.');
    } finally {
      setLoading(false);
    }
  };

  const send = async () => {
    if (!run || !message.trim() || loading) return;
    setLoading(true);
    setError('');
    const clean = message.trim();
    try {
      const response = await sendRealLifeMessage(run.session_id, clean, elapsed);
      setChat((prev) => [...prev, { role: 'user', text: clean }, { role: 'ai', text: response.ai_question }]);
      setFeedback(response.feedback);
      setMessage('');
      setQuestionStartedAt(Date.now());
      setElapsed(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao enviar resposta.');
    } finally {
      setLoading(false);
    }
  };

  const finish = async () => {
    if (!run) return;
    setLoading(true);
    setError('');
    try {
      const submitted = await submitDailyChallenge(run.challenge_id);
      setResult(submitted);
      setDaily(await fetchDailyChallenge());
      if (onRefresh) await onRefresh();
      if (onCompleted) await onCompleted();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao enviar score do desafio.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background-light pb-8">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-md items-center justify-between px-4">
          <button onClick={onBack} className="rounded-full p-2 hover:bg-slate-100">
            <ArrowLeft size={20} />
          </button>
          <p className="text-sm font-black tracking-wide">🔥 Desafio do Dia</p>
          {daily?.daily_badge_earned ? <BadgeCheck size={18} className="text-emerald-600" /> : <Flame size={18} className="text-amber-500" />}
        </div>
      </header>

      <main className="mx-auto max-w-md space-y-4 px-4 pt-5">
        {error && <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <section className="rounded-xl border border-primary/10 bg-white p-4">
          <h2 className="text-lg font-black">{daily?.challenge_title || 'Desafio Diario'}</h2>
          <p className="mt-1 text-xs text-slate-600">
            Cenario: <span className="font-semibold capitalize">{daily?.scenario || '--'}</span> • Dificuldade: {daily?.difficulty_level || 1}
          </p>
          <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
            <div className="rounded-lg bg-slate-50 p-2">
              <p className="text-slate-500">Tentativas</p>
              <p className="font-bold">{daily?.attempts_today ?? 0}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-2">
              <p className="text-slate-500">Melhor score</p>
              <p className="font-bold">{daily?.best_score_today ?? 0}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-2">
              <p className="text-slate-500">Sem penalidade</p>
              <p className="font-bold">{daily?.can_play_without_penalty ? 'Sim' : 'Nao'}</p>
            </div>
          </div>
          <button onClick={start} disabled={loading} className="mt-3 w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white disabled:opacity-60">
            Jogar agora
          </button>
        </section>

        {run && (
          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <div className="mb-2 flex items-center justify-between">
              <p className="text-sm font-bold">Chat do desafio</p>
              <p className={`flex items-center gap-1 text-xs font-bold ${pressureLeft <= 5 ? 'text-red-600' : 'text-slate-700'}`}>
                <Timer size={12} />
                {pressureLeft}s
              </p>
            </div>
            <div className="max-h-64 space-y-2 overflow-y-auto rounded-lg bg-slate-50 p-3">
              {chat.map((line, idx) => (
                <div key={`${line.role}-${idx}`} className={`rounded-lg px-3 py-2 text-sm ${line.role === 'ai' ? 'border border-slate-200 bg-white' : 'ml-6 bg-primary text-white'}`}>
                  <p className="mb-1 text-[10px] font-bold uppercase opacity-70">{line.role === 'ai' ? run.character_role : 'Voce'}</p>
                  <p>{line.text}</p>
                </div>
              ))}
            </div>
            <div className="mt-3 flex gap-2">
              <input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Responda em ingles..."
                className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
              <button onClick={send} disabled={loading} className="rounded-lg bg-primary px-3 py-2 text-white disabled:opacity-60">
                <Send size={16} />
              </button>
            </div>
            <button onClick={finish} disabled={loading} className="mt-2 w-full rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-bold text-emerald-700 disabled:opacity-60">
              Finalizar desafio
            </button>
          </section>
        )}

        {feedback.correction && (
          <section className="rounded-xl border border-slate-200 bg-white p-4 text-sm">
            <p className="font-bold">Feedback da IA</p>
            <p className="mt-2 text-slate-700"><strong>Correcao:</strong> {feedback.correction}</p>
            <p className="mt-1 text-slate-700"><strong>Resposta melhor:</strong> {feedback.better_response}</p>
            <p className="mt-1 text-slate-700"><strong>Pressao:</strong> {feedback.pressure_note}</p>
          </section>
        )}

        {result && (
          <section className="rounded-xl border border-primary/20 bg-primary/5 p-4">
            <p className="text-sm font-black">Resultado do desafio</p>
            <p className="mt-1 text-sm">Score: <span className="font-black">{result.score}</span> • XP extra: <span className="font-black">{result.xp_awarded}</span></p>
            <p className="mt-1 text-xs text-slate-600">Melhor score do dia: {result.best_score_today} • Tentativas: {result.attempts_today}</p>
            <p className="mt-1 text-xs text-slate-600">Badge diaria: {result.badge_awarded ? 'desbloqueada' : 'nao desbloqueada'}</p>
            <button onClick={start} className="mt-3 inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-bold text-slate-700">
              <RotateCcw size={14} />
              Tentar novamente
            </button>
          </section>
        )}
      </main>
    </div>
  );
}
