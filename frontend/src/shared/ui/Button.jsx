import React from "react";

export default function Button({ children, variant = "primary", className = "", ...props }) {
  const base = "rounded-xl px-4 py-2 text-sm font-medium transition";
  const styles = {
    primary: "bg-ink text-white hover:bg-slate-900",
    secondary: "border border-slate-200 hover:bg-white",
    ghost: "text-slate-600 hover:text-ink"
  };
  return (
    <button className={`${base} ${styles[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
