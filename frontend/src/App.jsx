import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Login from "./features/auth/Login.jsx";
import Register from "./features/auth/Register.jsx";
import Dashboard from "./features/dashboard/Dashboard.jsx";
import Chat from "./features/chat/Chat.jsx";
import Topics from "./features/topics/Topics.jsx";
import Vocabulary from "./features/vocabulary/Vocabulary.jsx";
import Progress from "./features/progress/Progress.jsx";
import Onboarding from "./features/onboarding/Onboarding.jsx";
import FakeCheckout from "./features/billing/FakeCheckout.jsx";
import LandingPage from "./features/landing/LandingPage.jsx";
import TermsPage from "./features/legal/TermsPage.jsx";
import PrivacyPage from "./features/legal/PrivacyPage.jsx";
import { useAuth } from "./hooks/useAuth.jsx";

function hasCompletedOnboarding(user) {
  return Boolean(user?.onboarding_completed || user?.target_language || user?.target_language_code);
}

function RequireAuthenticated({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  return user ? children : <Navigate to="/login" replace />;
}

function RequireOnboardingComplete({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (!hasCompletedOnboarding(user)) return <Navigate to="/onboarding" replace />;
  return children;
}

function RequireOnboardingPending({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (hasCompletedOnboarding(user)) return <Navigate to="/dashboard" replace />;
  return children;
}

export default function App() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/termos" element={<TermsPage />} />
      <Route path="/privacidade" element={<PrivacyPage />} />
      <Route
        path="/onboarding"
        element={
          <RequireOnboardingPending>
            <Onboarding />
          </RequireOnboardingPending>
        }
      />
      <Route
        path="/dashboard"
        element={
          <RequireOnboardingComplete>
            <Dashboard />
          </RequireOnboardingComplete>
        }
      />
      <Route
        path="/chat"
        element={
          <RequireOnboardingComplete>
            <Chat />
          </RequireOnboardingComplete>
        }
      />
      <Route
        path="/topics"
        element={
          <RequireOnboardingComplete>
            <Topics />
          </RequireOnboardingComplete>
        }
      />
      <Route
        path="/vocabulary"
        element={
          <RequireOnboardingComplete>
            <Vocabulary />
          </RequireOnboardingComplete>
        }
      />
      <Route
        path="/vocab"
        element={
          <RequireOnboardingComplete>
            <Vocabulary />
          </RequireOnboardingComplete>
        }
      />
      <Route
        path="/progress"
        element={
          <RequireOnboardingComplete>
            <Progress />
          </RequireOnboardingComplete>
        }
      />
      <Route path="/billing/fake-checkout" element={<FakeCheckout />} />
      <Route path="*" element={<Navigate to={user ? "/dashboard" : "/"} replace />} />
    </Routes>
  );
}
