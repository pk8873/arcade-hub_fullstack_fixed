import { useEffect, useState } from "react";
import { Link } from "@tanstack/react-router";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

export function DashboardPage() {
  const { user, refresh } = useAuth();
  const [balance, setBalance] = useState<number | null>(null);
  const [resendMsg, setResendMsg] = useState<string | null>(null);

  useEffect(() => { api<{balance:number}>("/api/wallet/balance").then(r => setBalance(r.balance)).catch(()=>{}); }, []);

  async function resend() {
    setResendMsg(null);
    if (!user) return;
    try {
      await api("/api/auth/resend-verification", { method: "POST", auth: false, body: JSON.stringify({ email: user.email }) });
      setResendMsg("Verification email sent. Check your inbox.");
    } catch (e: any) { setResendMsg(e.message || "Failed to resend."); }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold">Hi, {user?.username} 👋</h1>
          <p className="text-slate-400">Welcome to your ArcadeHub dashboard.</p>
        </div>
        <div className="card !p-4">
          <div className="text-xs uppercase text-slate-400">Wallet balance</div>
          <div className="text-3xl font-extrabold text-violet-400">{balance ?? "…"} 🪙</div>
        </div>
      </div>

      {user && !user.is_verified && (
        <div className="card border-amber-500/40">
          <div className="font-semibold text-amber-300">Verify your email</div>
          <p className="text-sm text-slate-300 mt-1">
            You can browse, but you need to verify your email before submitting scores.
          </p>
          <div className="mt-3 flex gap-2">
            <button className="btn-primary" onClick={resend}>Resend verification email</button>
            {resendMsg && <span className="text-sm text-slate-400 self-center">{resendMsg}</span>}
          </div>
        </div>
      )}

      <div className="grid sm:grid-cols-3 gap-4">
        <Link to="/games" className="card hover:border-violet-500/60 transition">
          <div className="text-xl font-bold">🎮 Play games</div>
          <p className="text-slate-400 mt-1 text-sm">Submit scores, earn coins.</p>
        </Link>
        <Link to="/wallet" className="card hover:border-violet-500/60 transition">
          <div className="text-xl font-bold">🪙 Wallet</div>
          <p className="text-slate-400 mt-1 text-sm">View balance and transactions.</p>
        </Link>
        {user?.is_admin && (
          <Link to="/admin" className="card hover:border-violet-500/60 transition">
            <div className="text-xl font-bold">🛠 Admin</div>
            <p className="text-slate-400 mt-1 text-sm">Manage users and coins.</p>
          </Link>
        )}
      </div>

      <button className="text-xs text-slate-500 underline" onClick={() => refresh()}>Refresh profile</button>
    </div>
  );
}
