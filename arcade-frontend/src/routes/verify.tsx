import { useEffect, useState } from "react";
import { Link } from "@tanstack/react-router";
import { api } from "../lib/api";

export function VerifyPage() {
  const [status, setStatus] = useState<"working" | "ok" | "fail">("working");
  const [msg, setMsg] = useState("Verifying your email…");

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("token");
    if (!token) { setStatus("fail"); setMsg("Missing verification token."); return; }
    (async () => {
      try {
        await api(`/api/auth/verify?token=${encodeURIComponent(token)}`, { method: "POST", auth: false });
        setStatus("ok"); setMsg("Your email is verified. You can play now!");
      } catch (e: any) {
        setStatus("fail"); setMsg(e.message || "Verification failed.");
      }
    })();
  }, []);

  const color = status === "ok" ? "text-emerald-400" : status === "fail" ? "text-rose-400" : "text-slate-300";
  return (
    <div className="max-w-md mx-auto card mt-10 text-center">
      <div className={`text-5xl mb-3 ${color}`}>
        {status === "ok" ? "✓" : status === "fail" ? "✕" : "…"}
      </div>
      <p className="text-lg">{msg}</p>
      <div className="mt-5 flex gap-2 justify-center">
        <Link to="/dashboard" className="btn-primary">Go to dashboard</Link>
        <Link to="/login" className="btn-ghost">Log in</Link>
      </div>
    </div>
  );
}
