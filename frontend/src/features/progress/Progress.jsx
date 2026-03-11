import React, { useEffect, useState } from "react";
import NavBar from "../../shared/components/NavBar.jsx";
import PageShell from "../../shared/layouts/PageShell.jsx";
import Card from "../../shared/ui/Card.jsx";
import Button from "../../shared/ui/Button.jsx";
import { useAuth } from "../../hooks/useAuth.jsx";
import { getProgress, updateProgress } from "../../services/learnaService.js";

export default function Progress() {
  const { user, logout } = useAuth();
  const [data, setData] = useState({ streak: 0, hours_spoken: 0, words_learned: 0 });
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const current = await getProgress();
        setData(current);
      } catch (err) {
        setError(err.message || "Erro ao carregar progresso");
      }
    })();
  }, []);

  const addPracticeHour = async () => {
    try {
      const updated = await updateProgress({
        hours_spoken: Number(data.hours_spoken || 0) + 1,
        streak: Number(data.streak || 0) + 1,
      });
      setData(updated);
    } catch (err) {
      setError(err.message || "Erro ao atualizar progresso");
    }
  };

  if (!user) return null;

  return (
    <PageShell>
      <NavBar user={user} onLogout={logout} />
      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
      <div className="grid gap-4 md:grid-cols-3">
        <Card><p className="text-xs uppercase tracking-[0.2em] text-lagoon">Streak</p><h3 className="font-display text-4xl">{data.streak}</h3></Card>
        <Card><p className="text-xs uppercase tracking-[0.2em] text-lagoon">Hours Spoken</p><h3 className="font-display text-4xl">{data.hours_spoken}</h3></Card>
        <Card><p className="text-xs uppercase tracking-[0.2em] text-lagoon">Words Learned</p><h3 className="font-display text-4xl">{data.words_learned}</h3></Card>
      </div>
      <div className="mt-6">
        <Button onClick={addPracticeHour}>Registrar 1h de prática</Button>
      </div>
    </PageShell>
  );
}
