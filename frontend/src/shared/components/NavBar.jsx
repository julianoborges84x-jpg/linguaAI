import React from "react";
import { Link } from "react-router-dom";
import Button from "../ui/Button.jsx";

export default function NavBar({ user, onLogout }) {
  const planClass =
    user?.plan === "PRO"
      ? "bg-amber-100 text-amber-800 border border-amber-300"
      : "bg-slate-100 text-slate-700 border border-slate-200";

  return (
    <nav className="flex flex-col gap-4 py-6 md:flex-row md:items-center md:justify-between">
      <Link to="/dashboard" className="font-display text-xl">
        MentorLingua
      </Link>
      <div className="flex flex-wrap items-center gap-3">
        {user && (
          <span className="text-sm text-slate-600">
            {user.name}
            {" "}
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${planClass}`}>
              {user.plan}
            </span>
          </span>
        )}
        <Link to="/chat" className="text-sm text-slate-600 hover:text-ink">
          Chat
        </Link>
        <Link to="/topics" className="text-sm text-slate-600 hover:text-ink">
          Tópicos
        </Link>
        <Link to="/vocabulary" className="text-sm text-slate-600 hover:text-ink">
          Vocabulário
        </Link>
        <Link to="/progress" className="text-sm text-slate-600 hover:text-ink">
          Progresso
        </Link>
        <Button variant="secondary" onClick={onLogout}>
          Sair
        </Button>
      </div>
    </nav>
  );
}
