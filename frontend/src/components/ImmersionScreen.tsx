import { ArrowLeft, Globe, Mic2, Rocket, ShieldCheck, Swords } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import {
  claimImmersionMission,
  fetchImmersionDashboard,
  fetchImmersionMissions,
  fetchImmersionScenarios,
  fetchScenarioCharacters,
  finishImmersionSession,
  sendImmersionTurn,
  startImmersionSession,
} from '../api/auth';
import { ImmersionDashboardData, ImmersionFinishResponse, ImmersionMission, ImmersionScenario, RoleplayCharacter } from '../types';

interface Props {
  onBack: () => void;
}

export default function ImmersionScreen({ onBack }: Props) {
  const [scenarios, setScenarios] = useState<ImmersionScenario[]>([]);
  const [missions, setMissions] = useState<ImmersionMission[]>([]);
  const [dashboard, setDashboard] = useState<ImmersionDashboardData | null>(null);
  const [characters, setCharacters] = useState<RoleplayCharacter[]>([]);
  const [activeScenario, setActiveScenario] = useState<string>('');
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [conversationLog, setConversationLog] = useState<string[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [hints, setHints] = useState<string[]>([]);
  const [lastResult, setLastResult] = useState<ImmersionFinishResponse | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        setLoading(true);
        const [scenarioRows, missionRows, dashboardRows] = await Promise.all([
          fetchImmersionScenarios(),
          fetchImmersionMissions(),
          fetchImmersionDashboard(),
        ]);
        setScenarios(scenarioRows);
        setMissions(missionRows);
        setDashboard(dashboardRows);
        if (scenarioRows.length > 0) {
          setActiveScenario(scenarioRows[0].slug);
          const cast = await fetchScenarioCharacters(scenarioRows[0].slug);
          setCharacters(cast);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Nao foi possivel carregar o modulo de imersao.');
      } finally {
        setLoading(false);
      }
    };

    bootstrap();
  }, []);

  const activeCharacter = useMemo(() => (characters.length > 0 ? characters[0] : null), [characters]);

  const handleScenarioChange = async (slug: string) => {
    setActiveScenario(slug);
    setActiveSessionId(null);
    setConversationLog([]);
    setHints([]);
    setLastResult(null);
    try {
      const cast = await fetchScenarioCharacters(slug);
      setCharacters(cast);
    } catch {
      setCharacters([]);
    }
  };

  const handleStartSession = async () => {
    if (!activeScenario) return;
    setSubmitting(true);
    setError('');
    try {
      const started = await startImmersionSession(activeScenario, activeCharacter?.id);
      setActiveSessionId(started.session_id);
      setConversationLog([`AI: ${started.opening_message}`]);
      setHints([]);
      setLastResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao iniciar roleplay.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSend = async () => {
    if (!activeSessionId || !inputMessage.trim()) return;
    setSubmitting(true);
    setError('');
    try {
      const sent = await sendImmersionTurn(activeSessionId, inputMessage.trim());
      setConversationLog((prev) => [...prev, `Voce: ${inputMessage.trim()}`, `AI: ${sent.ai_reply}`]);
      setHints(sent.hints);
      setInputMessage('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao enviar mensagem.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleFinish = async () => {
    if (!activeSessionId) return;
    setSubmitting(true);
    setError('');
    try {
      const result = await finishImmersionSession(activeSessionId);
      setLastResult(result);
      setActiveSessionId(null);
      const missionToClaim = missions.find((mission) => mission.status !== 'completed' && mission.scenario_slug === activeScenario);
      if (missionToClaim) {
        await claimImmersionMission(missionToClaim.id);
        setMissions(await fetchImmersionMissions());
      }
      setDashboard(await fetchImmersionDashboard());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao finalizar sessao.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background-light px-4 py-6">
        <div className="max-w-md mx-auto rounded-xl bg-white border border-slate-200 p-5 text-sm text-slate-500">
          Carregando Immersion Engine...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background-light pb-24">
      <header className="sticky top-0 z-40 bg-background-light/85 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-md mx-auto h-16 px-4 flex items-center justify-between">
          <button onClick={onBack} className="size-10 rounded-full bg-white border border-slate-200 flex items-center justify-center">
            <ArrowLeft size={18} />
          </button>
          <p className="text-sm font-black tracking-wide">IMMERSION ENGINE</p>
          <div className="size-10 rounded-full bg-emerald-100 flex items-center justify-center">
            <Mic2 size={18} className="text-emerald-600" />
          </div>
        </div>
      </header>

      <main className="max-w-md mx-auto p-4 space-y-4">
        {error && <div className="rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

        <section className="rounded-2xl bg-slate-900 text-white p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">Fluency RPG</p>
          <div className="mt-2 flex items-end justify-between">
            <div>
              <h1 className="text-xl font-black">{dashboard?.fluency_level || 'Turista'}</h1>
              <p className="text-xs text-slate-300">Score atual: {dashboard?.latest_fluency_score || 0}</p>
            </div>
            <Rocket className="text-amber-300" />
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2">
            <div className="rounded-lg bg-white/10 p-2">
              <p className="text-[11px] text-slate-300">Confianca</p>
              <p className="font-bold">{dashboard?.tutor_insights.confidence_score || 0}</p>
            </div>
            <div className="rounded-lg bg-white/10 p-2">
              <p className="text-[11px] text-slate-300">Velocidade</p>
              <p className="font-bold">{dashboard?.tutor_insights.avg_speaking_speed_wpm || 0} wpm</p>
            </div>
          </div>
        </section>

        <section className="rounded-xl bg-white border border-slate-200 p-4">
          <div className="flex items-center gap-2 mb-3">
            <Globe size={16} className="text-blue-600" />
            <h2 className="font-bold">Cenarios da vida real</h2>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {scenarios.slice(0, 6).map((scenario) => (
              <button
                key={scenario.id}
                onClick={() => handleScenarioChange(scenario.slug)}
                className={`text-left rounded-lg px-3 py-2 border ${activeScenario === scenario.slug ? 'border-blue-500 bg-blue-50' : 'border-slate-200 bg-slate-50'}`}
              >
                <p className="text-xs font-bold">{scenario.title}</p>
                <p className="text-[10px] text-slate-500">{scenario.difficulty}</p>
              </button>
            ))}
          </div>
          <div className="mt-3 rounded-lg bg-slate-50 border border-slate-200 px-3 py-2">
            <p className="text-xs font-semibold">Personagem IA</p>
            <p className="text-sm">{activeCharacter ? `${activeCharacter.name} • ${activeCharacter.accent}` : 'Sem personagem cadastrado'}</p>
          </div>
          <button
            onClick={handleStartSession}
            disabled={submitting || !activeScenario}
            className="mt-3 w-full rounded-lg bg-blue-600 text-white px-4 py-2.5 font-bold disabled:opacity-60"
          >
            {activeSessionId ? 'Sessao em andamento' : 'Iniciar roleplay'}
          </button>
        </section>

        <section className="rounded-xl bg-white border border-slate-200 p-4">
          <div className="flex items-center gap-2 mb-2">
            <Swords size={16} className="text-purple-600" />
            <h2 className="font-bold">Conversacao ativa</h2>
          </div>
          <div className="max-h-48 overflow-y-auto rounded-lg bg-slate-50 p-3 text-sm space-y-2">
            {conversationLog.length === 0 ? (
              <p className="text-slate-500">Inicie uma sessao para conversar com a IA.</p>
            ) : (
              conversationLog.map((line, idx) => (
                <p key={`${line}-${idx}`} className="text-slate-700">{line}</p>
              ))
            )}
          </div>
          <div className="mt-3 flex gap-2">
            <input
              value={inputMessage}
              onChange={(event) => setInputMessage(event.target.value)}
              placeholder="Digite sua resposta em ingles..."
              className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            <button onClick={handleSend} disabled={submitting || !activeSessionId} className="rounded-lg bg-slate-900 text-white px-3 py-2 text-sm font-bold disabled:opacity-60">
              Enviar
            </button>
          </div>
          <button onClick={handleFinish} disabled={submitting || !activeSessionId} className="mt-2 w-full rounded-lg border border-emerald-300 bg-emerald-50 text-emerald-700 px-3 py-2 text-sm font-bold disabled:opacity-60">
            Finalizar e analisar fluencia
          </button>
          {hints.length > 0 && (
            <div className="mt-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2">
              <p className="text-xs font-semibold text-amber-700">Dicas</p>
              <p className="text-xs text-amber-700">{hints.join(' | ')}</p>
            </div>
          )}
        </section>

        {lastResult && (
          <section className="rounded-xl bg-white border border-slate-200 p-4 space-y-2">
            <div className="flex items-center gap-2">
              <ShieldCheck size={16} className="text-emerald-600" />
              <h2 className="font-bold">Analise de fluencia</h2>
            </div>
            <p className="text-sm">Nivel: <span className="font-black">{lastResult.fluency_level}</span> • Score: <span className="font-black">{lastResult.fluency_score}</span></p>
            <p className="text-xs text-slate-600">
              Speed {lastResult.speaking_speed_wpm} wpm | Fillers {lastResult.filler_words_count} | Grammar {lastResult.grammar_mistakes} | Pronunciation {lastResult.pronunciation_score}
            </p>
            <p className="text-xs text-slate-600">Foco recomendado: {lastResult.recommended_focus.join(', ')}</p>
          </section>
        )}

        <section className="rounded-xl bg-white border border-slate-200 p-4">
          <h2 className="font-bold mb-2">Missoes reais</h2>
          <div className="space-y-2">
            {missions.map((mission) => (
              <div key={mission.id} className="rounded-lg border border-slate-200 px-3 py-2">
                <p className="text-sm font-semibold">{mission.title}</p>
                <p className="text-xs text-slate-600">{mission.description}</p>
                <p className="text-xs text-slate-500 mt-1">XP {mission.xp_reward} • {mission.status}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
