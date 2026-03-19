import { PedagogyDashboardData } from '../types';

interface Props {
  data: PedagogyDashboardData;
  onAction: () => void;
}

export default function SmartRecommendationCard({ data, onAction }: Props) {
  return (
    <section className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-wider text-indigo-700">Proximo passo inteligente</p>
      <p className="mt-1 text-sm font-black text-indigo-900">{data.next_step.title}</p>
      <p className="mt-1 text-xs text-indigo-700">{data.next_step.description}</p>
      <button type="button" onClick={onAction} className="mt-3 w-full rounded-lg bg-slate-900 px-3 py-2 text-sm font-bold text-white">
        {data.next_step.locked_for_free ? 'Desbloquear PRO para continuar' : 'Continuar trilha'}
      </button>
    </section>
  );
}
