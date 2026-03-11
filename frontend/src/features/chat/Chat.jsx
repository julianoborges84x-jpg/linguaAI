import React, { useEffect, useRef, useState } from "react";
import PageShell from "../../shared/layouts/PageShell.jsx";
import NavBar from "../../shared/components/NavBar.jsx";
import AdsPanel from "../../shared/components/AdsPanel.jsx";
import Button from "../../shared/ui/Button.jsx";
import { useAuth } from "../../hooks/useAuth.jsx";
import { subscribePro } from "../../services/billingService.js";
import { finishStudySession, sendChatMessage, startStudySession } from "../../services/learnaService.js";

export default function Chat() {

  const { user, logout, isPro } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const sessionIdRef = useRef(null);
  const interactionsRef = useRef(0);

  useEffect(() => {
    if (!user || !isPro) return undefined;
    let isMounted = true;

    (async () => {
      try {
        const started = await startStudySession("chat");
        if (isMounted) {
          sessionIdRef.current = started?.session_id || null;
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || "Erro ao iniciar sessão");
        }
      }
    })();

    return () => {
      isMounted = false;
      if (sessionIdRef.current) {
        finishStudySession(sessionIdRef.current, interactionsRef.current).catch(() => {});
      }
    };
  }, [user, isPro]);

  const sendMessage = async () => {
    if (!input.trim() || !user) return;
    const payload = input;
    setMessages((prev) => [...prev, { role: "user", content: payload }]);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const response = await sendChatMessage(payload);
      interactionsRef.current += 1;
      const content = `${response.correction}\n\n${response.explanation}\n\nVersão correta: ${response.corrected_text}`;
      setMessages((prev) => [...prev, { role: "assistant", content }]);
    } catch (err) {
      setError(err.message || "Erro ao enviar");
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  const handleSubscribe = async () => {
    try {
      const data = await subscribePro();
      if (data?.checkout_url) {
        window.location.assign(data.checkout_url);
      } else {
        throw new Error("Checkout indisponível no momento.");
      }
    } catch (err) {
      setError(err.message || "Não foi possível iniciar assinatura PRO");
    }
  };

  return (
    <PageShell>
      <NavBar user={user} onLogout={logout} />
      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="glass-card rounded-2xl p-6 shadow-soft flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-2xl">IA de Correção em tempo real</h2>
          </div>
          {!isPro && (
            <div className="rounded-xl border border-amber-300 bg-amber-50 p-4 text-amber-900">
              <p className="font-medium">Recurso PRO</p>
              <p className="mt-1 text-sm">Upgrade para PRO para acessar este recurso</p>
              <Button className="mt-3" onClick={handleSubscribe}>Assinar PRO</Button>
            </div>
          )}

          <div className="flex-1 overflow-y-auto space-y-4 max-h-[50vh]">
            {messages.length === 0 && (
              <p className="text-slate-500">
                Envie uma mensagem para iniciar sua sessão personalizada.
              </p>
            )}
            {messages.map((msg, idx) => (
              <div
                key={`${msg.role}-${idx}`}
                className={
                  msg.role === "user"
                    ? "bg-ink text-white p-3 rounded-2xl ml-auto max-w-[80%]"
                    : msg.role === "ads"
                    ? "bg-amber-50 text-amber-800 p-3 rounded-2xl"
                    : "bg-white p-3 rounded-2xl shadow"
                }
              >
                {msg.content}
              </div>
            ))}
          </div>

          <div className="grid gap-3">
            <textarea
              className="w-full rounded-2xl border border-slate-200 p-3 min-h-[90px]"
              placeholder="Escreva aqui..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={!isPro}
            />
            <div className="flex flex-wrap gap-3">
              <Button onClick={sendMessage} disabled={loading || !isPro}>
                {loading ? "Enviando..." : "Enviar"}
              </Button>
            </div>
          </div>
        </section>

        <div className="space-y-6">
          <section className="glass-card rounded-2xl p-6 shadow-soft">
            <h3 className="font-display text-xl">Seu plano</h3>
            <p className="text-slate-600 mt-2">
              Receba correção, explicação e versão correta para evoluir diariamente.
            </p>
          </section>

          <AdsPanel visible={user.plan === "FREE"} placement="chat" />
        </div>
      </div>
    </PageShell>
  );
}
