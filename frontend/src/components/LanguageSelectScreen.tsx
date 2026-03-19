import React from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, ArrowRight, CheckCircle2 } from 'lucide-react';

interface Props {
  onBack: () => void;
  onNext: (language: string) => void;
}

const languages = [
  { id: 'ingles', name: 'Inglês', flag: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAYbkM0y0G5CfYp-Iqk-mFt-G4Pkg35Cz8emPUOa7Nj0bogLFPe0KhZ1ud8xJnjYMEa0i2306Abwfp2ExSKiaaF5tYQ36HV0h5ARDjVP65R8ZwsXD6vtNGjro7QGn8reyMLcDuh3_QAeldMmlEeGgVzQ7lYyZMi313r90egSafkgrRTt1N0CrZdN3Zi_6Sx0yw-uCH8QVnqNkfKvgC0gLDrVknHooJPceWexx3NWwkIZoZPr47OsBOoWKLrE3zH1V8XHTVX10om0LQu' },
  { id: 'espanhol', name: 'Espanhol', flag: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCTRylLCc6Rc-ZtuUxGG9dp2sXpahFDIY5OsBxXPE2b98OIo7FZ5Czfd3gGThlipJN17q95hKHjwF3nRh1fG1TQLC8ePdcbPUaIGwfehhPi3Ho_1kQodX7x8plwfiZ1dQ7ucVPtecanZzRUbfz_nS_k8RZ9XatZ_amj3SlVZAFGB4RpI0zgvTIHglXA4XkVp58WV8I0She4vpgP8kgq-ZTnPBcuL6bCnkTbNa-YPizkC0XiCdIefJOlrIgOJAgAhLxYPlZ0Nq2Gy6Me' },
  { id: 'frances', name: 'Francês', flag: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBcgW4F9h4JjmzgNcDK0wBMq2L0JuMGBn8TjxKk7Z4zF7HsaonwRqIPU2MA7Uoh_vyxR-uAfIyulEyulPao58YnHfVRTcvr3mnJfTXu9MNPMG-9o9PIsK0P6kvqKGfPXsa-kigSl0YvEUBrFCGqDJZJaUrj32EpvrxaofL1Vm_snSS5ZTO151f9D7S5UJ5i9puMYMBXH8STKRroElXjiDvUTaI1lI5I4sES9LsKDuVKkvMpov1LkB8LGeUFethyDFvZrs05ryRvbR-8' },
  { id: 'alemao', name: 'Alemão', flag: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC9wrxRHBaL8v5Qvz0e8uWBRyMjnK0qQL3GtFcCSZ8Y4CvSaNw2tEedwH4rjM3MAJaTDPbu5B27eAkGDo5o1RcNJjfQSWkDa_zKNM48awLZ4T5S4Rfp5jfpqn-TG7lu1elyc5J2y-LCbcyBk9XjwZD11ifT91W-Z8r4fX3WAsHMsFabNI7pazXhf7syHW7_kYlNHDM9n_yXKL4uc7CFNoVue_0EAmv8oxw1WuoFrvjUDOQxMUQnt56vo-QDR4QaN-Iol0fqvUj_5gqT' },
  { id: 'italiano', name: 'Italiano', flag: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCgvSmoHWdLs68n24aPA50dKt1qwoIxB-BYIbBh3fBZruj4LXTZlzLqI-zQT4TFs4lhpe2_Brqq_llVGzwcuapvXhEoq6VYhajOYP1giqSvr__7x-jp4re-sfZLLPAwq9QmVaSfVkzenICDCwcFo40fq6GoLjWs6G-3Yz1Kqobvw4cIC51KV3hKzupRy79EzPzcX9bzqrA__ZQZX1o2YRh9wXeF5xiZhzSyLI1xwF43cw_40aux5pRNAifqSW6OiJPLgGtekkcxI9w0' },
];

export default function LanguageSelectScreen({ onBack, onNext }: Props) {
  const [selected, setSelected] = React.useState<string | null>(null);

  return (
    <div className="min-h-screen flex flex-col bg-background-light">
      <nav className="flex items-center p-4 pb-2 sticky top-0 z-10 bg-background-light">
        <button 
          onClick={onBack}
          className="text-slate-900 flex size-10 items-center justify-center cursor-pointer hover:bg-slate-200 rounded-full transition-colors"
        >
          <ArrowLeft size={24} />
        </button>
        <h2 className="text-slate-900 text-lg font-bold flex-1 text-center pr-10">Mentor Língua</h2>
      </nav>

      <div className="flex flex-col gap-3 p-6">
        <div className="flex justify-between items-center">
          <p className="text-slate-700 text-sm font-semibold uppercase tracking-wider">Progresso da configuração</p>
          <p className="text-primary text-sm font-bold">2 de 5</p>
        </div>
        <div className="rounded-full bg-slate-200 h-2.5 overflow-hidden">
          <div className="h-full rounded-full bg-primary w-[40%]"></div>
        </div>
      </div>

      <header className="px-6 py-4">
        <h1 className="text-slate-900 tracking-tight text-3xl font-extrabold leading-tight text-center">
          Qual idioma você quer aprender?
        </h1>
        <p className="text-slate-500 text-center mt-2 text-base">Escolha o seu próximo desafio linguístico</p>
      </header>

      <main className="grid grid-cols-2 gap-4 p-6 sm:grid-cols-3 lg:grid-cols-5 flex-1">
        {languages.map((lang) => (
          <motion.div
            key={lang.id}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelected(lang.id)}
            className={`group relative flex flex-col items-center gap-4 rounded-xl bg-white p-4 shadow-sm border transition-all cursor-pointer ${
              selected === lang.id ? 'border-primary ring-2 ring-primary/20' : 'border-slate-100 hover:border-primary/50'
            }`}
          >
            <div className="h-16 w-16 rounded-full overflow-hidden bg-slate-100 flex items-center justify-center">
              <img 
                src={lang.flag} 
                alt={lang.name} 
                className="w-full h-full object-cover"
                referrerPolicy="no-referrer"
              />
            </div>
            <span className="text-slate-900 font-bold text-lg">{lang.name}</span>
            {selected === lang.id && (
              <div className="absolute top-3 right-3">
                <CheckCircle2 className="text-primary" size={20} />
              </div>
            )}
          </motion.div>
        ))}
      </main>

      <footer className="p-6 border-t border-slate-200 bg-white">
        <div className="max-w-md mx-auto">
          <button 
            disabled={!selected}
            onClick={() => selected && onNext(selected)}
            className="w-full flex items-center justify-center rounded-xl h-14 px-5 bg-primary text-white text-base font-bold shadow-lg shadow-primary/25 hover:bg-primary/90 transition-all active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none"
          >
            <span>Continuar</span>
            <ArrowRight size={20} className="ml-2" />
          </button>
          <p className="text-slate-400 text-xs text-center mt-4">Você poderá adicionar mais idiomas depois</p>
        </div>
      </footer>
    </div>
  );
}
