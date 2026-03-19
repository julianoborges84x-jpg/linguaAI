import { PedagogyDashboardData } from '../types';

interface Props {
  data: PedagogyDashboardData;
}

export default function WeaknessFocusCard({ data }: Props) {
  return (
    <section className="rounded-xl border border-rose-200 bg-rose-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-wider text-rose-700">Foco recomendado</p>
      <p className="mt-1 text-sm font-bold text-rose-900">{data.weaknesses[0] || 'Sem fraqueza dominante no momento'}</p>
      <p className="mt-2 text-xs text-rose-700">Erros recorrentes</p>
      <div className="mt-1 flex flex-wrap gap-1">
        {(data.recurring_errors.length ? data.recurring_errors : ['Nenhum erro recorrente detectado']).slice(0, 3).map((item) => (
          <span key={item} className="rounded-full bg-white px-2 py-1 text-[11px] font-semibold text-rose-700">{item}</span>
        ))}
      </div>
    </section>
  );
}
