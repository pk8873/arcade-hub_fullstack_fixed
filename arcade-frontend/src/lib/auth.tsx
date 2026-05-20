import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, getToken, setToken, type TokenResponse, type User } from "./api";

interface AuthState {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<User>;
  signup: (email: string, username: string, password: string) => Promise<User>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(!!getToken());

  const refresh = useCallback(async () => {
    if (!getToken()) { setUser(null); setLoading(false); return; }
    try {
      const me = await api<User>("/api/auth/me");
      setUser(me);
    } catch { setToken(null); setUser(null); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const login = useCallback(async (email: string, password: string) => {
    const r = await api<TokenResponse>("/api/auth/login", {
      method: "POST", auth: false, body: JSON.stringify({ email, password }),
    });
    setToken(r.access_token); setUser(r.user); return r.user;
  }, []);

  const signup = useCallback(async (email: string, username: string, password: string) => {
    const r = await api<TokenResponse>("/api/auth/signup", {
      method: "POST", auth: false, body: JSON.stringify({ email, username, password }),
    });
    setToken(r.access_token); setUser(r.user); return r.user;
  }, []);

  const logout = useCallback(() => { setToken(null); setUser(null); }, []);

  const value = useMemo<AuthState>(() => ({
    user, loading, isAuthenticated: !!user, login, signup, logout, refresh,
  }), [user, loading, login, signup, logout, refresh]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth(): AuthState {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth must be used inside <AuthProvider>");
  return v;
}
