import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ArrowLeft, Bot, BookOpen, MessageSquare, Mic, Send, Settings, User as UserIcon } from 'lucide-react';
import { ChatMessage, AuthUser } from '../types';
import { fetchChatHistory, sendChatMessage } from '../api/auth';

interface Props {
  user: AuthUser;
  onBack: () => void;
}

export default function ChatScreen({ user, onBack }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'model', text: `Ola ${user.name}! Vamos praticar ${user.target_language_code || user.target_language || 'seu idioma alvo'}?` },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastFailedMessage, setLastFailedMessage] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  const classifyError = (message: string) => {
    const lower = message.toLowerCase();
    if (lower.includes('conectar') || lower.includes('network') || lower.includes('llm_service_url')) {
      return `Erro de conexao: ${message}`;
    }
    if (lower.includes('http') || lower.includes('api')) {
      return `Erro de API: ${message}`;
    }
    return `Erro interno: ${message}`;
  };

  useEffect(() => {
    const hydrateHistory = async () => {
      try {
        const history = await fetchChatHistory();
        if (history.length) {
          setMessages((prev) => [
            ...prev,
            ...history.slice(0, 6).map((item) => ({
              role: 'model' as const,
              text: item.preview,
            })),
          ]);
        }
      } catch {
        // keep chat available even if history fails
      }
    };

    hydrateHistory();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (text: string = input) => {
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = { role: 'user', text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError('');

    try {
      const response = await sendChatMessage(text);
      const modelMsg: ChatMessage = {
        role: 'model',
        text: response.message || response.reply || 'Desculpe, nao consegui processar sua mensagem.',
        correction: response.correction,
        explanation: response.explanation,
        suggestion: response.suggestion,
        detected_errors: response.detected_errors || [],
        recommendation: response.recommendation,
        micro_intervention: response.micro_intervention,
        micro_drill_questions: response.micro_drill_questions || [],
        fallback_reason: response.fallback_reason,
      };
      setMessages((prev) => [...prev, modelMsg]);
    } catch (err) {
      const realMessage = err instanceof Error ? err.message : 'Erro ao processar sua mensagem.';
      setError(classifyError(realMessage));
      setLastFailedMessage(text);
      setMessages((prev) => [
        ...prev,
        {
          role: 'model',
          text: 'Nao consegui acessar o motor de IA agora. Podemos continuar com treino guiado no proximo envio.',
          fallback_reason: realMessage,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-background-light min-h-screen flex flex-col">
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-slate-200 px-4 py-3">
        <div className="max-w-md mx-auto flex items-center justify-between gap-4">
          <button type="button" onClick={onBack} aria-label="Voltar ao dashboard" className="p-2 hover:bg-slate-100 rounded-full transition-colors">
            <ArrowLeft size={20} className="text-slate-600" />
          </button>
          <div className="flex-1 flex flex-col items-center">
            <h1 className="text-lg font-bold leading-tight">Mentor IA</h1>
            <div className="flex items-center gap-1.5">
              <span className="size-2 bg-green-500 rounded-full"></span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">/mentor/chat online</span>
            </div>
          </div>
          <button
            type="button"
            disabled
            aria-label="Configuracoes em breve"
            title="Configuracoes em breve"
            className="p-2 rounded-full transition-colors text-slate-400 cursor-not-allowed"
          >
            <Settings size={20} className="text-slate-600" />
          </button>
        </div>
      </header>

      {error && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-2">
          <div className="max-w-md mx-auto flex items-center justify-between gap-3">
            <p className="text-sm text-red-700">{error}</p>
            <button
              type="button"
              onClick={() => lastFailedMessage && handleSend(lastFailedMessage)}
              className="rounded-lg border border-red-200 bg-white px-3 py-1 text-xs font-semibold text-red-700"
            >
              Tentar de novo
            </button>
          </div>
        </div>
      )}

      <main ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-6 max-w-md mx-auto w-full">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex items-start gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'model' && (
                <div className="size-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0 border border-primary/20">
                  <Bot size={20} className="text-primary fill-primary" />
                </div>
              )}

              <div className={`flex flex-col gap-1.5 max-w-[80%] ${msg.role === 'user' ? 'items-end' : ''}`}>
                <p className="text-xs font-semibold text-slate-500 ml-1">{msg.role === 'model' ? 'Mentor IA' : 'Voce'}</p>
                <div className={`p-4 rounded-lg shadow-sm border ${msg.role === 'user' ? 'bg-primary text-white border-primary rounded-tr-none' : 'bg-white border-slate-100 rounded-tl-none'}`}>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                  {msg.role === 'model' && msg.correction ? (
                    <p className="mt-2 text-xs text-emerald-700"><strong>✔ Correcao:</strong> {msg.correction}</p>
                  ) : null}
                  {msg.role === 'model' && msg.explanation ? (
                    <p className="mt-1 text-xs text-slate-600"><strong>💡 Explicacao:</strong> {msg.explanation}</p>
                  ) : null}
                  {msg.role === 'model' && msg.suggestion ? (
                    <p className="mt-1 text-xs text-indigo-700"><strong>👉 Sugestao:</strong> {msg.suggestion}</p>
                  ) : null}
                  {msg.role === 'model' && msg.detected_errors && msg.detected_errors.length > 0 ? (
                    <p className="mt-1 text-xs text-rose-700"><strong>Erros detectados:</strong> {msg.detected_errors.join(', ')}</p>
                  ) : null}
                  {msg.role === 'model' && msg.recommendation ? (
                    <p className="mt-1 text-xs text-amber-700"><strong>Proximo passo:</strong> {msg.recommendation}</p>
                  ) : null}
                  {msg.role === 'model' && msg.micro_intervention ? (
                    <div className="mt-2 rounded-md border border-sky-200 bg-sky-50 p-2 text-xs text-sky-800">
                      <p><strong>Micro learning:</strong> {msg.micro_intervention}</p>
                      {msg.micro_drill_questions && msg.micro_drill_questions.length > 0 ? (
                        <ul className="mt-1 list-disc pl-4">
                          {msg.micro_drill_questions.slice(0, 3).map((q, idx) => (
                            <li key={`${idx}-${q}`}>{q}</li>
                          ))}
                        </ul>
                      ) : null}
                    </div>
                  ) : null}
                  {msg.role === 'model' && msg.fallback_reason ? (
                    <p className="mt-1 text-[11px] text-slate-500"><strong>Motivo tecnico:</strong> {msg.fallback_reason}</p>
                  ) : null}
                </div>
              </div>

              {msg.role === 'user' && (
                <div className="size-10 rounded-full bg-slate-200 flex items-center justify-center shrink-0">
                  <UserIcon size={18} className="text-slate-600" />
                </div>
              )}
            </motion.div>
          ))}

          {loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-start gap-3">
              <div className="size-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0 border border-primary/20">
                <Bot size={20} className="text-primary animate-pulse" />
              </div>
              <div className="bg-white border border-slate-100 p-4 rounded-lg rounded-tl-none shadow-sm">
                <div className="flex gap-1">
                  <span className="size-1.5 bg-slate-400 rounded-full animate-bounce"></span>
                  <span className="size-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                  <span className="size-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="bg-white border-t border-slate-200 p-4 pb-8">
        <div className="max-w-md mx-auto space-y-4">
          <div className="flex items-center gap-2">
            <div className="flex-1 relative">
              <input
                className="w-full bg-slate-100 border-none rounded-full py-3 px-5 pr-12 text-sm focus:ring-2 focus:ring-primary placeholder:text-slate-500"
                placeholder="Digite sua mensagem..."
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              />
              <button type="button" aria-label="Enviar mensagem" onClick={() => handleSend()} className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-primary">
                <Send size={20} />
              </button>
            </div>
            <button type="button" aria-label="Microfone em breve" disabled className="bg-primary text-white p-4 rounded-lg rounded-tr-none shadow-lg shadow-primary/20 opacity-60 cursor-not-allowed">
              <Mic size={24} className="fill-white" />
            </button>
          </div>
          <nav className="flex justify-between items-center px-2 pt-2">
            <button type="button" aria-label="Tela atual chat" disabled className="flex flex-col items-center gap-1 text-primary cursor-default">
              <MessageSquare size={24} className="fill-primary" />
              <span className="text-[10px] font-bold">Chat</span>
            </button>
            <button type="button" onClick={onBack} className="flex flex-col items-center gap-1 text-slate-400">
              <BookOpen size={24} />
              <span className="text-[10px] font-bold">Dashboard</span>
            </button>
          </nav>
        </div>
      </footer>
    </div>
  );
}
