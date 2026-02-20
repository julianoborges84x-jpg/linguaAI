import React from "react";

export default function Card({ children, className = "" }) {
  return <div className={`glass-card rounded-2xl p-6 shadow-soft ${className}`}>{children}</div>;
}
