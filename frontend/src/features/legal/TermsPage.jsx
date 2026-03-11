import React from "react";
import { Link } from "react-router-dom";

export default function TermsPage() {
  return (
    <main className="mx-auto min-h-screen max-w-4xl px-6 py-10">
      <Link to="/" className="text-sm text-lagoon">Voltar para home</Link>
      <h1 className="mt-4 font-display text-4xl">Termos de Uso</h1>
      <p className="mt-6 text-slate-700">
        Ao usar o LinguaAI, voce concorda em utilizar a plataforma para fins legais e respeitar os limites do plano contratado.
      </p>
      <h2 className="mt-8 font-display text-2xl">Conta e acesso</h2>
      <p className="mt-2 text-slate-700">
        O usuario e responsavel pela seguranca das credenciais e pelas atividades realizadas em sua conta.
      </p>
      <h2 className="mt-8 font-display text-2xl">Assinatura</h2>
      <p className="mt-2 text-slate-700">
        Assinaturas PRO sao processadas pelo Stripe. Renovacao, cancelamento e reembolso seguem as regras do checkout e do portal de cobranca.
      </p>
      <h2 className="mt-8 font-display text-2xl">Disponibilidade</h2>
      <p className="mt-2 text-slate-700">
        O servico pode sofrer manutencoes e atualizacoes sem aviso previo para melhoria de performance e seguranca.
      </p>
    </main>
  );
}
