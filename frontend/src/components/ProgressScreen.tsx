import { ArrowLeft } from 'lucide-react';
import { ProgressSummaryData } from '../types';

interface Props {
  data: ProgressSummaryData | null;
  onBack: () => void;
}

export default function ProgressScreen({ data, onBack }: Props) {
  return (
    <div className="min-h-screen bg-background-light px-4 py-6">
      <div className="max-w-md mx-auto space-y-4">
        <button onClick={onBack} className="rounded-full border border-slate-300 bg-white p-2">
          <ArrowLeft size={16} />
        </button>
        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h1 className="text-xl font-black">Progresso Pedagogico</h1>
          <p className="text-sm text-slate-600">Foco: o que voce aprendeu e o que vem agora.</p>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-4 grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-slate-500">Licoes</p>
            <p className="font-black">{data?.lesson_progress.completed ?? 0}/{data?.lesson_progress.total ?? 0}</p>
          </div>
          <div>
            <p className="text-slate-500">Trilha</p>
            <p className="font-black">{data?.module_completion ?? 0}%</p>
          </div>
          <div>
            <p className="text-slate-500">Revisao pendente</p>
            <p className="font-black">{data?.review_due ?? 0}</p>
          </div>
          <div>
            <p className="text-slate-500">Nivel estimado</p>
            <p className="font-black">{data?.estimated_level ?? 'A1'}</p>
          </div>
        </section>
      </div>
    </div>
  );
}
