import { Send } from 'lucide-react';

type VoiceLine = {
  role: 'user' | 'mentor';
  text: string;
};

interface Props {
  transcript: string;
  conversation: VoiceLine[];
  input: string;
  disabled: boolean;
  onInputChange: (value: string) => void;
  onSubmit: () => void;
  mentorName: string;
}

export default function VoiceConversationPanel({
  transcript,
  conversation,
  input,
  disabled,
  onInputChange,
  onSubmit,
  mentorName,
}: Props) {
  return (
    <section className="space-y-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Transcricao ao vivo</p>
        <p className="mt-1 text-sm text-slate-800">{transcript || 'Aguardando sua fala...'}</p>
      </div>

      <div className="max-h-56 space-y-2 overflow-auto rounded-xl border border-slate-200 bg-slate-50 p-3">
        {conversation.length === 0 ? <p className="text-sm text-slate-500">A conversa vai aparecer aqui em texto.</p> : null}
        {conversation.map((line, idx) => (
          <div
            key={`${line.role}-${idx}`}
            className={`rounded-lg px-3 py-2 text-sm ${line.role === 'mentor' ? 'border border-slate-200 bg-white' : 'ml-8 bg-primary text-white'}`}
          >
            <p className="mb-1 text-[10px] font-bold uppercase opacity-70">{line.role === 'mentor' ? mentorName : 'Voce'}</p>
            <p>{line.text}</p>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder="Digite para enviar sem microfone..."
          className="flex-1 rounded-xl border border-slate-300 px-3 py-2 text-sm"
        />
        <button
          type="button"
          aria-label="Enviar mensagem"
          onClick={onSubmit}
          disabled={disabled}
          className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-3 py-2 text-slate-700 disabled:opacity-50"
        >
          <Send size={16} />
        </button>
      </div>
    </section>
  );
}
