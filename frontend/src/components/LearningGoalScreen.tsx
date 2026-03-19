import React from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, PlaneTakeoff, Briefcase, Globe, Heart, GraduationCap } from 'lucide-react';

interface Props {
  onBack: () => void;
  onNext: (goal: string) => void;
}

const goals = [
  { id: 'viagens', title: 'Viagens', desc: 'Explore o mundo sem barreiras', icon: PlaneTakeoff },
  { id: 'carreira', title: 'Carreira', desc: 'Impulsione seu currículo e ganhos', icon: Briefcase },
  { id: 'cultura', title: 'Cultura', desc: 'Conheça novas gentes e costumes', icon: Globe },
  { id: 'hobby', title: 'Hobby', desc: 'Aprenda por puro prazer', icon: Heart },
  { id: 'estudos', title: 'Estudos', desc: 'Melhore suas notas acadêmicas', icon: GraduationCap },
];

export default function LearningGoalScreen({ onBack, onNext }: Props) {
  const [selected, setSelected] = React.useState<string | null>(null);

  return (
    <div className="min-h-screen flex flex-col bg-background-light">
      <header className="flex items-center bg-white p-4 pb-2 justify-between sticky top-0 z-10 backdrop-blur-md">
        <button onClick={onBack} className="text-primary flex size-12 items-center cursor-pointer hover:bg-primary/10 rounded-full justify-center transition-colors">
          <ArrowLeft size={24} />
        </button>
        <h2 className="text-slate-900 text-lg font-bold flex-1 text-center pr-12">Mentor Língua</h2>
      </header>

      <div className="flex flex-col gap-3 p-6">
        <div className="flex gap-6 justify-between items-center">
          <p className="text-slate-900 text-base font-semibold">Meta de Aprendizado</p>
          <p className="text-primary text-sm font-bold bg-primary/10 px-3 py-1 rounded-full">Etapa 3 de 4</p>
        </div>
        <div className="rounded-full bg-slate-200 h-3 overflow-hidden">
          <div className="h-full rounded-full bg-primary w-[75%]"></div>
        </div>
      </div>

      <div className="px-6 py-4">
        <h3 className="text-slate-900 tracking-tight text-2xl font-extrabold text-center">Por que você quer aprender?</h3>
        <p className="text-slate-500 text-center mt-2 text-sm">Isso nos ajuda a personalizar sua experiência.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-6 flex-1">
        {goals.map((goal) => (
          <button 
            key={goal.id}
            onClick={() => setSelected(goal.id)}
            className={`flex flex-1 gap-4 rounded-xl border-2 p-5 flex-col items-start transition-all text-left group ${
              selected === goal.id ? 'border-primary bg-primary/5' : 'border-slate-200 bg-white hover:border-primary/50'
            }`}
          >
            <div className={`p-3 rounded-lg transition-colors ${
              selected === goal.id ? 'bg-primary text-white' : 'bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white'
            }`}>
              <goal.icon size={24} />
            </div>
            <div className="flex flex-col gap-1">
              <h4 className="text-slate-900 text-lg font-bold">{goal.title}</h4>
              <p className="text-slate-500 text-sm font-normal">{goal.desc}</p>
            </div>
          </button>
        ))}
      </div>

      <div className="mt-auto p-6 bg-white border-t border-slate-200 shadow-2xl">
        <button 
          disabled={!selected}
          onClick={() => selected && onNext(selected)}
          className="w-full flex items-center justify-center rounded-xl h-14 px-5 bg-primary text-white text-lg font-bold transition-transform active:scale-[0.98] disabled:opacity-50"
        >
          <span>Continuar</span>
        </button>
      </div>
    </div>
  );
}
