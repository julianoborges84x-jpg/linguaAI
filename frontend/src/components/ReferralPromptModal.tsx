import { Gift, Send, Share2, X } from 'lucide-react';

interface Props {
  open: boolean;
  trigger: 'daily_challenge_completed' | 'xp_gained' | 'level_up';
  onClose: () => void;
  onCopy: () => Promise<void> | void;
  onSend: () => Promise<void> | void;
  onOpenReferral: () => void;
}

const triggerTitle: Record<Props['trigger'], string> = {
  daily_challenge_completed: 'Desafio concluido! Aproveite seu momento.',
  xp_gained: 'Voce ganhou XP! Continue acelerando.',
  level_up: 'Level up desbloqueado! Hora de crescer ainda mais.',
};

export default function ReferralPromptModal({ open, trigger, onClose, onCopy, onSend, onOpenReferral }: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[70] flex items-end justify-center bg-slate-900/50 p-4 sm:items-center">
      <div className="w-full max-w-md rounded-2xl border border-primary/20 bg-white p-5 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-black uppercase tracking-[0.15em] text-primary">Referral Boost</p>
            <h3 className="mt-1 text-lg font-black text-slate-900">🚀 Voce foi bem! Convide um amigo e ganhe bonus exclusivo</h3>
          </div>
          <button onClick={onClose} className="rounded-full p-2 text-slate-500 hover:bg-slate-100">
            <X size={16} />
          </button>
        </div>

        <p className="mt-2 text-sm text-slate-700">{triggerTitle[trigger]}</p>
        <p className="mt-1 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-bold text-amber-700">
          🔥 Convide hoje e ganhe bonus dobrado
        </p>

        <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
          <div className="rounded-lg bg-slate-50 p-3">
            <p className="text-slate-500">Recompensa</p>
            <p className="mt-1 font-black text-slate-900">+XP para ambos</p>
          </div>
          <div className="rounded-lg bg-slate-50 p-3">
            <p className="text-slate-500">Extra</p>
            <p className="mt-1 font-black text-slate-900">+1 dia PRO</p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2">
          <button onClick={onCopy} className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-3 text-sm font-bold text-white">
            <Share2 size={16} />
            Copiar link
          </button>
          <button onClick={onSend} className="inline-flex items-center justify-center gap-2 rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm font-bold text-primary">
            <Send size={16} />
            Enviar convite
          </button>
        </div>

        <button onClick={onOpenReferral} className="mt-3 inline-flex items-center gap-2 text-xs font-bold text-primary">
          <Gift size={14} />
          Ver painel completo de indicacoes
        </button>
      </div>
    </div>
  );
}

