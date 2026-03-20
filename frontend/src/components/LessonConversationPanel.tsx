interface Props {
  lessonTitle: string;
  onPractice: () => void;
}

export default function LessonConversationPanel({ lessonTitle, onPractice }: Props) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 space-y-2">
      <h3 className="font-black text-sm uppercase tracking-[0.12em] text-slate-500">Mini pratica com IA</h3>
      <p className="text-sm text-slate-700">
        Contexto da aula: <span className="font-bold">{lessonTitle}</span>.
      </p>
      <p className="text-xs text-slate-500">Formato: resposta, correcao, explicacao e nova tentativa guiada.</p>
      <button onClick={onPractice} className="w-full rounded-lg bg-slate-900 text-white py-2 text-sm font-bold">
        Praticar conversa da aula
      </button>
    </section>
  );
}
