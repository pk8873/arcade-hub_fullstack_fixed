import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { useAuth } from "../lib/auth";

export function SignupPage() {
  const { signup } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault(); setErr(null); setBusy(true);
    try {
      await signup(email, username, password);
      await nav({ to: "/dashboard" });
    } catch (e: any) { setErr(e.message || "Signup failed"); }
    finally { setBusy(false); }
  }

  return (
    <div className="max-w-md mx-auto card mt-10">
      <h1 className="text-2xl font-bold mb-1">Create your account</h1>
      <p className="text-slate-400 text-sm mb-6">We'll email you a one-click verify link automatically.</p>
      <form onSubmit={onSubmit} className="space-y-4">
        <div><label className="label">Email</label>
          <input className="input" type="email" required value={email} onChange={e=>setEmail(e.target.value)} /></div>
        <div><label className="label">Username</label>
          <input className="input" pattern="[A-Za-z0-9_]{3,60}" required value={username} onChange={e=>setUsername(e.target.value)} />
          <p className="text-xs text-slate-500 mt-1">3–60 chars, letters/numbers/underscore.</p></div>
        <div><label className="label">Password</label>
          <input className="input" type="password" minLength={8} required value={password} onChange={e=>setPassword(e.target.value)} />
          <p className="text-xs text-slate-500 mt-1">Minimum 8 characters.</p></div>
        {err && <div className="text-rose-400 text-sm">{err}</div>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Creating account…" : "Create account"}</button>
      </form>
      <p className="text-sm text-slate-400 mt-4">
        Already have an account? <Link to="/login" className="text-violet-400">Log in</Link>
      </p>
    </div>
  );
}
