import { useEffect, useMemo } from 'react';
import { ArrowRight, CheckCircle2, MessageSquare, ShieldCheck, Sparkles, Star, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { trackPublicGrowthEvent } from '../api/auth';

const featureCards = [
  {
    title: 'Conversacao com IA',
    text: 'Pratique dialogos reais em vez de so responder exercicios.',
  },
  {
    title: 'Correcao em tempo real',
    text: 'Receba feedback instantaneo sobre o que dizer e como melhorar.',
  },
  {
    title: 'Situacoes reais',
    text: 'Treine viagens, trabalho, reunioes, entrevistas e conversas do dia a dia.',
  },
  {
    title: 'Evolucao personalizada',
    text: 'A IA acompanha seu progresso e adapta o aprendizado ao seu ritmo.',
  },
  {
    title: 'Progresso visivel',
    text: 'Acompanhe streak, XP, nivel, missoes e evolucao semanal.',
  },
  {
    title: 'Plano FREE e PRO',
    text: 'Comece gratis e destrave pratica ilimitada quando quiser ir alem.',
  },
];

const testimonials = [
  {
    quote: 'Eu travava em toda reuniao em ingles. Em 3 semanas consegui falar sem decorar frases prontas.',
    author: 'Camila R.',
    role: 'Product Manager',
  },
  {
    quote: 'Parece um treino real. A IA corrige na hora e eu sei exatamente como responder melhor.',
    author: 'Rafael S.',
    role: 'Analista de Dados',
  },
  {
    quote: 'Finalmente um app que me faz falar de verdade, e nao so preencher lacunas.',
    author: 'Juliana M.',
    role: 'Profissional de Marketing',
  },
];

type LandingVariant = 'a' | 'b';
const VARIANT_STORAGE_KEY = 'linguaai_landing_variant';

function resolveLandingVariant(): LandingVariant {
  const abEnabled = (import.meta.env.VITE_LANDING_AB_TEST || 'false').toLowerCase() === 'true';
  if (!abEnabled) return 'a';

  const forced = (import.meta.env.VITE_LANDING_AB_VARIANT || '').trim().toLowerCase();
  if (forced === 'a' || forced === 'b') return forced;

  const saved = localStorage.getItem(VARIANT_STORAGE_KEY);
  if (saved === 'a' || saved === 'b') return saved;

  const chosen: LandingVariant = Math.random() < 0.5 ? 'a' : 'b';
  localStorage.setItem(VARIANT_STORAGE_KEY, chosen);
  return chosen;
}

export default function LandingPage() {
  const variant = useMemo(resolveLandingVariant, []);
  const copy = variant === 'a'
    ? {
        headline: 'Fale ingles com IA. De verdade.',
        subheadline: 'Pare de so estudar. Comece a conversar.',
      }
    : {
        headline: 'Fale ingles com IA sem travar.',
        subheadline: 'Saia do estudo passivo e entre em conversas reais.',
      };

  useEffect(() => {
    Promise.resolve(trackPublicGrowthEvent('landing_variant_exposed', { variant })).catch(() => {
      // keep landing resilient even if analytics is unavailable
    });
  }, [variant]);

  const handleTrack = (eventType: 'hero_cta_click' | 'demo_cta_click' | 'final_cta_click', placement: string) => {
    Promise.resolve(trackPublicGrowthEvent(eventType, { variant, placement })).catch(() => {
      // no-op for analytics errors in public page
    });
  };

  return (
    <div className="min-h-screen overflow-x-hidden bg-slate-950 text-slate-100">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_10%_0%,#1e3a8a_0%,#020617_48%,#020617_100%)]"></div>
      <div className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[460px] bg-[radial-gradient(circle_at_20%_20%,rgba(34,211,238,0.22),transparent_52%),radial-gradient(circle_at_78%_10%,rgba(56,189,248,0.20),transparent_48%)]"></div>

      <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <p className="text-lg font-black tracking-tight">LinguaAI</p>
          <div className="flex items-center gap-2">
            <Link to="/login" className="rounded-lg border border-white/20 px-3 py-1.5 text-xs font-semibold hover:bg-white/10">
              Login
            </Link>
            <Link to="/login" className="rounded-lg bg-white px-3 py-1.5 text-xs font-bold text-slate-900 hover:bg-slate-100">
              Comecar gratis
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="mx-auto max-w-6xl px-4 pb-16 pt-14 sm:pt-20">
          <div className="grid items-center gap-10 lg:grid-cols-[1.05fr_0.95fr]">
            <div>
              <p className="inline-flex items-center gap-2 rounded-full border border-cyan-300/40 bg-cyan-300/10 px-3 py-1 text-[11px] font-bold uppercase tracking-[0.2em] text-cyan-200">
                <Sparkles size={14} />
                Conversacao real com IA
              </p>
              <h1 className="mt-6 text-5xl font-black leading-[1.04] tracking-tight sm:text-6xl lg:text-7xl">{copy.headline}</h1>
              <p className="mt-5 text-xl font-semibold text-slate-100 sm:text-2xl">{copy.subheadline}</p>
              <p className="mt-5 max-w-2xl text-sm text-slate-300 sm:text-base">
                Pratique com uma IA que responde, corrige e evolui com voce - em minutos por dia.
              </p>
              <div className="mt-8 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center">
                <Link
                  to="/login"
                  onClick={() => handleTrack('hero_cta_click', 'hero_primary')}
                  className="inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-cyan-300 px-6 text-sm font-black text-slate-950 shadow-[0_18px_55px_-22px_rgba(103,232,249,0.95)] transition hover:-translate-y-0.5 hover:bg-cyan-200"
                >
                  Comecar gratis agora
                  <ArrowRight size={18} />
                </Link>
                <a
                  href="#demonstracao"
                  onClick={() => handleTrack('demo_cta_click', 'hero_secondary')}
                  className="inline-flex h-12 items-center justify-center rounded-xl border border-white/20 px-6 text-sm font-semibold text-white/95 transition hover:bg-white/10"
                >
                  Ver como funciona
                </a>
              </div>
              <div className="mt-6 flex flex-wrap gap-3 text-xs text-slate-300">
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5">Sem vergonha para praticar</span>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5">Feedback imediato</span>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5">Evolucao personalizada</span>
              </div>
            </div>

            <div id="demonstracao" className="relative">
              <div className="absolute -inset-4 rounded-3xl bg-gradient-to-br from-cyan-300/30 via-sky-300/10 to-indigo-300/20 blur-2xl"></div>
              <div className="relative rounded-3xl border border-white/15 bg-slate-900/85 p-4 shadow-2xl shadow-black/45">
                <div className="rounded-2xl border border-white/10 bg-slate-950/90 p-4">
                  <div className="mb-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="size-8 rounded-full bg-cyan-300/20 text-cyan-200 flex items-center justify-center">
                        <MessageSquare size={16} />
                      </div>
                      <div>
                        <p className="text-sm font-bold">LinguaAI Tutor</p>
                        <p className="text-[11px] text-emerald-300">ao vivo agora</p>
                      </div>
                    </div>
                    <span className="rounded-full border border-white/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-300">demo</span>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="ml-auto max-w-[85%] rounded-2xl rounded-br-md border border-cyan-200/20 bg-cyan-300/15 px-3 py-2">
                      <p className="text-cyan-100">I want food</p>
                    </div>
                    <div className="max-w-[92%] rounded-2xl rounded-tl-md border border-emerald-200/20 bg-emerald-300/10 px-3 py-2">
                      <p className="text-emerald-100">
                        You can say: <span className="font-bold">I&apos;d like to order food.</span>
                      </p>
                    </div>
                    <div className="max-w-[92%] rounded-2xl rounded-tl-md border border-sky-200/20 bg-sky-300/10 px-3 py-2">
                      <p className="text-sky-100">Quer treinar mais? Tente pedir uma bebida tambem.</p>
                    </div>
                  </div>

                  <div className="mt-4 grid gap-2 sm:grid-cols-2">
                    <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2">
                      <p className="text-[11px] text-slate-300">Correcao</p>
                      <p className="text-xs font-semibold text-white">Imediata</p>
                    </div>
                    <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2">
                      <p className="text-[11px] text-slate-300">Resposta sugerida</p>
                      <p className="text-xs font-semibold text-white">Natural e contextual</p>
                    </div>
                  </div>
                </div>
              </div>
              <p className="mt-3 text-center text-xs text-slate-400">Feito para quem quer falar de verdade.</p>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-12">
          <div className="rounded-2xl border border-white/10 bg-white/5 px-5 py-6 text-center text-xl font-bold text-white sm:text-2xl lg:text-3xl">
            Sem vergonha. Sem travar. Sem exercicios chatos. So pratica real com IA.
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-14">
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
              <p className="text-xs text-slate-300">Pessoas em pratica ativa</p>
              <p className="mt-1 text-2xl font-black text-white">+120k</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
              <p className="text-xs text-slate-300">Sessoes de conversacao por semana</p>
              <p className="mt-1 text-2xl font-black text-white">+1.4M</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
              <p className="text-xs text-slate-300">NPS (beta privada)</p>
              <p className="mt-1 text-2xl font-black text-white">72</p>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-14">
          <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-6 sm:p-8 lg:p-10">
            <h2 className="text-2xl font-black sm:text-3xl">Pare de decorar. Comece a falar.</h2>
            <p className="mt-3 text-sm text-slate-300">Apps ensinam palavras. LinguaAI coloca voce em conversa real com correcao no momento certo.</p>
            <div className="mt-6 grid gap-4 lg:grid-cols-2">
              <div className="rounded-xl border border-red-300/20 bg-red-300/5 p-5">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-red-200">Apps tradicionais</p>
                <ul className="mt-3 space-y-2 text-sm text-slate-200">
                  <li>- ensinam palavras isoladas</li>
                  <li>- focam em exercicios frios</li>
                  <li>- pouca conversa espontanea</li>
                  <li>- contexto artificial</li>
                </ul>
              </div>
              <div className="rounded-xl border border-cyan-300/30 bg-cyan-300/10 p-5">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan-100">LinguaAI</p>
                <ul className="mt-3 space-y-2 text-sm text-white">
                  <li>- faz voce conversar desde o primeiro dia</li>
                  <li>- corrige em tempo real</li>
                  <li>- adapta o aprendizado ao seu nivel</li>
                  <li>- cria pratica real com IA em situacoes reais</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-14">
          <div className="grid gap-6 rounded-2xl border border-white/10 bg-white/5 p-6 sm:grid-cols-[1.2fr_1fr]">
            <div>
              <h2 className="text-2xl font-black sm:text-3xl">Veja como funciona na pratica</h2>
              <div className="mt-4 space-y-3 rounded-xl border border-white/10 bg-slate-900/70 p-4 text-sm">
                <p>
                  <span className="font-bold text-cyan-200">Voce:</span> I want food
                </p>
                <p>
                  <span className="font-bold text-emerald-200">IA:</span> You can say: I&apos;d like to order food.
                </p>
                <p>
                  <span className="font-bold text-emerald-200">IA:</span> Quer treinar mais? Tente pedir uma bebida tambem.
                </p>
              </div>
            </div>
            <div className="space-y-3">
              {['correcao imediata', 'explicacao clara', 'proxima resposta sugerida', 'pratica natural'].map((item) => (
                <div key={item} className="flex items-center gap-3 rounded-xl border border-white/10 bg-black/25 px-4 py-3 text-sm">
                  <CheckCircle2 size={16} className="text-cyan-300" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-14">
          <h2 className="text-center text-2xl font-black sm:text-3xl">Tudo que voce precisa para comecar a falar</h2>
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {featureCards.map((card) => (
              <article key={card.title} className="rounded-xl border border-white/10 bg-white/[0.065] p-4 transition hover:-translate-y-0.5 hover:border-cyan-300/30 hover:bg-cyan-300/[0.07]">
                <p className="text-base font-bold">{card.title}</p>
                <p className="mt-2 text-sm text-slate-300">{card.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-14">
          <div className="rounded-2xl border border-white/10 bg-slate-900/65 p-6 sm:p-8">
            <div className="mb-5 flex items-center gap-2">
              <Star size={18} className="text-amber-300" />
              <h2 className="text-2xl font-black sm:text-3xl">Prova social</h2>
            </div>
            <div className="grid gap-3 lg:grid-cols-3">
              {testimonials.map((item) => (
                <article key={item.author} className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <p className="text-sm text-slate-200">&quot;{item.quote}&quot;</p>
                  <p className="mt-4 text-sm font-bold text-white">{item.author}</p>
                  <p className="text-xs text-slate-400">{item.role}</p>
                </article>
              ))}
            </div>
            <div className="mt-4 flex flex-wrap gap-3 text-xs">
              <span className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-slate-300">
                <TrendingUp size={13} className="text-cyan-300" />
                Feito para quem quer falar de verdade
              </span>
              <span className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-slate-300">
                <ShieldCheck size={13} className="text-emerald-300" />
                Sem julgamentos, com feedback acionavel
              </span>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-14">
          <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-cyan-300/15 via-slate-900/60 to-indigo-300/15 p-6 sm:p-8">
            <h2 className="text-2xl font-black sm:text-3xl">Voce nao precisa ser perfeito para comecar.</h2>
            <p className="mt-4 max-w-3xl text-sm text-slate-200 sm:text-base">
              A maioria das pessoas nao trava por falta de inteligencia. Trava por medo de errar. O LinguaAI foi feito para tirar essa barreira e colocar voce em pratica de verdade.
            </p>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-14">
          <h2 className="text-center text-2xl font-black sm:text-3xl">Comece em 3 passos</h2>
          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-white/10 bg-white/[0.065] p-4">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-200">1</p>
              <p className="mt-2 text-base font-bold">Escolha seu objetivo</p>
              <p className="mt-2 text-sm text-slate-300">Viagem, trabalho, fluencia ou pratica diaria.</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.065] p-4">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-200">2</p>
              <p className="mt-2 text-base font-bold">Converse com a IA</p>
              <p className="mt-2 text-sm text-slate-300">Receba respostas, correcoes e sugestoes em tempo real.</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.065] p-4">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-200">3</p>
              <p className="mt-2 text-base font-bold">Evolua todos os dias</p>
              <p className="mt-2 text-sm text-slate-300">Ganhe XP, mantenha streak e fale com mais confianca.</p>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-4xl px-4 pb-16">
          <div className="rounded-2xl border border-cyan-300/30 bg-gradient-to-br from-cyan-300/20 to-sky-300/10 p-6 text-center sm:p-9">
            <h2 className="text-2xl font-black text-white sm:text-3xl">Comece a falar ingles hoje</h2>
            <p className="mx-auto mt-3 max-w-2xl text-sm text-slate-200 sm:text-base">
              Crie sua conta gratis e faca sua primeira pratica com IA em minutos.
            </p>
            <p className="mx-auto mt-2 max-w-xl text-xs font-semibold uppercase tracking-[0.18em] text-cyan-100">
              Cada dia sem pratica e mais um dia sem confianca para falar
            </p>
            <Link
              to="/login"
              onClick={() => handleTrack('final_cta_click', 'final_section')}
              className="mt-6 inline-flex h-12 items-center justify-center rounded-xl bg-white px-7 text-sm font-black text-slate-900 shadow-xl shadow-cyan-500/20 transition hover:-translate-y-0.5"
            >
              Comecar gratis agora
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 bg-slate-950/80">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-6 text-sm text-slate-300 sm:flex-row sm:items-center sm:justify-between">
          <p className="font-bold text-white">LinguaAI</p>
          <nav className="flex flex-wrap items-center gap-4">
            <Link to="/login">Login</Link>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/privacy">Privacidade</Link>
            <Link to="/terms">Termos</Link>
            <a href="#">Contato</a>
          </nav>
        </div>
      </footer>
    </div>
  );
}
