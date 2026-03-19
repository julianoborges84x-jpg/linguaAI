import React from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, Baby, MessageSquare, BookOpen, GraduationCap } from 'lucide-react';

interface Props {
  onBack: () => void;
  onNext: (level: string) => void;
}

const levels = [
  { id: 'iniciante', title: 'Iniciante', desc: 'Estou começando do zero agora', icon: Baby },
  { id: 'intermediario', title: 'Intermediário', desc: 'Consigo manter conversas básicas', icon: MessageSquare },
  { id: 'avancado', title: 'Avançado', desc: 'Tenho boa compreensão e fala', icon: BookOpen },
  { id: 'fluente', title: 'Fluente', desc: 'Domínio total e natural do idioma', icon: GraduationCap },
];

export default function ProficiencyLevelScreen({ onBack, onNext }: Props) {
  const [selected, setSelected] = React.useState<string | null>(null);

  return (
    <div className="min-h-screen flex flex-col bg-white">
      <div className="flex items-center p-4 pb-2 justify-between">
        <button onClick={onBack} className="text-slate-900 flex size-12 items-center justify-start">
          <ArrowLeft size={24} />
        </button>
        <h2 className="text-slate-900 text-lg font-bold flex-1 text-center pr-12">Mentor Língua</h2>
      </div>

      <div className="flex flex-col gap-3 p-4">
        <div className="flex justify-between items-end">
          <p className="text-slate-900 text-base font-semibold">Etapa 2 de 4</p>
          <p className="text-primary text-sm font-bold">50%</p>
        </div>
        <div className="rounded-full bg-slate-100 h-2 w-full overflow-hidden">
          <div className="h-full rounded-full bg-primary w-[50%]"></div>
        </div>
      </div>

      <div className="px-4 pt-6 pb-2">
        <h3 className="text-slate-900 tracking-tight text-2xl font-extrabold">Qual seu nível atual?</h3>
        <p className="text-slate-500 text-sm mt-1">Isso nos ajuda a personalizar seu plano de estudos.</p>
      </div>

      <div className="flex flex-col gap-4 p-4 flex-1">
        {levels.map((level) => (
          <label 
            key={level.id}
            className={`group flex items-center gap-4 rounded-xl border-2 p-4 cursor-pointer transition-all ${
              selected === level.id ? 'border-primary bg-primary/5' : 'border-slate-100 hover:border-primary/50'
            }`}
          >
            <div className="flex size-12 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <level.icon size={24} />
            </div>
            <div className="flex grow flex-col">
              <p className="text-slate-900 text-base font-bold">{level.title}</p>
              <p className="text-slate-500 text-sm">{level.desc}</p>
            </div>
            <input 
              type="radio" 
              name="proficiency" 
              checked={selected === level.id}
              onChange={() => setSelected(level.id)}
              className="h-5 w-5 border-2 border-slate-300 text-primary focus:ring-primary focus:ring-offset-0" 
            />
          </label>
        ))}
      </div>

      <div className="px-4 py-6 mt-auto">
        <button 
          disabled={!selected}
          onClick={() => selected && onNext(selected)}
          className="flex w-full items-center justify-center rounded-xl h-14 px-5 bg-primary text-white text-base font-bold shadow-lg shadow-primary/25 active:scale-[0.98] transition-all disabled:opacity-50"
        >
          <span>Continuar</span>
        </button>
      </div>
    </div>
  );
}
