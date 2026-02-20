import React from "react";

export default function StreakBadge({ streak }) {
  if (streak == null) return null;
  return (
    <div className="glass-card rounded-2xl p-4 shadow-soft flex items-center justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-amber-500">Streak</p>
        <p className="font-display text-2xl mt-2">{streak} dias seguidos</p>
      </div>
      <div className="h-12 w-12 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center font-display">
        {streak}
      </div>
    </div>
  );
}
