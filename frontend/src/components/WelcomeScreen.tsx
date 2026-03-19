import React from 'react';
import { motion } from 'motion/react';
import { Languages, Brain, MessageSquare, ArrowRight, Verified } from 'lucide-react';

interface Props {
  onStart: () => void;
}

export default function WelcomeScreen({ onStart }: Props) {
  return (
    <div className="min-h-screen flex flex-col bg-pattern">
      <header className="sticky top-0 z-50 w-full bg-white/80 backdrop-blur-md border-b border-primary/10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary text-white p-2 rounded-lg flex items-center justify-center shadow-sm">
              <Languages size={24} />
            </div>
            <span className="text-lg font-bold tracking-tight">Mentor Língua</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 border border-emerald-200 rounded-full">
              <Verified size={16} className="text-emerald-600" />
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700">Validated & API Connected</span>
            </div>
            <button
              type="button"
              disabled
              aria-label="Configuracoes em breve"
              title="Configuracoes em breve"
              className="text-slate-400 p-2 rounded-full transition-colors cursor-not-allowed"
            >
              <span className="material-symbols-outlined">settings</span>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-12 relative overflow-hidden">
        <div className="absolute top-20 -left-20 w-64 h-64 bg-primary/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 -right-20 w-80 h-80 bg-primary/5 rounded-full blur-3xl"></div>
        
        <div className="w-full max-w-lg text-center relative z-10">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-10 animate-bounce-subtle"
          >
            <div className="relative inline-block">
              <div className="absolute inset-0 bg-primary/20 rounded-full scale-110 blur-xl opacity-60"></div>
              <div className="relative w-48 h-48 md:w-64 md:h-64 mx-auto bg-white rounded-full shadow-2xl flex items-center justify-center border-4 border-primary/10 overflow-hidden">
                <img 
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuCts0Af9aIphu5WaSFEMgJ72ErBIG6gnH-Yi8eesfVJOf0vTjwFt4P8-mVTTr6QCTP8bi-0KACUtJg9CSOgUAcbmFNoK0rftAail4sIK6UnhEg-36JzjqqtUmHWO-2Y3nsaeRoR2YKZ3ui1DcBI89-V9gHT5GVxD_Kr6IxIPcZk2vgSIwNTvoxMPNKYj0RSsebi4Z9NgCP09tv9v6dFnyGyutmf_PTY-HREgfuDzDz8Q9xjokNAsLrs09fWjSzzNk5SfBV_Jb3d2FJL" 
                  alt="Friendly AI robot tutor"
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
              </div>
              <div className="absolute bottom-4 right-4 bg-primary text-white p-3 rounded-full shadow-lg border-4 border-white">
                <Languages size={24} />
              </div>
            </div>
          </motion.div>

          <div className="space-y-4">
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900">
              Bem-vindo ao <span className="text-primary">Mentor Língua</span>
            </h1>
            <p className="text-lg md:text-xl text-slate-600 max-w-md mx-auto leading-relaxed">
              Seu tutor de idiomas inteligente, agora totalmente conectado à rede global. Aprenda com feedback em tempo real.
            </p>
          </div>

          <div className="mt-12 space-y-4">
            <button 
              onClick={onStart}
              className="w-full sm:w-80 h-14 bg-primary hover:bg-blue-600 text-white text-lg font-bold rounded-xl shadow-lg shadow-primary/30 transition-all active:scale-[0.98] flex items-center justify-center gap-2 mx-auto"
            >
              <span>Começar Jornada</span>
              <ArrowRight size={20} />
            </button>
            <p className="text-sm text-slate-500 font-medium">
              Seu tutor de idiomas inteligente, agora totalmente conectado à rede global.
            </p>
          </div>
        </div>

        <div className="mt-20 grid grid-cols-2 md:grid-cols-3 gap-4 w-full max-w-4xl">
          <div className="p-4 bg-white/50 backdrop-blur-sm rounded-xl border border-primary/5 flex flex-col items-center text-center relative hover:border-primary/20 transition-colors">
            <div className="absolute top-2 right-2 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
              <span className="text-[8px] text-emerald-600 font-bold uppercase">Live</span>
            </div>
            <Brain className="text-primary mb-2" size={24} />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">IA Adaptativa</span>
          </div>
          <div className="p-4 bg-white/50 backdrop-blur-sm rounded-xl border border-primary/5 flex flex-col items-center text-center relative hover:border-primary/20 transition-colors">
            <div className="absolute top-2 right-2 flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
              <span className="text-[8px] text-emerald-600 font-bold uppercase">Live</span>
            </div>
            <MessageSquare className="text-primary mb-2" size={24} />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Conversa Real</span>
          </div>
        </div>
      </main>

      <footer className="py-6 px-4 text-center">
        <div className="flex items-center justify-center gap-6 mb-4">
          <div className="flex -space-x-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="w-8 h-8 rounded-full border-2 border-white bg-slate-200 overflow-hidden">
                <img 
                  src={`https://picsum.photos/seed/student${i}/100/100`} 
                  alt="Student" 
                  className="w-full h-full object-cover"
                  referrerPolicy="no-referrer"
                />
              </div>
            ))}
          </div>
          <span className="text-sm font-medium text-slate-600">+10k alunos aprendendo hoje</span>
        </div>
      </footer>
    </div>
  );
}
