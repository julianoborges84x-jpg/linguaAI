import React from "react";
import { Link } from "react-router-dom";
import Button from "../ui/Button.jsx";

export default function NavBar({ user, onLogout }) {
  return (
    <nav className="flex flex-col gap-4 py-6 md:flex-row md:items-center md:justify-between">
      <Link to="/dashboard" className="font-display text-xl">
        MentorLingua
      </Link>
      <div className="flex flex-wrap items-center gap-3">
        {user && <span className="text-sm text-slate-600">{user.name} · {user.plan}</span>}
        <Link to="/chat" className="text-sm text-slate-600 hover:text-ink">
          Chat
        </Link>
        <Button variant="secondary" onClick={onLogout}>
          Sair
        </Button>
      </div>
    </nav>
  );
}
