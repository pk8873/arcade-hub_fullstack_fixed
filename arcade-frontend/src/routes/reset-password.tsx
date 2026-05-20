import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { api } from "../lib/api";

export function ResetPasswordPage() {
  const nav = useNavigate();
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get("token") || "";
    setToken(t);
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault(); setErr(null); setBusy(true);
    if (password !== confirm) { setErr("Passwords do not match"); setBusy(false); return; }
    try {
      await api("/api/auth/reset-password", {
        method: "POST", auth: false,
        body: JSON.stringify({ token, new_password: password }),
      });
      setOk(true);
      setTimeout(() => { nav({ to: "/login" }); }, 1500);
    } catch (e: any) { setErr(e.message || "Reset failed"); }
    finally { setBusy(false); }
  }

  return (
    <div className="max-w-md mx-auto card mt-10">
      <h1 className="text-2xl font-bold mb-1">Set a new password</h1>
      <p className="text-slate-400 text-sm mb-6">Choose a strong password (minimum 8 characters).</p>
      {ok ? (
        <div className="text-emerald-400 text-sm">
          Password updated. Redirecting to login…
        </div>
      ) : (
        <form onSubmit={onSubmit} className="space-y-4">
          <div><label className="label">Reset token</label>
            <input className="input" required value={token} onChange={e=>setToken(e.target.value)} /></div>
          <div><label className="label">New password</label>
            <input className="input" type="password" minLength={8} required value={password} onChange={e=>setPassword(e.target.value)} /></div>
          <div><label className="label">Confirm password</label>
            <input className="input" type="password" minLength={8} required value={confirm} onChange={e=>setConfirm(e.target.value)} /></div>
          {err && <div className="text-rose-400 text-sm">{err}</div>}
          <button className="btn-primary w-full" disabled={busy}>{busy ? "Saving…" : "Update password"}</button>
        </form>
      )}
      <p className="text-sm text-slate-400 mt-4">
        <Link to="/login" className="text-violet-400">Back to login</Link>
      </p>
    </div>
  );
}
