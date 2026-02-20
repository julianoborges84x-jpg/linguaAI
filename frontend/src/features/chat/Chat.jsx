import React, { useState } from "react";
import PageShell from "../../shared/layouts/PageShell.jsx";
import NavBar from "../../shared/components/NavBar.jsx";
import AdsPanel from "../../shared/components/AdsPanel.jsx";
import Button from "../../shared/ui/Button.jsx";
import { useAuth } from "../../hooks/useAuth.js";
import { chatMentor, detectBaseLanguage } from "../../services/mentorService.js";

export default function Chat() {
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [feature, setFeature] = useState("writing");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const sendMessage = async () => {
    if (!input.trim() || !user) return;
    const payload = input;
    setMessages((prev) => [...prev, { role: "user", content: payload }]);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const response = await chatMentor(payload, feature);
      setMessages((prev) => [...prev, { role: "assistant", content: response.reply }]);
      if (response.ads?.length) {
        setMessages((prev) => [
          ...prev,
          { role: "ads", content: response.ads.join(" ") }
        ]);
      }
    } catch (err) {
      setError(err.message || "Erro ao enviar");
    } finally {
      setLoading(false);
    }
  };

  const handleDetect = async () => {
    if (!input.trim()) return;
    try {
      await detectBaseLanguage(input);
    } catch (err) {
      setError(err.message || "Falha ao detectar idioma");
    }
  };

  if (!user) return null;

  return (
    <PageShell>
      <NavBar user={user} onLogout={logout} />
      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <section className="glass-card rounded-2xl p-6 shadow-soft flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-2xl">MentorLingua ao vivo</h2>
            <select
              value={feature}
              onChange={(e) => setFeature(e.target.value)}
              className="rounded-full border border-slate-200 px-3 py-2 text-sm"
            >
              <option value="writing">Escrita</option>
              <option value="speaking">Conversação</option>
              <option value="dialect">Dialeto</option>
              <option value="fillers">Vícios de linguagem</option>
            </select>
          </div>

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
            />
            <div className="flex flex-wrap gap-3">
              <Button onClick={sendMessage} disabled={loading}>
                {loading ? "Enviando..." : "Enviar"}
              </Button>
              <Button variant="secondary" onClick={handleDetect}>
                Detectar idioma base
              </Button>
            </div>
          </div>
        </section>

        <div className="space-y-6">
          <section className="glass-card rounded-2xl p-6 shadow-soft">
            <h3 className="font-display text-xl">Seu plano</h3>
            <p className="text-slate-600 mt-2">
              {user.plan === "FREE"
                ? "Você está no plano FREE. Conversação e dialeto exigem PRO."
                : "Plano PRO ativo. Aproveite sem anúncios."}
            </p>
          </section>

          <AdsPanel visible={user.plan === "FREE"} placement="chat" />
        </div>
      </div>
    </PageShell>
  );
}
