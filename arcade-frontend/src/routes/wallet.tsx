import { useEffect, useState } from "react";
import { api } from "../lib/api";

interface Tx { id: number; amount: number; kind: string; note: string | null; created_at: string; }

export function WalletPage() {
  const [balance, setBalance] = useState<number | null>(null);
  const [txs, setTxs] = useState<Tx[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const b = await api<{balance:number}>("/api/wallet/balance");
        setBalance(b.balance);
        const t = await api<Tx[]>("/api/wallet/transactions");
        setTxs(t);
      } catch (e: any) { setErr(e.message); }
    })();
  }, []);

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="text-xs uppercase text-slate-400">Balance</div>
        <div className="text-5xl font-extrabold text-violet-400 mt-1">{balance ?? "…"} 🪙</div>
        <p className="text-xs text-slate-500 mt-2">Virtual coins. Not redeemable for cash.</p>
      </div>
      <div className="card">
        <h2 className="text-xl font-bold mb-3">Transactions</h2>
        {err && <div className="text-rose-400 text-sm">{err}</div>}
        {txs.length === 0 ? <p className="text-slate-400 text-sm">No transactions yet.</p> : (
          <div className="divide-y divide-slate-800">
            {txs.map(t => (
              <div key={t.id} className="py-2 flex items-center justify-between text-sm">
                <div>
                  <div className="font-medium">{t.kind}</div>
                  <div className="text-slate-500 text-xs">{t.note || "—"} · {new Date(t.created_at).toLocaleString()}</div>
                </div>
                <div className={t.amount >= 0 ? "text-emerald-400 font-semibold" : "text-rose-400 font-semibold"}>
                  {t.amount >= 0 ? "+" : ""}{t.amount}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
