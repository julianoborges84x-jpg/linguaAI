import React from "react";

export default function HistoryList({ items = [] }) {
  return (
    <div className="space-y-3">
      {items.length === 0 && (
        <p className="text-sm text-slate-500">Nenhuma conversa recente.</p>
      )}
      {items.map((item) => (
        <div key={item.id} className="rounded-2xl border border-slate-200 p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
            {item.feature} · {new Date(item.created_at).toLocaleString()}
          </p>
          <p className="mt-2 text-sm text-slate-600">{item.preview}</p>
        </div>
      ))}
    </div>
  );
}
