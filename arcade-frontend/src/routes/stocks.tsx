import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Player = { key: string; name: string; role: string; base: number; price: number };
type Holding = { player_key: string; name: string; role: string; shares: number; avg_cost: number; price: number; value: number; pnl: number };

export function StocksPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [port, setPort] = useState<Holding[]>([]);
  const [qty, setQty] = useState<Record<string, number>>({});
  const [msg, setMsg] = useState<string | null>(null);

  async function reload() {
    try {
      const [p, pf] = await Promise.all([
        api<Player[]>("/api/games/stocks/players"),
        api<Holding[]>("/api/games/stocks/portfolio"),
      ]);
      setPlayers(p); setPort(pf);
    } catch (e: any) { setMsg(e.message); }
  }
  useEffect(() => { reload(); const t = setInterval(reload, 15000); return () => clearInterval(t); }, []);

  async function trade(key: string, side: "buy" | "sell") {
    const shares = qty[key] || 1;
    try {
      const r = await api<any>(`/api/games/stocks/${side}`, {
        method: "POST", body: JSON.stringify({ player_key: key, shares }),
      });
      setMsg(side === "buy" ? `Bought ${shares} @ ${r.price}` : `Sold ${shares} @ ${r.price}`);
      reload();
    } catch (e: any) { setMsg(e.message); }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">🏏 Pitch Stocks</h1>
        <p className="text-slate-400 text-sm">Trade virtual shares in cricket players. Prices tick every 30s.</p>
      </div>
      {msg && <div className="card text-sm">{msg}</div>}

      <div className="card">
        <h3 className="font-semibold mb-3">Market</h3>
        <div className="grid sm:grid-cols-2 gap-3">
          {players.map(p => (
            <div key={p.key} className="border border-slate-800 rounded p-3">
              <div className="flex justify-between">
                <div>
                  <div className="font-semibold">{p.name}</div>
                  <div className="text-xs text-slate-500">{p.role}</div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-lg">{p.price}</div>
                  <div className={`text-xs ${p.price >= p.base ? "text-emerald-400" : "text-rose-400"}`}>
                    base {p.base}
                  </div>
                </div>
              </div>
              <div className="flex gap-2 mt-2">
                <input type="number" min={1} value={qty[p.key] || 1}
                  onChange={e => setQty(q => ({ ...q, [p.key]: +e.target.value }))}
                  className="w-20 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm"/>
                <button className="btn-primary text-sm" onClick={() => trade(p.key, "buy")}>Buy</button>
                <button className="btn-ghost text-sm" onClick={() => trade(p.key, "sell")}>Sell</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold mb-3">Your portfolio</h3>
        {port.length === 0 ? <p className="text-slate-500 text-sm">No holdings yet.</p> : (
          <table className="w-full text-sm">
            <thead className="text-slate-500 text-left">
              <tr><th>Player</th><th>Shares</th><th>Avg cost</th><th>Price</th><th>Value</th><th>P/L</th></tr>
            </thead>
            <tbody>
              {port.map(h => (
                <tr key={h.player_key} className="border-t border-slate-800">
                  <td className="py-1">{h.name}</td>
                  <td>{h.shares}</td><td>{h.avg_cost}</td><td>{h.price}</td><td>{h.value}</td>
                  <td className={h.pnl >= 0 ? "text-emerald-400" : "text-rose-400"}>{h.pnl}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
