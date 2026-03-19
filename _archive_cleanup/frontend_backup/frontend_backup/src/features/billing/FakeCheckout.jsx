import React, { useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import Card from "../../shared/ui/Card.jsx";
import Button from "../../shared/ui/Button.jsx";
import apiClient from "../../core/apiClient.js";

export default function FakeCheckout() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const userId = useMemo(() => searchParams.get("user_id"), [searchParams]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  const handleConfirm = async () => {
    setError("");
    setLoading(true);

    try {
      if (!userId) {
        throw new Error("user_id não encontrado na URL.");
      }

      // ✅ ESTE É O ENDPOINT QUE VAMOS CRIAR NO BACKEND:
      const res = await apiClient.request(`/billing/fake/confirm?user_id=${encodeURIComponent(userId)}`, {
        method: "POST",
      });

      console.log("[FakeCheckout] confirm response:", res);

      setDone(true);

      // dá um tempinho pra mostrar "OK" e volta pro dashboard
      setTimeout(() => {
        navigate("/dashboard", { replace: true });
      }, 600);
    } catch (err) {
      console.error("[FakeCheckout] confirm error:", err);
      setError(err?.message || "Falha ao confirmar pagamento.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-10">
      <div className="mx-auto max-w-2xl">
        <Card>
          <h1 className="font-display text-3xl">Checkout de teste</h1>

          <p className="mt-3 text-slate-600">
            Este ambiente está usando checkout fake para desenvolvimento/testes.
          </p>

          <div className="mt-4 text-slate-700">
            <div>
              <strong>Usuário:</strong> {userId || "—"}
            </div>
            <div className="text-slate-500 text-sm mt-1">
              URL esperada: <code>/billing/fake-checkout?user_id=SEU_ID</code>
            </div>
          </div>

          {error ? (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-red-700">
              <strong>Erro:</strong> {error}
            </div>
          ) : null}

          {done ? (
            <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-emerald-800">
              ✅ Pagamento confirmado. Atualizando sua conta para PRO e voltando ao dashboard...
            </div>
          ) : null}

          <div className="mt-6 flex flex-wrap gap-3">
            <Button onClick={handleConfirm} disabled={loading || done}>
              {loading ? "Confirmando..." : "Confirmar pagamento (PRO)"}
            </Button>

            <Link to="/dashboard">
              <Button variant="secondary">Voltar ao dashboard</Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
