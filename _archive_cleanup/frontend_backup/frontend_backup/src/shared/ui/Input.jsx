import React from "react";

export default function Input({ label, ...props }) {
  return (
    <label className="block text-sm text-slate-600">
      {label}
      <input
        className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-lagoon/40"
        {...props}
      />
    </label>
  );
}
