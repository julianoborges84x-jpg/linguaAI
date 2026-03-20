import { ArrowLeft, Lock } from 'lucide-react';
import { PedagogyModule } from '../types';

interface Props {
  module: PedagogyModule | null;
  currentLessonId?: number | null;
  onBack: () => void;
  onOpenLesson: (lessonId: number) => void;
}

export default function ModuleScreen({ module, currentLessonId, onBack, onOpenLesson }: Props) {
  if (!module) {
    return (
      <div className="min-h-screen bg-background-light px-4 py-6">
        <button onClick={onBack} className="rounded-full border border-slate-300 bg-white p-2">
          <ArrowLeft size={16} />
        </button>
        <p className="mt-4 text-sm text-slate-600">Modulo nao encontrado.</p>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-background-light px-4 py-6">
      <div className="max-w-md mx-auto space-y-4">
        <button onClick={onBack} className="rounded-full border border-slate-300 bg-white p-2">
          <ArrowLeft size={16} />
        </button>
        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h1 className="text-xl font-black">{module.title}</h1>
          <p className="text-sm text-slate-600">Progresso do modulo: {module.progress_percent}%</p>
        </section>
        {module.lessons.length === 0 ? (
          <section className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            Nenhuma aula encontrada. Execute seed pedagogico para popular o conteudo.
          </section>
        ) : null}
        {module.lessons.map((lesson) => (
          <button
            key={lesson.id}
            onClick={() => lesson.status === 'bloqueada' ? undefined : onOpenLesson(lesson.id)}
            className={`w-full rounded-xl border p-4 text-left disabled:opacity-60 ${currentLessonId === lesson.id ? 'border-slate-900 bg-slate-50' : 'border-slate-200 bg-white'}`}
            disabled={lesson.status === 'bloqueada'}
          >
            <div className="flex items-center justify-between">
              <p className="font-bold">{lesson.title}</p>
              {lesson.status === 'bloqueada' ? <Lock size={14} className="text-slate-500" /> : null}
            </div>
            <p className="text-xs text-slate-500">
              Status: {lesson.status} • passo {lesson.current_step}/{lesson.total_steps}
              {currentLessonId === lesson.id ? ' • aula atual' : ''}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
