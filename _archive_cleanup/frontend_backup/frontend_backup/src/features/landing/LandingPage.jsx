import React from "react";
import { Link } from "react-router-dom";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-cyan-50 to-slate-100 text-ink">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <h1 className="font-display text-2xl">LinguaAI</h1>
        <nav className="flex items-center gap-4 text-sm">
          <Link to="/termos" className="text-slate-600 hover:text-ink">Termos</Link>
          <Link to="/privacidade" className="text-slate-600 hover:text-ink">Privacidade</Link>
          <Link to="/login" className="rounded-full bg-ink px-4 py-2 text-white">Entrar</Link>
        </nav>
      </header>

      <main className="mx-auto max-w-6xl space-y-20 px-6 pb-16 pt-4">
        <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-lagoon">SaaS de idiomas</p>
            <h2 className="mt-4 font-display text-5xl leading-tight">
              Fale com confianca em outro idioma todos os dias.
            </h2>
            <p className="mt-5 max-w-xl text-lg text-slate-700">
              Pratica guiada por IA, progresso real e trilhas de estudo para sair do basico e evoluir com consistencia.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/register" className="rounded-xl bg-lagoon px-5 py-3 font-medium text-white">Comecar gratis</Link>
              <a href="#precos" className="rounded-xl border border-slate-300 px-5 py-3 font-medium text-slate-700">Ver planos</a>
            </div>
          </div>
          <div className="rounded-3xl border border-cyan-100 bg-white/80 p-6 shadow-soft">
            <p className="text-sm text-slate-500">Como funciona</p>
            <ul className="mt-4 space-y-3 text-sm text-slate-700">
              <li>1. Defina idioma e rotina no onboarding.</li>
              <li>2. Receba atividades diarias e feedback de escrita.</li>
              <li>3. Acompanhe streak, XP e evolucao semanal.</li>
            </ul>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          {[
            ["Feedback instantaneo", "Correcao de texto com explicacao objetiva."],
            ["Evolucao visivel", "Historico, streak e nivel no mesmo painel."],
            ["Foco no que importa", "FREE para iniciar e PRO para acelerar."],
          ].map(([title, description]) => (
            <article key={title} className="rounded-2xl border border-slate-200 bg-white p-6">
              <h3 className="font-display text-xl">{title}</h3>
              <p className="mt-2 text-slate-600">{description}</p>
            </article>
          ))}
        </section>

        <section className="rounded-3xl bg-ink p-8 text-white">
          <h3 className="font-display text-3xl">FREE vs PRO</h3>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl bg-white/10 p-5">
              <p className="text-lg font-medium">FREE</p>
              <ul className="mt-3 space-y-2 text-sm text-white/80">
                <li>Acesso ao dashboard e progresso basico</li>
                <li>Recursos essenciais para criar habito</li>
                <li>Anuncios ativos</li>
              </ul>
            </div>
            <div className="rounded-2xl bg-lagoon p-5">
              <p className="text-lg font-medium">PRO</p>
              <ul className="mt-3 space-y-2 text-sm text-white/90">
                <li>Recursos premium de speaking e dialetos</li>
                <li>Experiencia sem anuncios</li>
                <li>Gestao de assinatura no Stripe</li>
              </ul>
            </div>
          </div>
        </section>

        <section id="precos" className="rounded-3xl border border-slate-200 bg-white p-8">
          <h3 className="font-display text-3xl">Pricing</h3>
          <p className="mt-2 text-slate-600">Comece no FREE e faca upgrade quando quiser.</p>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <article className="rounded-2xl border border-slate-200 p-5">
              <p className="text-sm text-slate-500">Plano FREE</p>
              <p className="mt-2 font-display text-3xl">R$ 0</p>
              <p className="mt-1 text-sm text-slate-600">Para comecar hoje</p>
            </article>
            <article className="rounded-2xl border border-lagoon bg-cyan-50 p-5">
              <p className="text-sm text-slate-500">Plano PRO</p>
              <p className="mt-2 font-display text-3xl">Assinatura mensal</p>
              <p className="mt-1 text-sm text-slate-600">Preco final definido no Stripe</p>
            </article>
          </div>
          <Link to="/register" className="mt-6 inline-block rounded-xl bg-ink px-5 py-3 font-medium text-white">
            Criar conta e testar
          </Link>
        </section>
      </main>
    </div>
  );
}
