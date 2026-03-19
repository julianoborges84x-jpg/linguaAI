import { Link } from 'react-router-dom';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <main className="mx-auto max-w-3xl px-4 py-10">
        <Link to="/" className="text-sm font-semibold text-cyan-300 hover:underline">
          Voltar para home
        </Link>
        <h1 className="mt-4 text-3xl font-black">Termos de Uso</h1>
        <p className="mt-4 text-sm text-slate-300">
          Ao usar o LinguaAI, voce concorda com estes termos para uso responsavel da plataforma de pratica de idiomas.
        </p>
        <section className="mt-6 space-y-4 text-sm text-slate-200">
          <p>
            <strong>Conta:</strong> voce e responsavel por manter suas credenciais seguras e pelas atividades na conta.
          </p>
          <p>
            <strong>Uso aceitavel:</strong> e proibido uso abusivo, tentativa de fraude, scraping indevido ou violacao
            de seguranca da plataforma.
          </p>
          <p>
            <strong>Planos:</strong> recursos FREE e PRO podem mudar com aviso previo. Assinaturas seguem regras de
            cobranca e cancelamento do provedor de pagamento.
          </p>
          <p>
            <strong>Disponibilidade:</strong> buscamos alta disponibilidade, mas nao garantimos servico ininterrupto.
          </p>
        </section>
      </main>
    </div>
  );
}
