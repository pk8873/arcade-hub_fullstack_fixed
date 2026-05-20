import { useEffect, useRef, useState } from "react";
import { api } from "../lib/api";

export function SkyClimbPage() {
  const [bet, setBet] = useState(50);
  const [target, setTarget] = useState(2.0);
  const [mult, setMult] = useState(1.0);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [balance, setBalance] = useState<number | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const raf = useRef<number | null>(null);

  async function loadHistory() {
    try { setHistory(await api("/api/games/skyclimb/history")); } catch {}
  }
  useEffect(() => { loadHistory(); }, []);

  async function play() {
    setResult(null); setRunning(true); setMult(1.0);
    let r: any;
    try {
      r = await api("/api/games/skyclimb/round", {
        method: "POST", body: JSON.stringify({ bet, cashout_at: target }),
      });
    } catch (e: any) {
      setRunning(false); setResult({ error: e.message }); return;
    }
    setBalance(r.balance);
    const start = performance.now();
    const tick = (t: number) => {
      const elapsed = (t - start) / 1000;
      const m = Math.min(r.crash_at, +(Math.pow(1.07, elapsed * 6)).toFixed(2));
      setMult(m);
      if (m >= r.crash_at) {
        setRunning(false); setResult(r); loadHistory(); return;
      }
      raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
  }

  useEffect(() => () => { if (raf.current) cancelAnimationFrame(raf.current); }, []);

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold">🚀 Sky Climb</h1>
        <p className="text-slate-400 text-sm">Set a cash-out multiplier. Win if the rocket reaches it before crashing.</p>
      </div>

      <div className="card">
        <div className="h-48 rounded-lg bg-gradient-to-b from-indigo-900/40 to-slate-950 flex items-center justify-center relative overflow-hidden">
          <div className={`text-6xl font-mono font-bold ${running ? "text-emerald-400" : result?.won ? "text-emerald-400" : result ? "text-rose-500" : "text-slate-400"}`}>
            {mult.toFixed(2)}x
          </div>
        </div>
        <div className="grid sm:grid-cols-3 gap-3 mt-4">
          <label className="text-sm">Bet (coins)
            <input type="number" min={1} max={10000} value={bet}
              onChange={e => setBet(+e.target.value)}
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded px-2 py-1" disabled={running}/>
          </label>
          <label className="text-sm">Cash out at
            <input type="number" min={1.01} step={0.1} value={target}
              onChange={e => setTarget(+e.target.value)}
              className="mt-1 w-full bg-slate-900 border border-slate-700 rounded px-2 py-1" disabled={running}/>
          </label>
          <button onClick={play} disabled={running} className="btn-primary self-end">
            {running ? "Launching…" : "Launch"}
          </button>
        </div>
        {balance !== null && <div className="text-xs text-slate-400 mt-2">Balance: {balance} coins</div>}
        {result && !result.error && (
          <div className={`mt-3 text-sm ${result.won ? "text-emerald-400" : "text-rose-400"}`}>
            Crashed at {result.crash_at}x — {result.won ? `won ${result.payout} coins` : "lost the bet"}.
          </div>
        )}
        {result?.error && <div className="text-rose-400 mt-3 text-sm">{result.error}</div>}
      </div>

      <div className="card">
        <h3 className="font-semibold mb-2">Recent rounds</h3>
        <ul className="text-sm divide-y divide-slate-800">
          {history.map((h, i) => (
            <li key={i} className="flex justify-between py-1">
              <span>{h.cashout_at}x target · crash {h.crash_at}x</span>
              <span className={h.won ? "text-emerald-400" : "text-rose-400"}>
                {h.won ? `+${h.payout}` : `-${h.bet}`}
              </span>
            </li>
          ))}
          {history.length === 0 && <li className="text-slate-500 py-2">No rounds yet.</li>}
        </ul>
      </div>
    </div>
  );
}
