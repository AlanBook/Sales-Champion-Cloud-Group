"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { apiFetch } from "@/lib/api";
import type { AuthUser, LoginResponse } from "@/lib/types";

type AuthContextValue = {
  ready: boolean;
  token: string | null;
  user: AuthUser | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const TOKEN_KEY = "sales-champion-token";
const USER_KEY = "sales-champion-user";

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    const savedToken = window.localStorage.getItem(TOKEN_KEY);
    const savedUser = window.localStorage.getItem(USER_KEY);
    queueMicrotask(() => {
      setToken(savedToken);
      setUser(savedUser ? (JSON.parse(savedUser) as AuthUser) : null);
      setReady(true);
    });
  }, []);

  useEffect(() => {
    if (!ready || !token || user) {
      return;
    }
    apiFetch<AuthUser>("/auth/me", token)
      .then((nextUser) => {
        setUser(nextUser);
        window.localStorage.setItem(USER_KEY, JSON.stringify(nextUser));
      })
      .catch(() => {
        setToken(null);
        setUser(null);
        window.localStorage.removeItem(TOKEN_KEY);
        window.localStorage.removeItem(USER_KEY);
      });
  }, [ready, token, user]);

  const value = useMemo<AuthContextValue>(
    () => ({
      ready,
      token,
      user,
      async login(username: string, password: string) {
        const payload = await apiFetch<LoginResponse>("/auth/login", null, {
          method: "POST",
          body: JSON.stringify({ username, password }),
        });
        setToken(payload.access_token);
        setUser(payload.user);
        window.localStorage.setItem(TOKEN_KEY, payload.access_token);
        window.localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
      },
      logout() {
        setToken(null);
        setUser(null);
        window.localStorage.removeItem(TOKEN_KEY);
        window.localStorage.removeItem(USER_KEY);
      },
    }),
    [ready, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth 必须在 AuthProvider 内使用。");
  }
  return context;
}
