import { PedagogyDashboardData } from '../types';

interface Props {
  data: PedagogyDashboardData;
}

export default function LearningProgressCard({ data }: Props) {
  return (
    <section className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700">Seu nivel estimado</p>
      <p className="mt-1 text-2xl font-black text-emerald-900">{data.estimated_level}</p>
      <p className="text-xs text-emerald-700">Confianca da estimativa: {Math.round(data.confidence * 100)}%</p>
      <div className="mt-3 grid grid-cols-5 gap-1">
        {['A1', 'A2', 'B1', 'B2', 'C1'].map((level) => (
          <div key={level} className={`rounded px-2 py-1 text-center text-[10px] font-bold ${level === data.estimated_level ? 'bg-emerald-700 text-white' : 'bg-white text-emerald-700'}`}>
            {level}
          </div>
        ))}
      </div>
    </section>
  );
}
