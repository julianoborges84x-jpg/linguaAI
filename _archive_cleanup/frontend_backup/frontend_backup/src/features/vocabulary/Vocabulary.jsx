import React, { useEffect, useState } from "react";
import NavBar from "../../shared/components/NavBar.jsx";
import PageShell from "../../shared/layouts/PageShell.jsx";
import Card from "../../shared/ui/Card.jsx";
import { getVocabulary } from "../../services/learnaService.js";
import { useAuth } from "../../hooks/useAuth.jsx";

export default function Vocabulary() {
  const { user, logout } = useAuth();
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await getVocabulary();
        setItems(data || []);
      } catch (err) {
        setError(err.message || "Erro ao carregar vocabulário");
      }
    })();
  }, []);

  if (!user) return null;

  return (
    <PageShell>
      <NavBar user={user} onLogout={logout} />
      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
      <div className="grid gap-4 md:grid-cols-2">
        {items.map((item) => (
          <Card key={item.id}>
            <h3 className="font-display text-2xl">{item.word}</h3>
            <p className="text-slate-700 mt-2">{item.definition}</p>
            <p className="text-slate-500 mt-2 italic">{item.example}</p>
          </Card>
        ))}
      </div>
    </PageShell>
  );
}
