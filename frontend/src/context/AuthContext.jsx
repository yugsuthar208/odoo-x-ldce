import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authService } from "../services/authService";
import { TOKEN_KEY } from "../services/apiClient";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [token, setToken]     = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true);

  /* On mount: if token exists, fetch profile */
  useEffect(() => {
    let isMounted = true;
    if (token) {
      authService.getProfile()
        .then((res) => {
          if (isMounted) setUser(res.data);
        })
        .catch(() => {
          localStorage.removeItem(TOKEN_KEY);
          if (isMounted) setToken(null);
        })
        .finally(() => {
          if (isMounted) setLoading(false);
        });
    } else {
      if (isMounted) setLoading(false);
    }
    return () => { isMounted = false; };
  }, [token]);

  const login = useCallback(async (email, password) => {
    const res = await authService.login(email, password);
    const t = res.data?.access_token;
    if (!t) throw new Error("No token received");
    localStorage.setItem(TOKEN_KEY, t);
    setToken(t);
    const profile = await authService.getProfile();
    setUser(profile.data);
    return profile.data;
  }, []);

  const signup = useCallback(async (payload) => {
    const res = await authService.signup(payload);
    const t = res.data?.access_token;
    if (t) {
      localStorage.setItem(TOKEN_KEY, t);
      setToken(t);
      const profile = await authService.getProfile();
      setUser(profile.data);
    }
    return res.data;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  const refreshProfile = useCallback(async () => {
    const profile = await authService.getProfile();
    setUser(profile.data);
    return profile.data;
  }, []);

  const updateProfile = useCallback(async (payload) => {
    const res = await authService.updateProfile(payload);
    setUser(res.data);
    return res.data;
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout, refreshProfile, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
