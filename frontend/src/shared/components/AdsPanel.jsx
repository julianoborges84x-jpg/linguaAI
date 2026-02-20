import React from "react";

const DEFAULT_COPY = {
  title: "Aprenda mais rápido com o PRO",
  body: "Desbloqueie fala, dialeto e sem anúncios."
};

export default function AdsPanel({ visible, placement = "dashboard", copy = DEFAULT_COPY }) {
  if (!visible) return null;

  return (
    <section className="glass-card rounded-2xl p-4 border border-amber-200/60 bg-amber-50/80 shadow-soft">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-amber-700">Anúncio</p>
          <h3 className="text-lg font-display text-amber-900">{copy.title}</h3>
          <p className="text-sm text-amber-800/80">{copy.body}</p>
        </div>
        <div
          className="rounded-xl bg-white/80 px-3 py-2 text-xs text-amber-700 border border-amber-200"
          data-ad-slot
          data-placement={placement}
          data-provider="google"
        >
          Slot preparado para Google Ads
        </div>
      </div>
    </section>
  );
}
