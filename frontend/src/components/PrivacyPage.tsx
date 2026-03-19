import { Link } from 'react-router-dom';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <main className="mx-auto max-w-3xl px-4 py-10">
        <Link to="/" className="text-sm font-semibold text-cyan-300 hover:underline">
          Voltar para home
        </Link>
        <h1 className="mt-4 text-3xl font-black">Privacidade</h1>
        <p className="mt-4 text-sm text-slate-300">
          O LinguaAI coleta dados essenciais para autenticacao, uso do produto, progresso de aprendizado e analytics
          de conversao para melhorar a experiencia.
        </p>
        <section className="mt-6 space-y-4 text-sm text-slate-200">
          <p>
            <strong>Dados coletados:</strong> email, nome, eventos de uso, progresso (XP, streak, sessoes) e eventos
            anonimos da landing para medir CAC e conversao.
          </p>
          <p>
            <strong>Uso dos dados:</strong> personalizar aprendizado, operar cobranca quando aplicavel, melhorar o
            produto e prevenir abuso.
          </p>
          <p>
            <strong>Compartilhamento:</strong> nao vendemos dados pessoais. Integracoes como Stripe sao usadas apenas
            para processamento de pagamento.
          </p>
          <p>
            <strong>Contato:</strong> para solicitacoes de dados, exclusao ou correcoes, use o canal de contato
            informado no produto.
          </p>
        </section>
      </main>
    </div>
  );
}
