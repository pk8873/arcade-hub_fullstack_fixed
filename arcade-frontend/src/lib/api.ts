export const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/+$/, "") ||
  "http://localhost:8000";

const TOKEN_KEY = "arcade.token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
export function setToken(t: string | null) {
  if (t) localStorage.setItem(TOKEN_KEY, t);
  else localStorage.removeItem(TOKEN_KEY);
}

export async function api<T = any>(
  path: string,
  opts: RequestInit & { auth?: boolean } = {}
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((opts.headers as Record<string, string>) || {}),
  };
  if (opts.auth !== false) {
    const t = getToken();
    if (t) headers["Authorization"] = `Bearer ${t}`;
  }
  const res = await fetch(`${API_URL}${path}`, { ...opts, headers });
  const text = await res.text();
  const data = text ? safeJson(text) : null;
  if (!res.ok) {
    const msg = (data && (data.detail || data.message)) || res.statusText;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data as T;
}

function safeJson(s: string) {
  try { return JSON.parse(s); } catch { return s; }
}

export interface User {
  id: number;
  email: string;
  username: string;
  is_verified: boolean;
  is_admin: boolean;
  created_at: string;
}
export interface TokenResponse { access_token: string; token_type: string; user: User; }
