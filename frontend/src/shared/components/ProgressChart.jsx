import React from "react";

export default function ProgressChart({ data = [] }) {
  if (!data.length) return null;
  const max = Math.max(...data.map((d) => d.value), 1);
  const points = data
    .map((d, idx) => {
      const x = (idx / (data.length - 1)) * 280;
      const y = 80 - (d.value / max) * 70;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg viewBox="0 0 280 90" className="w-full h-24">
      <polyline
        points={points}
        fill="none"
        stroke="#1f8ef1"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {data.map((d, idx) => {
        const x = (idx / (data.length - 1)) * 280;
        const y = 80 - (d.value / max) * 70;
        return (
          <circle key={d.label} cx={x} cy={y} r="4" fill="#0f172a" />
        );
      })}
    </svg>
  );
}
