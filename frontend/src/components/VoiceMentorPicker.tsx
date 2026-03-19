import { CheckCircle2 } from 'lucide-react';

import { VoiceMentor } from '../types';

interface Props {
  mentors: VoiceMentor[];
  selectedMentorId: string;
  onSelect: (mentorId: string) => void;
}

export default function VoiceMentorPicker({ mentors, selectedMentorId, onSelect }: Props) {
  return (
    <div className="grid grid-cols-1 gap-3">
      {mentors.map((mentor) => {
        const selected = mentor.id === selectedMentorId;
        return (
          <button
            key={mentor.id}
            onClick={() => onSelect(mentor.id)}
            className={`rounded-xl border p-3 text-left transition-colors ${
              selected ? 'border-primary bg-primary/10' : 'border-slate-200 bg-white'
            }`}
          >
            <div className="flex items-start gap-3">
              <img src={mentor.avatar} alt={mentor.name} className="size-12 rounded-full object-cover border border-slate-200" />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-black">{mentor.name}</p>
                  {selected ? <CheckCircle2 size={16} className="text-primary" /> : null}
                </div>
                <p className="mt-1 text-xs text-slate-600">{mentor.description}</p>
                <p className="mt-1 text-[11px] text-slate-500">Estilo: {mentor.speaking_style}</p>
                <p className="text-[11px] text-slate-500">Foco: {mentor.pedagogical_focus}</p>
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}

