import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { ArrowLeft, CheckCircle2 } from 'lucide-react';
import LessonConversationPanel from './LessonConversationPanel';
import { LessonDetail } from '../types';

interface Props {
  lesson: LessonDetail | null;
  submitting: boolean;
  onBack: () => void;
  onSaveStep: (lessonId: number, currentStep: number) => Promise<void>;
  onComplete: (lessonId: number) => Promise<{ nextLessonId: number | null; xpEarned: number; reviewCount: number }>;
  onOpenNextLesson: (lessonId: number) => Promise<void>;
  onOpenTrack: () => void;
  onPracticeConversation: () => void;
}

interface LessonStep {
  id: string;
  title: string;
  render: () => ReactNode;
}

export default function PedagogyLessonScreen({
  lesson,
  submitting,
  onBack,
  onSaveStep,
  onComplete,
  onOpenNextLesson,
  onOpenTrack,
  onPracticeConversation,
}: Props) {
  const [stepIndex, setStepIndex] = useState(0);
  const [completion, setCompletion] = useState<{
    nextLessonId: number | null;
    xpEarned: number;
    reviewCount: number;
  } | null>(null);
  const [screenError, setScreenError] = useState('');

  useEffect(() => {
    if (!lesson) return;
    setStepIndex(Math.max(0, Math.min(lesson.progress.current_step, 9)));
    setCompletion(null);
    setScreenError('');
  }, [lesson]);

  const steps = useMemo<LessonStep[]>(() => {
    if (!lesson) return [];

    return [
      {
        id: 'goal',
        title: 'Objetivo da aula',
        render: () => (
          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <h2 className="font-bold">Objetivo</h2>
            <p className="mt-2 text-sm text-slate-700">{lesson.lesson_objective}</p>
          </section>
        ),
      },
      {
        id: 'vocab',
        title: 'Vocabulario principal',
        render: () => (
          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <h2 className="font-bold">Vocabulario principal</h2>
            <p className="mt-2 text-sm text-slate-700">{lesson.target_vocabulary.join(', ')}</p>
          </section>
        ),
      },
      {
        id: 'examples',
        title: 'Exemplos',
        render: () => (
          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <h2 className="font-bold">Exemplos</h2>
            <div className="mt-2 space-y-2">
              {lesson.examples.map((item, idx) => (
                <div key={`${item.en}-${idx}`} className="rounded-lg bg-slate-50 p-2">
                  <p className="text-sm">{item.en}</p>
                  <p className="text-xs text-slate-500">{item.pt}</p>
                </div>
              ))}
            </div>
          </section>
        ),
      },
      {
        id: 'grammar',
        title: 'Explicacao breve',
        render: () => (
          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <h2 className="font-bold">Explicacao breve</h2>
            <p className="mt-2 text-sm text-slate-700">{lesson.grammar_explanation_pt}</p>
          </section>
        ),
      },
      {
        id: 'ex1',
        title: 'Exercicio 1',
        render: () => <ExerciseCard exercise={lesson.exercises[0]} />,
      },
      {
        id: 'ex2',
        title: 'Exercicio 2',
        render: () => <ExerciseCard exercise={lesson.exercises[1]} />,
      },
      {
        id: 'ex3',
        title: 'Exercicio 3',
        render: () => <ExerciseCard exercise={lesson.exercises[2]} />,
      },
      {
        id: 'practice',
        title: 'Mini pratica guiada com IA',
        render: () => (
          <LessonConversationPanel
            lessonTitle={lesson.title}
            onPractice={onPracticeConversation}
          />
        ),
      },
      {
        id: 'summary',
        title: 'Resumo final',
        render: () => (
          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <h2 className="font-bold">Resumo do que aprendeu</h2>
            <ul className="mt-2 space-y-1">
              {lesson.final_review.map((line) => (
                <li key={line} className="text-sm text-slate-700">
                  • {line}
                </li>
              ))}
            </ul>
          </section>
        ),
      },
      {
        id: 'finish',
        title: 'Concluir aula',
        render: () => (
          <section className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
            <h2 className="font-bold text-emerald-800">Concluir aula</h2>
            <p className="mt-2 text-sm text-emerald-800">
              Finalize para salvar progresso, desbloquear a proxima aula e enviar itens para revisao.
            </p>
          </section>
        ),
      },
    ];
  }, [lesson, onPracticeConversation]);

  if (!lesson) {
    return (
      <div className="min-h-screen bg-background-light px-4 py-6">
        <button onClick={onBack} className="rounded-full border border-slate-300 bg-white p-2">
          <ArrowLeft size={16} />
        </button>
        <p className="mt-4 text-sm text-slate-600">Licao nao encontrada.</p>
      </div>
    );
  }

  if (completion) {
    return (
      <div className="min-h-screen bg-background-light pb-10">
        <div className="mx-auto max-w-md space-y-4 px-4 py-5">
          <section className="rounded-xl border border-emerald-200 bg-white p-5">
            <h1 className="text-xl font-black text-emerald-700">Aula concluida</h1>
            <p className="mt-2 text-sm text-slate-700">Voce concluiu: {lesson.title}</p>
            <p className="mt-1 text-sm text-slate-700">
              XP ganho: <span className="font-bold">{completion.xpEarned}</span>
            </p>
            <p className="mt-1 text-sm text-slate-700">
              Vocabulario novo: <span className="font-bold">{lesson.target_vocabulary.length}</span>
            </p>
            <p className="mt-1 text-sm text-slate-700">
              Itens para revisar: <span className="font-bold">{completion.reviewCount}</span>
            </p>
          </section>

          {completion.nextLessonId ? (
            <button
              onClick={() => void onOpenNextLesson(completion.nextLessonId)}
              className="w-full rounded-xl bg-slate-900 py-3 font-bold text-white"
            >
              Proxima aula
            </button>
          ) : null}

          <button
            onClick={onOpenTrack}
            className="w-full rounded-xl border border-slate-300 bg-white py-3 font-bold text-slate-800"
          >
            Voltar para trilha
          </button>
        </div>
      </div>
    );
  }

  const totalSteps = 10;
  const currentStep = Math.max(0, Math.min(stepIndex, totalSteps - 1));
  const percent = Math.round(((currentStep + 1) / totalSteps) * 100);
  const isFinalStep = currentStep === totalSteps - 1;

  const handleContinue = async () => {
    if (!lesson) return;

    try {
      setScreenError('');
      const nextStep = Math.min(currentStep + 1, totalSteps - 1);
      await onSaveStep(lesson.id, nextStep);
      setStepIndex(nextStep);
    } catch (error) {
      console.error('Erro ao salvar etapa:', error);
      setScreenError('Nao foi possivel salvar esta etapa. Tente novamente.');
    }
  };

  const handleComplete = async () => {
    if (!lesson) return;

    try {
      setScreenError('');

      // Garante que o backend receba o passo final antes da conclusao
      await onSaveStep(lesson.id, lesson.progress.total_steps);

      const result = await onComplete(lesson.id);
      setCompletion(result);
    } catch (error) {
      console.error('Erro ao concluir aula:', error);
      setScreenError('Nao foi possivel concluir a aula agora. Tente novamente.');
    }
  };

  return (
    <div className="min-h-screen bg-background-light pb-10">
      <div className="mx-auto max-w-md space-y-4 px-4 py-5">
        <button onClick={onBack} className="rounded-full border border-slate-300 bg-white p-2">
          <ArrowLeft size={16} />
        </button>

        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <h1 className="text-xl font-black">{lesson.title}</h1>
          <p className="mt-1 text-xs text-slate-500">Modulo: {lesson.module_name}</p>
          <p className="mt-1 text-xs text-slate-500">
            Etapa {currentStep + 1}/{totalSteps} • {steps[currentStep]?.title}
          </p>
          <div className="mt-3 h-2 w-full rounded-full bg-slate-200">
            <div
              className="h-2 rounded-full bg-slate-900 transition-all"
              style={{ width: `${percent}%` }}
            />
          </div>
        </section>

        {screenError ? (
          <section className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {screenError}
          </section>
        ) : null}

        {steps[currentStep]?.render()}

        {!isFinalStep ? (
          <button
            onClick={() => void handleContinue()}
            className="w-full rounded-xl bg-slate-900 py-3 font-bold text-white"
          >
            Continuar etapa
          </button>
        ) : (
          <button
            onClick={() => void handleComplete()}
            disabled={submitting}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3 font-bold text-white disabled:opacity-60"
          >
            <CheckCircle2 size={18} />
            {submitting ? 'Finalizando...' : 'Concluir aula'}
          </button>
        )}
      </div>
    </div>
  );
}

function ExerciseCard({
  exercise,
}: {
  exercise?: { type: string; prompt: string; hint_pt: string };
}) {
  if (!exercise) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <h2 className="font-bold">Exercicio</h2>
        <p className="mt-2 text-sm text-slate-600">Sem exercicio disponivel para esta etapa.</p>
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4">
      <h2 className="font-bold">{exercise.type}</h2>
      <p className="mt-2 text-sm text-slate-700">{exercise.prompt}</p>
      <p className="mt-2 text-xs text-slate-500">Dica: {exercise.hint_pt}</p>
    </section>
  );
}