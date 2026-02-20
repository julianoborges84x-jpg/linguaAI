import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../../services/authService.js";
import Button from "../../shared/ui/Button.jsx";
import Input from "../../shared/ui/Input.jsx";
import Card from "../../shared/ui/Card.jsx";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(form.email, form.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Falha ao entrar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="hidden lg:flex flex-col justify-between bg-ink text-white p-12">
        <div>
          <h1 className="font-display text-4xl">MentorLingua</h1>
          <p className="text-white/70 mt-4">
            Seu mentor diário para falar, escrever e entender culturas com confiança.
          </p>
        </div>
        <div className="text-sm text-white/60">Conectado ao seu progresso real.</div>
      </div>
      <div className="flex items-center justify-center p-8">
        <Card className="w-full max-w-md">
          <h2 className="font-display text-3xl">Entrar</h2>
          <p className="text-slate-600 mt-2">Acesse sua jornada personalizada.</p>

          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <Input
              label="Email"
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
            <Input
              label="Senha"
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Entrando..." : "Entrar"}
            </Button>
          </form>

          <p className="text-sm text-slate-600 mt-6">
            Ainda não tem conta? <Link to="/register" className="text-ink font-medium">Criar conta</Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
