import React from "react";

export default function DailyMessage({ message }) {
  if (!message) return null;
  return (
    <section className="glass-card rounded-2xl p-6 shadow-soft">
      <p className="text-xs uppercase tracking-[0.2em] text-moss">Passagem do dia</p>
      <h3 className="font-display text-2xl mt-2">{message.reference}</h3>
      <p className="text-slate-700 mt-3 leading-relaxed">{message.text}</p>
    </section>
  );
}
