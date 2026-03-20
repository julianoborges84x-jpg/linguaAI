import { ArrowLeft } from 'lucide-react';
import { ReviewTodayData } from '../types';

interface Props {
  data: ReviewTodayData | null;
  onBack: () => void;
  onSubmit: (reviewItemId: number, correct: boolean) => void;
}

export default function ReviewTodayScreen({ data, onBack, onSubmit }: Props) {
  return (
    <div className="min-h-screen bg-background-light px-4 py-6">
      <div className="max-w-md mx-auto space-y-4">
        <button onClick={onBack} className="rounded-full border border-slate-300 bg-white p-2">
          <ArrowLeft size={16} />
        </button>
        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h1 className="text-xl font-black">Revisao de Hoje</h1>
          <p className="text-sm text-slate-600">Tempo estimado: {data?.estimated_minutes ?? 5} min</p>
        </section>
        {(data?.items || []).length === 0 ? (
          <section className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
            Nada pendente agora. Volte depois para consolidar.
          </section>
        ) : (
          (data?.items || []).map((item) => (
            <section key={item.id} className="rounded-xl border border-slate-200 bg-white p-4 space-y-2">
              <p className="text-sm font-bold">{item.queue_type}</p>
              <p className="text-xs text-slate-500">Referencia {item.reference_id} • prioridade {item.priority}</p>
              <div className="grid grid-cols-2 gap-2">
                <button onClick={() => onSubmit(item.id, true)} className="rounded-lg border border-emerald-300 bg-emerald-50 py-2 text-sm font-bold text-emerald-700">Acertei</button>
                <button onClick={() => onSubmit(item.id, false)} className="rounded-lg border border-amber-300 bg-amber-50 py-2 text-sm font-bold text-amber-700">Errei</button>
              </div>
            </section>
          ))
        )}
      </div>
    </div>
  );
}
