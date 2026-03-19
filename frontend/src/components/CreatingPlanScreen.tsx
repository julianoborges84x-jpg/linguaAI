import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, Languages, SignalHigh, PlaneTakeoff } from 'lucide-react';
import { UserProfile } from '../types';

interface Props {
  profile: UserProfile;
  onComplete: () => void;
}

export default function CreatingPlanScreen({ profile, onComplete }: Props) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("Iniciando...");

  const states = [
    { threshold: 20, label: "Analisando perfil..." },
    { threshold: 50, label: "Customizando lições..." },
    { threshold: 80, label: "Finalizando jornada..." },
    { threshold: 100, label: "Plano pronto!" }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        const next = prev + Math.floor(Math.random() * 5) + 2;
        return next > 100 ? 100 : next;
      });
    }, 150);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const currentState = states.find(s => progress <= s.threshold) || states[states.length - 1];
    setStatus(currentState.label);
  }, [progress]);

  const circumference = 2 * Math.PI * 88;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className="min-h-screen flex flex-col bg-background-light">
      <header className="flex items-center justify-between p-4 bg-white border-b border-slate-200">
        <ArrowLeft className="text-slate-900 cursor-pointer" size={24} />
        <h2 className="text-lg font-bold tracking-tight">Mentor Língua</h2>
        <div className="flex items-center gap-1 bg-primary/10 text-primary px-2 py-1 rounded-full border border-primary/20">
          <span className="text-[10px] font-bold">API Connected</span>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-8 text-center max-w-md mx-auto w-full">
        <h1 className="text-3xl font-bold leading-tight mb-4 text-slate-900">
          Criando seu plano personalizado...
        </h1>
        <p className="text-slate-500 mb-10">
          Estamos analisando suas preferências para montar a melhor jornada de aprendizado.
        </p>

        <div className="relative flex items-center justify-center mb-12">
          <svg className="w-48 h-48 transform -rotate-90">
            <circle className="text-slate-200" cx="96" cy="96" fill="transparent" r="88" stroke="currentColor" strokeWidth="12" />
            <circle 
              className="text-primary transition-all duration-500" 
              cx="96" cy="96" fill="transparent" r="88" 
              stroke="currentColor" strokeWidth="12" 
              strokeDasharray={circumference} 
              strokeDashoffset={offset} 
              strokeLinecap="round" 
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-extrabold text-slate-900">{progress}%</span>
            <span className="text-sm font-medium text-slate-500">{status}</span>
          </div>
        </div>

        <div className="w-full bg-white rounded-xl p-6 shadow-sm border border-slate-100 mb-8">
          <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">
            Resumo do seu perfil
          </h4>
          <div className="flex flex-wrap justify-center gap-2">
            <div className="flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full border border-primary/20">
              <Languages size={18} />
              <span className="text-sm font-semibold capitalize">{profile.language}</span>
            </div>
            <div className="flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full border border-primary/20">
              <SignalHigh size={18} />
              <span className="text-sm font-semibold capitalize">{profile.level}</span>
            </div>
            <div className="flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full border border-primary/20">
              <PlaneTakeoff size={18} />
              <span className="text-sm font-semibold capitalize">{profile.goal}</span>
            </div>
          </div>
        </div>

        <div className="w-full mt-auto space-y-4">
          <button 
            onClick={onComplete}
            disabled={progress < 100}
            className={`w-full bg-primary text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all ${
              progress < 100 ? 'opacity-50 pointer-events-none' : 'hover:bg-primary/90'
            }`}
          >
            Ver meu plano
          </button>
          <p className="text-xs text-slate-400">
            Isso levará apenas alguns segundos.
          </p>
        </div>
      </main>
    </div>
  );
}
