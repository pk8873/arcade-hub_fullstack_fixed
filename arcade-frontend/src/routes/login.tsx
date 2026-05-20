import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { useAuth } from "../lib/auth";

export function LoginPage() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault(); setErr(null); setBusy(true);
    try { await login(email, password); await nav({ to: "/dashboard" }); }
    catch (e: any) { setErr(e.message || "Login failed"); }
    finally { setBusy(false); }
  }

  return (
    <div className="max-w-md mx-auto card mt-10">
      <h1 className="text-2xl font-bold mb-1">Welcome back</h1>
      <p className="text-slate-400 text-sm mb-6">Log in to your ArcadeHub account.</p>
      <form onSubmit={onSubmit} className="space-y-4">
        <div><label className="label">Email</label>
          <input className="input" type="email" required value={email} onChange={e=>setEmail(e.target.value)} /></div>
        <div><label className="label">Password</label>
          <input className="input" type="password" required value={password} onChange={e=>setPassword(e.target.value)} /></div>
        {err && <div className="text-rose-400 text-sm">{err}</div>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
      </form>
      <p className="text-sm text-slate-400 mt-4">
        <Link to="/forgot-password" className="text-violet-400">Forgot password?</Link>
      </p>
      <p className="text-sm text-slate-400 mt-2">
        No account? <Link to="/signup" className="text-violet-400">Create one</Link>
      </p>
    </div>
  );
}
