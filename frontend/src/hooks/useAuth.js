import { useEffect, useState } from "react";
import { getCurrentUser } from "../services/userService.js";
import { getToken, logout as clearSession } from "../services/authService.js";

export function useAuth() {
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

  return { user, setUser, loading, logout };
}
