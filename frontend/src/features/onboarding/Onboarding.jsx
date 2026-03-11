import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../../shared/ui/Card.jsx";
import Button from "../../shared/ui/Button.jsx";
import { completeOnboarding, getCurrentUser } from "../../services/userService.js";
import { useAuth } from "../../hooks/useAuth.jsx";

const LANGUAGE_OPTIONS = [
  { label: "Inglês", value: "en" },
  { label: "Espanhol", value: "es" },
  { label: "Francês", value: "fr" },
  { label: "Italiano", value: "it" },
];

const COMMON_TIMEZONES = [
  "America/Sao_Paulo",
  "America/New_York",
  "Europe/Lisbon",
  "Europe/Madrid",
  "Europe/Paris",
];

export default function Onboarding() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const browserTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "America/Sao_Paulo";
  const [step, setStep] = useState(1);
  const [targetLanguage, setTargetLanguage] = useState("");
  const [timezone, setTimezone] = useState(browserTimezone);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const timezoneOptions = useMemo(() => {
    const combined = [browserTimezone, ...COMMON_TIMEZONES];
    return [...new Set(combined)];
  }, [browserTimezone]);

  const handleFinish = async () => {
    if (!targetLanguage || !timezone.trim()) {
      setError("Não foi possível salvar. Tente novamente.");
      return;
    }
    try {
      setError("");
      setLoading(true);
      await completeOnboarding({
        target_language: targetLanguage,
        timezone: timezone.trim(),
      });
      const updated = await getCurrentUser();
      setUser(updated);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError("Não foi possível salvar. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 p-6 md:p-10">
      <div className="mx-auto max-w-2xl">
        <Card>
          <h1 className="font-display text-4xl">Primeira configuração</h1>
          <p className="mt-2 text-slate-600">Só 2 passos e você começa.</p>

          {step === 1 ? (
            <div className="mt-8">
              <h2 className="font-display text-2xl">Qual idioma você quer aprender?</h2>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {LANGUAGE_OPTIONS.map((option) => (
                  <Button
                    key={option.value}
                    variant={targetLanguage === option.value ? "primary" : "secondary"}
                    onClick={() => setTargetLanguage(option.value)}
                  >
                    {option.label}
                  </Button>
                ))}
              </div>
              <Button
                className="mt-6"
                onClick={() => setStep(2)}
                disabled={!targetLanguage}
              >
                Continuar
              </Button>
            </div>
          ) : (
            <div className="mt-8">
              <h2 className="font-display text-2xl">Seu fuso horário</h2>
              <select
                className="mt-4 w-full rounded-lg border border-slate-300 bg-white p-3"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                disabled={loading}
              >
                {timezoneOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>

              {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}

              <div className="mt-6 flex gap-3">
                <Button variant="secondary" onClick={() => setStep(1)} disabled={loading}>
                  Voltar
                </Button>
                <Button onClick={handleFinish} disabled={loading}>
                  {loading ? "Salvando..." : "Começar"}
                </Button>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
