import { ArrowLeft, Bell, Globe2, LogOut, Save, SlidersHorizontal, Volume2 } from 'lucide-react';
import { useEffect, useState } from 'react';

const SETTINGS_KEY = 'lingua_settings';

interface Props {
  onBack: () => void;
  onLogout: () => void;
}

type SettingsState = {
  language: string;
  voiceEnabled: boolean;
  volume: number;
  speechRate: number;
  defaultMentor: string;
  notificationsEnabled: boolean;
};

const defaultState: SettingsState = {
  language: 'en',
  voiceEnabled: true,
  volume: 80,
  speechRate: 100,
  defaultMentor: 'clara',
  notificationsEnabled: true,
};

export default function SettingsScreen({ onBack, onLogout }: Props) {
  const [state, setState] = useState<SettingsState>(defaultState);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw) as Partial<SettingsState>;
      setState({ ...defaultState, ...parsed });
    } catch {
      setState(defaultState);
    }
  }, []);

  const save = () => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(state));
    setSaved(true);
    setTimeout(() => setSaved(false), 1800);
  };

  return (
    <div className="min-h-screen bg-background-light pb-10">
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-md items-center justify-between px-4">
          <button type="button" onClick={onBack} className="rounded-full p-2 hover:bg-slate-100" aria-label="Voltar">
            <ArrowLeft size={20} />
          </button>
          <p className="text-sm font-black tracking-wide">Configuracoes</p>
          <button type="button" onClick={save} className="rounded-full p-2 hover:bg-slate-100" aria-label="Salvar configuracoes">
            <Save size={18} />
          </button>
        </div>
      </header>

      <main className="mx-auto mt-5 max-w-md space-y-4 px-4">
        {saved ? <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">Configuracoes salvas.</div> : null}

        <section className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
          <p className="text-sm font-black">Idioma</p>
          <div className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500"><Globe2 size={14} /> Idioma preferido</div>
          <select
            value={state.language}
            onChange={(e) => setState((prev) => ({ ...prev, language: e.target.value }))}
            className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="en">English</option>
            <option value="es">Espanol</option>
            <option value="fr">Francais</option>
            <option value="it">Italiano</option>
          </select>
        </section>

        <section className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
          <p className="text-sm font-black">Voz e mentor</p>
          <label className="flex items-center justify-between text-sm">
            Voz ativa
            <input type="checkbox" checked={state.voiceEnabled} onChange={(e) => setState((prev) => ({ ...prev, voiceEnabled: e.target.checked }))} />
          </label>

          <label className="block text-sm">
            <div className="mb-1 inline-flex items-center gap-2"><Volume2 size={14} /> Volume ({state.volume}%)</div>
            <input
              type="range"
              min={0}
              max={100}
              value={state.volume}
              onChange={(e) => setState((prev) => ({ ...prev, volume: Number(e.target.value) }))}
              className="w-full"
            />
          </label>

          <label className="block text-sm">
            <div className="mb-1 inline-flex items-center gap-2"><SlidersHorizontal size={14} /> Velocidade ({state.speechRate}%)</div>
            <input
              type="range"
              min={60}
              max={140}
              value={state.speechRate}
              onChange={(e) => setState((prev) => ({ ...prev, speechRate: Number(e.target.value) }))}
              className="w-full"
            />
          </label>

          <label className="block text-sm">
            Mentor padrao
            <select
              value={state.defaultMentor}
              onChange={(e) => setState((prev) => ({ ...prev, defaultMentor: e.target.value }))}
              className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2"
            >
              <option value="clara">Clara</option>
              <option value="maya">Maya</option>
              <option value="ethan">Ethan</option>
              <option value="noah">Noah</option>
            </select>
          </label>
        </section>

        <section className="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
          <p className="text-sm font-black">Notificacoes</p>
          <label className="flex items-center justify-between text-sm">
            <span className="inline-flex items-center gap-2"><Bell size={14} /> Ativar notificacoes</span>
            <input
              type="checkbox"
              checked={state.notificationsEnabled}
              onChange={(e) => setState((prev) => ({ ...prev, notificationsEnabled: e.target.checked }))}
            />
          </label>
        </section>

        <button type="button" onClick={onLogout} className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-bold text-red-700">
          <LogOut size={16} />
          Sair da conta
        </button>
      </main>
    </div>
  );
}
