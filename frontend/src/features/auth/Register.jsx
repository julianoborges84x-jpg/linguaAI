import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../../services/authService.js";
import Button from "../../shared/ui/Button.jsx";
import Input from "../../shared/ui/Input.jsx";
import Card from "../../shared/ui/Card.jsx";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      navigate("/login");
    } catch (err) {
      setError(err.message || "Falha ao cadastrar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="hidden lg:flex flex-col justify-between bg-moss text-white p-12">
        <div>
          <h1 className="font-display text-4xl">Novo começo</h1>
          <p className="text-white/70 mt-4">
            Acompanhe seu progresso e desbloqueie novos modos de aprendizado.
          </p>
        </div>
        <div className="text-sm text-white/60">MentorLingua 24/7</div>
      </div>
      <div className="flex items-center justify-center p-8">
        <Card className="w-full max-w-md">
          <h2 className="font-display text-3xl">Criar conta</h2>
          <p className="text-slate-600 mt-2">Leva menos de um minuto.</p>

          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <Input
              label="Nome"
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
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
              {loading ? "Criando..." : "Criar conta"}
            </Button>
          </form>

          <p className="text-sm text-slate-600 mt-6">
            Já tem conta? <Link to="/login" className="text-ink font-medium">Entrar</Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
