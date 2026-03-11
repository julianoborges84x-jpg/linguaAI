import React, { useEffect, useState } from "react";
import NavBar from "../../shared/components/NavBar.jsx";
import PageShell from "../../shared/layouts/PageShell.jsx";
import Card from "../../shared/ui/Card.jsx";
import Button from "../../shared/ui/Button.jsx";
import { useAuth } from "../../hooks/useAuth.jsx";
import { subscribePro } from "../../services/billingService.js";
import { getTopics } from "../../services/learnaService.js";

export default function Topics() {
  const { user, logout, isPro } = useAuth();
  const [topics, setTopics] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isPro) return;
    (async () => {
      try {
        setError("");
        const data = await getTopics();
        setTopics(data || []);
      } catch (err) {
        setError(err.message || "Erro ao carregar tópicos");
      }
    })();
  }, [isPro]);

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
      {!isPro && (
        <Card className="mb-4">
          <h3 className="font-display text-2xl">Tópicos premium</h3>
          <p className="text-slate-600 mt-2">Upgrade para PRO para acessar este recurso</p>
          <Button className="mt-4" onClick={handleSubscribe}>Assinar PRO</Button>
        </Card>
      )}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {topics.map((topic) => (
          <Card key={topic.id}>
            <p className="text-xs uppercase tracking-[0.2em] text-lagoon">{topic.category}</p>
            <h3 className="font-display text-2xl mt-2">{topic.name}</h3>
          </Card>
        ))}
      </div>
    </PageShell>
  );
}
