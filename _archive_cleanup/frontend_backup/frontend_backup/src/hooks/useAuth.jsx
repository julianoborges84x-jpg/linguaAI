import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getCurrentUser } from "../services/userService.js";
import { getToken, logout as clearSession } from "../services/authService.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        if (!getToken()) {
          setUser(null);
          setLoading(false);
          return;
        }
        const profile = await getCurrentUser();
        setUser(profile);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const logout = () => {
    clearSession();
    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      setUser,
      loading,
      logout,
      plan: user?.plan || "FREE",
      isPro: user?.plan === "PRO",
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
