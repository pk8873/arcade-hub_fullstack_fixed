import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { api } from "../lib/api";

export function ForgotPasswordPage() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault(); setErr(null); setMsg(null); setBusy(true);
    try {
      const res = await api<{ ok: boolean; reset_token: string | null }>(
        "/api/auth/forgot-password",
        { method: "POST", auth: false, body: JSON.stringify({ email }) }
      );
      if (res.reset_token) {
        await nav({ to: "/reset-password", search: { token: res.reset_token } as any });
      } else {
        setMsg("If that email is registered, a reset link was issued. Please contact support if you do not receive it.");
      }
    } catch (e: any) { setErr(e.message || "Request failed"); }
    finally { setBusy(false); }
  }

  return (
    <div className="max-w-md mx-auto card mt-10">
      <h1 className="text-2xl font-bold mb-1">Forgot your password?</h1>
      <p className="text-slate-400 text-sm mb-6">Enter your account email to reset your password.</p>
      <form onSubmit={onSubmit} className="space-y-4">
        <div><label className="label">Email</label>
          <input className="input" type="email" required value={email} onChange={e=>setEmail(e.target.value)} /></div>
        {err && <div className="text-rose-400 text-sm">{err}</div>}
        {msg && <div className="text-emerald-400 text-sm">{msg}</div>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Working…" : "Continue"}</button>
      </form>
      <p className="text-sm text-slate-400 mt-4">
        Remembered it? <Link to="/login" className="text-violet-400">Back to login</Link>
      </p>
    </div>
  );
}
