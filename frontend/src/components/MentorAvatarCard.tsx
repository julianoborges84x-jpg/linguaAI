import { Mic, Brain, Volume2, Repeat2, VolumeX } from 'lucide-react';
import type { RefObject } from 'react';
import { VoiceMentor } from '../types';

type TutorState = 'idle' | 'listening' | 'thinking' | 'speaking';

interface Props {
  mentor: VoiceMentor | null;
  state: TutorState;
  muted: boolean;
  clientListening: boolean;
  localVideoRef: RefObject<HTMLVideoElement | null>;
  localVideoEnabled: boolean;
  onToggleMute: () => void;
  onReplay: () => void;
}

const stateLabel: Record<TutorState, string> = {
  idle: 'pronto',
  listening: 'ouvindo',
  thinking: 'pensando',
  speaking: 'falando',
};

export default function MentorAvatarCard({
  mentor,
  state,
  muted,
  clientListening,
  localVideoRef,
  localVideoEnabled,
  onToggleMute,
  onReplay,
}: Props) {
  const ringClass = state === 'speaking'
    ? 'ring-4 ring-emerald-300 animate-pulse'
    : state === 'listening'
      ? 'ring-4 ring-sky-300'
      : state === 'thinking'
        ? 'ring-4 ring-amber-300'
        : 'ring-2 ring-slate-200';

  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200 bg-slate-900 text-white shadow-lg">
      <div className="relative aspect-video w-full">
        {mentor?.avatar ? (
          <img src={mentor.avatar} alt={mentor.name} className={`h-full w-full object-cover ${state === 'speaking' ? 'scale-[1.02]' : ''} transition-transform`} />
        ) : (
          <div className="h-full w-full bg-slate-800" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/55 via-black/10 to-black/20" />
        <div className="absolute left-3 top-3 rounded-full bg-black/45 px-2 py-1 text-[10px] font-bold uppercase tracking-wider">Ligacao ao vivo</div>
        <div className="absolute right-3 top-3 rounded-full bg-black/45 px-2 py-1 text-[10px] font-bold uppercase">{stateLabel[state]}</div>
        <div className="absolute bottom-3 right-3 w-20 overflow-hidden rounded-xl border border-white/40 bg-black/40 p-1">
          {localVideoEnabled ? (
            <video
              ref={localVideoRef}
              autoPlay
              playsInline
              muted
              className={`h-12 w-full rounded-lg object-cover ${clientListening ? 'ring-2 ring-sky-300' : ''}`}
            />
          ) : (
            <div className={`h-12 rounded-lg bg-white/10 ${clientListening ? 'ring-2 ring-sky-300' : ''}`} />
          )}
          <p className="mt-1 text-center text-[10px] font-bold">Voce</p>
        </div>
      </div>

      <div className="space-y-2 p-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">Mentor ao vivo</p>
          <h2 className="mt-1 text-2xl font-black">{mentor?.name || 'Carregando mentor'}</h2>
          <p className="mt-1 text-sm text-slate-200">{mentor?.description || 'Preparando sua aula por voz...'}</p>
        </div>
        <div className={`relative inline-flex rounded-full bg-white/10 p-2 ${ringClass}`}>
          <div className="h-6 w-6 rounded-full bg-emerald-300/70" />
        </div>
        <div className="flex-1 space-y-2 text-xs text-slate-200">
          <p>Estilo: <span className="font-bold">{mentor?.speaking_style || '--'}</span></p>
          <p>Foco: <span className="font-bold">{mentor?.pedagogical_focus || '--'}</span></p>
          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onToggleMute} className="inline-flex items-center gap-1 rounded-lg border border-white/20 bg-white/10 px-2 py-1 text-xs font-semibold">
              {muted ? <VolumeX size={12} /> : <Volume2 size={12} />}
              {muted ? 'Mutado' : 'Audio'}
            </button>
            <button type="button" onClick={onReplay} className="inline-flex items-center gap-1 rounded-lg border border-white/20 bg-white/10 px-2 py-1 text-xs font-semibold">
              <Repeat2 size={12} />
              Repetir
            </button>
          </div>
          <div className="inline-flex items-center gap-1 rounded-lg border border-white/20 bg-white/10 px-2 py-1">
            {state === 'listening' ? <Mic size={12} /> : state === 'thinking' ? <Brain size={12} /> : <Volume2 size={12} />}
            Estado: {stateLabel[state]}
          </div>
        </div>
      </div>
    </section>
  );
}
