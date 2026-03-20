import { ArrowLeft } from 'lucide-react';
import { PedagogyModule } from '../types';

interface Props {
  modules: PedagogyModule[];
  currentModuleId?: number | null;
  onBack: () => void;
  onOpenModule: (moduleId: number) => void;
}

export default function TrackScreen({ modules, currentModuleId, onBack, onOpenModule }: Props) {
  return (
    <div className="min-h-screen bg-background-light pb-10">
      <div className="max-w-md mx-auto px-4 py-4 space-y-4">
        <button onClick={onBack} className="rounded-full border border-slate-300 bg-white p-2">
          <ArrowLeft size={16} />
        </button>
        <section className="rounded-xl bg-white border border-slate-200 p-4">
          <h1 className="text-xl font-black">English Foundations A1</h1>
          <p className="text-sm text-slate-600">Trilha sequencial com foco em aprendizagem clara.</p>
        </section>
        {modules.length === 0 ? (
          <section className="rounded-xl border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm font-bold text-amber-800">Sua primeira aula esta pronta.</p>
            <p className="text-xs text-amber-700 mt-1">Ainda estamos carregando os modulos. Tente novamente em instantes.</p>
          </section>
        ) : null}
        {modules.map((module) => (
          <button
            key={module.id}
            onClick={() => onOpenModule(module.id)}
            className={`w-full rounded-xl border p-4 text-left ${currentModuleId === module.id ? 'border-slate-900 bg-slate-50' : 'border-slate-200 bg-white'}`}
          >
            <div className="flex items-center justify-between">
              <p className="font-bold">{module.title}</p>
              <span className="text-xs font-bold">{module.progress_percent}%</span>
            </div>
            <p className="mt-1 text-xs text-slate-500">{module.lessons.length} aulas {currentModuleId === module.id ? '• modulo atual' : ''}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
