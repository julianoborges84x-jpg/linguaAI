import { RefreshCw } from 'lucide-react';
import { AuthUser, CurrentTrackData, PedagogyDashboardData, ProgressSummaryData, ReviewTodayData } from '../types';

interface Props {
  user: AuthUser;
  track: CurrentTrackData | null;
  pedagogy: PedagogyDashboardData | null;
  summary: ProgressSummaryData | null;
  reviewToday: ReviewTodayData | null;
  onContinue: () => void;
  onReviewErrors: () => void;
  onOpenTrack: () => void;
  appError?: string;
}

export default function LearningHome({
  user,
  track,
  pedagogy,
  summary,
  reviewToday,
  onContinue,
  onReviewErrors,
  onOpenTrack,
  appError,
}: Props) {
  const resumeLabel = track?.resume_available ? 'Continuar aula de onde voce parou' : 'Continuar aula';
  return (
    <div className="min-h-screen bg-background-light pb-20">
      <main className="max-w-md mx-auto px-4 py-5 space-y-4">
        {appError ? <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{appError}</div> : null}
        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="text-xs uppercase font-bold tracking-[0.18em] text-slate-500">Painel de Aprendizagem</p>
          <h1 className="mt-2 text-2xl font-black text-slate-900">Hello, {user.name}</h1>
          <p className="mt-2 text-sm text-slate-600">
            Nivel atual: <span className="font-bold">{track?.estimated_level || pedagogy?.estimated_level || 'A1'}</span>
            {' '}• Trilha: <span className="font-bold">{track?.track_title || 'English Foundations A1'}</span>
          </p>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-5 space-y-2">
          <h2 className="text-lg font-black">Hoje voce vai aprender</h2>
          <p className="text-sm text-slate-700">{pedagogy?.next_step?.title || 'Licao inicial da trilha A1'}</p>
          <p className="text-xs text-slate-500">{pedagogy?.next_step?.description || 'Microlicao curta com exercicios e pratica guiada.'}</p>
          <p className="text-xs text-slate-500">
            Modulo atual: <span className="font-semibold text-slate-700">{track?.current_module_id ?? 1}</span>
            {' '}• Aula atual: <span className="font-semibold text-slate-700">{track?.current_lesson_id ?? track?.next_lesson_id ?? 1}</span>
            {' '}• Etapa: <span className="font-semibold text-slate-700">{(track?.current_step_index ?? 0) + 1}/10</span>
          </p>
          <button onClick={onContinue} className="mt-3 w-full rounded-xl bg-slate-900 text-white py-3 font-bold">
            {resumeLabel}
          </button>
          <button onClick={onReviewErrors} className="w-full rounded-xl border border-slate-300 bg-white text-slate-800 py-3 font-bold">
            Revisar agora
          </button>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-black uppercase tracking-[0.14em] text-slate-500">Progresso simples</h2>
          <p className="mt-2 text-sm text-slate-700">
            Aulas concluidas: <span className="font-bold">{summary?.lesson_progress?.completed ?? track?.completed_lessons ?? 0}</span>
            {' / '}
            <span className="font-bold">{summary?.lesson_progress?.total ?? track?.total_lessons ?? 24}</span>
          </p>
          <p className="text-sm text-slate-700 inline-flex items-center gap-2">
            <RefreshCw size={14} className="text-amber-700" />
            Voce tem <span className="font-bold">{summary?.review_due ?? reviewToday?.items.length ?? 0}</span> itens para revisar hoje
          </p>
          <div className="mt-3">
            <button onClick={onOpenTrack} className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-bold">Ver trilha completa</button>
          </div>
        </section>
      </main>
    </div>
  );
}
