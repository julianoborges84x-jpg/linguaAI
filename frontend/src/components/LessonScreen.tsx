
import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { ArrowRight, Bolt, GraduationCap, Trophy, User, Volume2, X } from 'lucide-react';
import { finishLessonSession, startLessonSession } from '../api/auth';

interface Props {
  onFinish: () => void;
}

const options = [
  { id: 'sobre-a', text: 'sobre a' },
  { id: 'o-gato', text: 'o gato', disabled: true },
  { id: 'embaixo-da', text: 'embaixo da' },
  { id: 'esta', text: 'esta', disabled: true },
  { id: 'dentro-da', text: 'dentro da' },
  { id: 'mesa', text: 'mesa', disabled: true },
];

export default function LessonScreen({ onFinish }: Props) {
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [interactionsCount, setInteractionsCount] = useState(0);
  const [error, setError] = useState('');
  const [completing, setCompleting] = useState(false);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        const payload = await startLessonSession();
        setSessionId(payload.session_id);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Nao foi possivel iniciar a sessao.');
      }
    };

    bootstrap();
  }, []);

  const handleVerify = async () => {
    setInteractionsCount((prev) => prev + 1);

    if (selectedWord !== 'sobre-a') {
      setError('Resposta incorreta. Tente novamente.');
      return;
    }

    setError('');
    setShowFeedback(true);
  };

  const handleContinue = async () => {
    setCompleting(true);
    try {
      if (sessionId) {
        await finishLessonSession(sessionId, interactionsCount || 1);
      }
      onFinish();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nao foi possivel concluir a licao.');
    } finally {
      setCompleting(false);
    }
  };

  return (
    <div className="bg-background-light min-h-screen flex flex-col">
      <header className="bg-white border-b border-primary/10 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto flex items-center gap-4">
          <button onClick={onFinish} className="text-slate-500 hover:text-primary transition-colors">
            <X size={24} />
          </button>
          <div className="flex-1 flex flex-col gap-2">
            <div className="flex justify-between items-center text-xs font-bold uppercase tracking-wider text-slate-500">
              <span>Licao real</span>
              <span className="text-primary flex items-center gap-1">
                <Bolt size={14} className="fill-primary" />
                Sessao {sessionId ? `#${sessionId}` : '...'}
              </span>
            </div>
            <div className="h-3 w-full bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full w-[65%] transition-all duration-500"></div>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 flex flex-col max-w-2xl mx-auto w-full p-4 md:p-8">
        {error && <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-6 text-center md:text-left">Como se diz "The cat is on the table" em Portugues?</h2>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-primary/5 flex flex-col md:flex-row gap-6 items-center">
            <div className="w-full md:w-48 aspect-square rounded-lg bg-cover bg-center border-4 border-primary/10 overflow-hidden">
              <img
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuBMDJh6Oe_v7iCAQ8H0ujeHW_vK6chx2qUOOVao6oKuwiL4UyP-UflWq53KHdnRwwD2Dp4V8_jjD0xP56raCk1ten0lBpjpLExzbtsv6iFhpAT08TZhRWemu6yPPwEf5jD-IIvyW195E1ThsN3ySg9sDOOYW0fTLnp83jMPutlQVyMuNejg1xuBa4R21MZveg-DOdLFGjpSy3LM-m7WUrQSNIYWO0vuSnBuBaNd6PSe1D9VpsX6wf1n_OKppmMAY0hxqQnxuVTQPuEr"
                alt="Cat on table"
                className="w-full h-full object-cover"
                referrerPolicy="no-referrer"
              />
            </div>
            <div className="flex-1 space-y-4 text-center md:text-left">
              <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-semibold">
                <Volume2 size={16} />
                Ingles
              </div>
              <p className="text-xl font-medium italic text-slate-600">"The cat is on the table."</p>
            </div>
          </div>
        </div>

        <div className="flex-1 space-y-8">
          <div className="min-h-[120px] p-4 rounded-xl border-2 border-dashed border-slate-300 flex flex-wrap gap-2 items-center justify-center bg-slate-50/50">
            <div className="bg-white border-2 border-primary px-4 py-2 rounded-lg shadow-sm font-medium">O gato</div>
            <div className="bg-white border-2 border-primary px-4 py-2 rounded-lg shadow-sm font-medium">esta</div>
            {selectedWord ? (
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                onClick={() => setSelectedWord(null)}
                className="bg-white border-2 border-primary px-4 py-2 rounded-lg shadow-sm font-medium cursor-pointer"
              >
                {options.find((o) => o.id === selectedWord)?.text}
              </motion.div>
            ) : (
              <div className="h-10 w-24 border-b-2 border-slate-300"></div>
            )}
            <div className="bg-white border-2 border-primary px-4 py-2 rounded-lg shadow-sm font-medium">mesa.</div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {options.map((opt) => (
              <button
                key={opt.id}
                disabled={opt.disabled || selectedWord === opt.id}
                onClick={() => setSelectedWord(opt.id)}
                className={`bg-white border-2 p-4 rounded-xl font-medium transition-all active:scale-95 shadow-sm ${
                  opt.disabled || selectedWord === opt.id ? 'opacity-40 cursor-not-allowed border-slate-200' : 'border-slate-200 hover:border-primary hover:bg-primary/5'
                }`}
              >
                {opt.text}
              </button>
            ))}
          </div>
        </div>
      </main>

      <footer className="bg-white border-t border-primary/10 p-6">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <p className="text-sm text-slate-500 hidden md:block">Interacoes registradas: {interactionsCount}</p>
          <button
            onClick={handleVerify}
            className="w-full md:w-48 bg-primary hover:bg-primary/90 text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/20 transition-all active:transform active:scale-95 flex items-center justify-center gap-2"
          >
            Verificar
            <ArrowRight size={20} />
          </button>
        </div>
      </footer>

      <nav className="bg-white border-t border-slate-100 px-4 pb-3 pt-2 md:hidden">
        <div className="flex gap-2 max-w-md mx-auto">
          <div className="flex flex-1 flex-col items-center justify-center gap-1 text-primary">
            <GraduationCap size={24} className="fill-primary" />
            <p className="text-[10px] font-bold uppercase">Aprender</p>
          </div>
          <div className="flex flex-1 flex-col items-center justify-center gap-1 text-slate-400">
            <Trophy size={24} />
            <p className="text-[10px] font-bold uppercase">Ranking</p>
          </div>
          <div className="flex flex-1 flex-col items-center justify-center gap-1 text-slate-400">
            <User size={24} />
            <p className="text-[10px] font-bold uppercase">Perfil</p>
          </div>
        </div>
      </nav>

      {showFeedback && (
        <div className="fixed bottom-0 left-0 w-full bg-green-100 border-t-4 border-green-500 p-6 z-50">
          <div className="max-w-2xl mx-auto flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="bg-green-500 text-white rounded-full p-2 flex items-center justify-center">
                <ArrowRight size={24} />
              </div>
              <div>
                <h4 className="text-green-800 font-bold text-lg leading-none">Excelente!</h4>
                <p className="text-green-700 text-sm mt-1">Sua sessao vai ser concluida com XP real.</p>
              </div>
            </div>
            <button onClick={handleContinue} disabled={completing} className="bg-green-500 hover:bg-green-600 text-white font-bold px-8 py-3 rounded-xl transition-all disabled:opacity-50">
              {completing ? 'Salvando...' : 'Continuar'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
