import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PedagogyLessonScreen from './PedagogyLessonScreen';
import { LessonDetail } from '../types';

const lessonMock: LessonDetail = {
  id: 10,
  module_name: 'Primeiros Contatos',
  order_index: 1,
  title: 'Greetings and Introductions',
  lesson_objective: 'Introduce yourself in English.',
  cefr_level: 'A1',
  estimated_duration_min: 12,
  target_vocabulary: ['hello', 'name', 'please'],
  key_structures: ['My name is...', 'Nice to meet you.'],
  grammar_explanation_pt: 'Use frases curtas.',
  examples: [{ en: 'Hello, I am Ana.', pt: 'Ola, eu sou Ana.' }],
  exercises: [
    { id: '1', type: 'multiple_choice', prompt: 'Pick best greeting', hint_pt: 'Leia o contexto.' },
    { id: '2', type: 'fill', prompt: 'Complete with am/is', hint_pt: 'Verbo to be.' },
    { id: '3', type: 'order', prompt: 'Order words', hint_pt: 'Sujeito + verbo.' },
  ],
  ai_context: {},
  final_review: ['You can introduce yourself.'],
  completion_criteria: { min_exercises_correct: 4, min_conversation_turns: 2, checkpoint_required: true },
  progress: { current_step: 0, total_steps: 10, completed: false, score: 0 },
};

describe('PedagogyLessonScreen', () => {
  it('avanca etapa sem concluir aula no meio do fluxo', async () => {
    const user = userEvent.setup();
    const onSaveStep = vi.fn().mockResolvedValue(undefined);
    const onComplete = vi.fn().mockResolvedValue({ nextLessonId: 11, xpEarned: 80, reviewCount: 2 });

    render(
      <PedagogyLessonScreen
        lesson={lessonMock}
        submitting={false}
        onBack={() => undefined}
        onSaveStep={onSaveStep}
        onComplete={onComplete}
        onOpenNextLesson={async () => undefined}
        onOpenTrack={() => undefined}
        onPracticeConversation={() => undefined}
      />,
    );

    expect(screen.getByText(/Etapa 1\/10/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Continuar etapa/i }));
    await waitFor(() => expect(onSaveStep).toHaveBeenCalledWith(10, 1));
    expect(onComplete).not.toHaveBeenCalled();
  });
});
