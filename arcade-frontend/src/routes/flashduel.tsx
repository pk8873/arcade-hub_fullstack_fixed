import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Q = { id: number; q: string; a: string[]; _c: number };

export function FlashDuelPage() {
  const [data, setData] = useState<{ questions: Q[] } | null>(null);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [times, setTimes] = useState<number[]>([]);
  const [started, setStarted] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [board, setBoard] = useState<any[]>([]);

  async function loadBoard() {
    try { setBoard(await api("/api/games/flashduel/leaderboard")); } catch {}
  }
  useEffect(() => { loadBoard(); }, []);

  async function startGame() {
    setResult(null); setAnswers([]); setTimes([]); setIdx(0);
    const d = await api<{ questions: Q[] }>("/api/games/flashduel/questions");
    setData(d); setStarted(performance.now());
  }

  function pick(choice: number) {
    if (!data) return;
    const now = performance.now();
    const t = now - started;
    const newA = [...answers, choice];
    const newT = [...times, t];
    setAnswers(newA); setTimes(newT); setStarted(now);
    if (idx + 1 >= data.questions.length) {
      const avg = Math.round(newT.reduce((s, x) => s + x, 0) / newT.length);
      api("/api/games/flashduel/submit", {
        method: "POST",
        body: JSON.stringify({
          answers: newA,
          correct_key: data.questions.map(q => q._c),
          avg_ms: avg,
        }),
      }).then(r => { setResult(r); setData(null); loadBoard(); })
        .catch(e => setResult({ error: e.message }));
    } else {
      setIdx(idx + 1);
    }
  }

  const cur = data?.questions[idx];

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold">⚡ Flash Duel</h1>
        <p className="text-slate-400 text-sm">5 questions. Speed matters — faster correct answers score higher.</p>
      </div>

      {!data && !result && (
        <button className="btn-primary" onClick={startGame}>Start match</button>
      )}

      {cur && (
        <div className="card">
          <div className="text-xs text-slate-500">Question {idx + 1} / {data!.questions.length}</div>
          <div className="text-xl font-semibold mt-2">{cur.q}</div>
          <div className="grid sm:grid-cols-2 gap-2 mt-4">
            {cur.a.map((opt, i) => (
              <button key={i} className="btn-ghost text-left" onClick={() => pick(i)}>{opt}</button>
            ))}
          </div>
        </div>
      )}

      {result && !result.error && (
        <div className="card">
          <div className="text-2xl font-bold">{result.correct}/{result.total} correct</div>
          <div className="text-slate-400 text-sm">Score: {result.score} · Coins: +{result.coins_awarded}</div>
          <button className="btn-primary mt-3" onClick={startGame}>Play again</button>
        </div>
      )}
      {result?.error && <div className="card text-rose-400">{result.error}</div>}

      <div className="card">
        <h3 className="font-semibold mb-2">Top players</h3>
        <ol className="text-sm divide-y divide-slate-800">
          {board.map((r, i) => (
            <li key={i} className="flex justify-between py-1">
              <span><span className="text-slate-500 mr-2">#{i+1}</span>{r.username} · {r.correct}/{r.total}</span>
              <span className="font-mono">{r.score}</span>
            </li>
          ))}
          {board.length === 0 && <li className="text-slate-500 py-2">No results yet.</li>}
        </ol>
      </div>
    </div>
  );
}
