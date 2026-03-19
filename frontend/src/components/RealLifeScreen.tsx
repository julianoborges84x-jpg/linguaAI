import { ArrowLeft, Flame, RotateCcw, Send, Timer } from 'lucide-react';
import { useMemo, useState } from 'react';

import { sendRealLifeMessage, startRealLifeSession } from '../api/auth';
import { RealLifeFeedback, RealLifeMessageResponse, RealLifeSessionStart } from '../types';

interface Props {
  onBack: () => void;
}

const SCENARIOS = [
  'Restaurante',
  'Aeroporto',
  'Entrevista de emprego',
  'Reuniao de trabalho',
  'Date / conversa casual',
  'Emergencia',
];

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

export default function RealLifeScreen({ onBack }: Props) {
  const [scenario, setScenario] = useState<string>(SCENARIOS[0]);
  const [session, setSession] = useState<RealLifeSessionStart | null>(null);
  const [chat, setChat] = useState<ChatLine[]>([]);
  const [message, setMessage] = useState('');
  const [feedback, setFeedback] = useState<RealLifeFeedback>(emptyFeedback);
  const [status, setStatus] = useState<'idle' | 'active' | 'completed' | 'failed'>('idle');
  const [error, setError] = useState('');
  const [sessionStartedAt, setSessionStartedAt] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastSessionId, setLastSessionId] = useState<number | null>(null);
  const [xpSession, setXpSession] = useState(0);

  const pressureLabel = useMemo(() => {
    if (!session) return '--';
    return `${session.pressure_seconds}s`;
  }, [session]);

  const start = async (retrySessionId?: number | null) => {
    setLoading(true);
    setError('');
    try {
      const payload = await startRealLifeSession(scenario, retrySessionId || undefined);
      setSession(payload);
      setChat([{ role: 'ai', text: payload.opening_message }]);
      setFeedback(emptyFeedback);
      setStatus('active');
      setSessionStartedAt(Date.now());
      setXpSession(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nao foi possivel iniciar o modo.');
    } finally {
      setLoading(false);
    }
  };

  const submitMessage = async () => {
    if (!session || !message.trim() || status !== 'active') return;
    const elapsedSec = sessionStartedAt ? Math.max(1, Math.round((Date.now() - sessionStartedAt) / 1000)) : session.pressure_seconds + 1;
    const cleanMessage = message.trim();
    setLoading(true);
    setError('');
    try {
      const payload: RealLifeMessageResponse = await sendRealLifeMessage(session.session_id, cleanMessage, elapsedSec);
      setChat((prev) => [...prev, { role: 'user', text: cleanMessage }, { role: 'ai', text: payload.ai_question }]);
      setFeedback(payload.feedback);
      setStatus(payload.status);
      setSessionStartedAt(Date.now());
      setSession((prev) => (prev ? { ...prev, pressure_seconds: payload.pressure_seconds, difficulty_level: payload.difficulty_level } : prev));
      setLastSessionId(payload.session_id);
      setXpSession(payload.total_xp_session);
      setMessage('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao enviar resposta.');
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
          <p className="text-sm font-black tracking-wide">Real Life Mode</p>
          <span className={`rounded-full px-2 py-1 text-[10px] font-bold uppercase ${status === 'active' ? 'bg-emerald-100 text-emerald-700' : status === 'completed' ? 'bg-cyan-100 text-cyan-700' : status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'}`}>
            {status}
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-md space-y-4 px-4 pt-5">
        {error && <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h2 className="text-lg font-black">Modo Vida Real</h2>
          <p className="mt-1 text-xs text-slate-600">Escolha uma situacao e pratique sob pressao com IA ativa.</p>
          <div className="mt-3 grid grid-cols-2 gap-2">
            {SCENARIOS.map((item) => (
              <button
                key={item}
                onClick={() => setScenario(item)}
                className={`rounded-lg border px-3 py-2 text-left text-xs font-semibold ${scenario === item ? 'border-primary bg-primary/10 text-primary' : 'border-slate-200 bg-slate-50 text-slate-700'}`}
              >
                {item}
              </button>
            ))}
          </div>
          <button
            onClick={() => start()}
            disabled={loading}
            className="mt-3 w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white disabled:opacity-60"
          >
            🔥 Iniciar simulacao
          </button>
        </section>

        {session && (
          <section className="grid grid-cols-3 gap-2 text-xs">
            <div className="rounded-lg border border-slate-200 bg-white p-3">
              <p className="text-slate-500">Situacao</p>
              <p className="mt-1 font-bold">{scenario}</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-3">
              <p className="text-slate-500">Nivel</p>
              <p className="mt-1 font-bold">Lv {session.difficulty_level}</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white p-3">
              <p className="text-slate-500">Pressao</p>
              <p className="mt-1 flex items-center gap-1 font-bold">
                <Timer size={12} />
                {pressureLabel}
              </p>
            </div>
          </section>
        )}

        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="mb-3 flex items-center justify-between">
            <p className="text-sm font-bold">Chat principal</p>
            <p className="flex items-center gap-1 text-xs font-bold text-amber-600">
              <Flame size={12} />
              XP {xpSession}
            </p>
          </div>

          <div className="max-h-72 space-y-2 overflow-y-auto rounded-lg bg-slate-50 p-3">
            {chat.length === 0 ? (
              <p className="text-sm text-slate-500">Inicie uma simulacao para conversar com o personagem.</p>
            ) : (
              chat.map((line, idx) => (
                <div
                  key={`${line.role}-${idx}`}
                  className={`rounded-lg px-3 py-2 text-sm ${line.role === 'ai' ? 'bg-white border border-slate-200 text-slate-800' : 'bg-primary text-white ml-6'}`}
                >
                  <p className="mb-1 text-[10px] font-bold uppercase opacity-70">{line.role === 'ai' ? session?.character_role || 'IA' : 'Voce'}</p>
                  <p>{line.text}</p>
                </div>
              ))
            )}
          </div>

          <div className="mt-3 flex gap-2">
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Responda rapido em ingles..."
              className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <button onClick={submitMessage} disabled={loading || status !== 'active'} className="rounded-lg bg-primary px-3 py-2 text-white disabled:opacity-60">
              <Send size={16} />
            </button>
          </div>
        </section>

        {feedback.correction && (
          <section className="rounded-xl border border-slate-200 bg-white p-4 text-sm">
            <p className="font-bold">Feedback da IA</p>
            <p className="mt-2 text-slate-700"><strong>Correcao:</strong> {feedback.correction}</p>
            <p className="mt-1 text-slate-700"><strong>Resposta melhor:</strong> {feedback.better_response}</p>
            <p className="mt-1 text-slate-700"><strong>Pressao:</strong> {feedback.pressure_note}</p>
            <p className="mt-1 text-slate-700"><strong>Ajuste:</strong> {feedback.level_adaptation}</p>
          </section>
        )}

        <section className="grid grid-cols-2 gap-2">
          <button
            onClick={() => start(lastSessionId)}
            disabled={loading || !session}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-bold text-slate-700 disabled:opacity-60"
          >
            <RotateCcw size={16} />
            Tentar novamente
          </button>
          <button
            onClick={() => {
              setSession(null);
              setChat([]);
              setFeedback(emptyFeedback);
              setStatus('idle');
              setMessage('');
            }}
            className="rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white"
          >
            Mudar cenario
          </button>
        </section>
      </main>
    </div>
  );
}
