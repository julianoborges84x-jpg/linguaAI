import React from "react";
import { Link } from "react-router-dom";

export default function PrivacyPage() {
  return (
    <main className="mx-auto min-h-screen max-w-4xl px-6 py-10">
      <Link to="/" className="text-sm text-lagoon">Voltar para home</Link>
      <h1 className="mt-4 font-display text-4xl">Politica de Privacidade</h1>
      <p className="mt-6 text-slate-700">
        Coletamos dados de cadastro e uso para operar o produto, personalizar a experiencia e garantir seguranca da conta.
      </p>
      <h2 className="mt-8 font-display text-2xl">Dados coletados</h2>
      <p className="mt-2 text-slate-700">
        Nome, email, configuracoes de idioma, progresso de estudo e eventos de assinatura.
      </p>
      <h2 className="mt-8 font-display text-2xl">Pagamento</h2>
      <p className="mt-2 text-slate-700">
        Dados de pagamento sao processados pelo Stripe. O LinguaAI nao armazena numero completo de cartao.
      </p>
      <h2 className="mt-8 font-display text-2xl">Direitos do usuario</h2>
      <p className="mt-2 text-slate-700">
        Voce pode solicitar atualizacao ou exclusao dos seus dados conforme legislacao aplicavel.
      </p>
    </main>
  );
}
