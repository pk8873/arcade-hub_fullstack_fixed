import { Link } from "@tanstack/react-router";

const GAMES = [
  { to: "/games/skyclimb", title: "Sky Climb", emoji: "🚀", tag: "Cash out before the rocket crashes." },
  { to: "/games/flashduel", title: "Flash Duel", emoji: "⚡", tag: "Speed-quiz the global leaderboard." },
  { to: "/games/stocks", title: "Pitch Stocks", emoji: "🏏", tag: "Buy & sell shares in cricket players." },
];

export function GamesPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Games</h1>
      <p className="text-slate-400 text-sm">Pick a game. All play uses virtual coins.</p>
      <div className="grid sm:grid-cols-3 gap-4">
        {GAMES.map(g => (
          <Link key={g.to} to={g.to} className="card hover:border-violet-500/60 transition">
            <div className="text-4xl">{g.emoji}</div>
            <div className="text-xl font-bold mt-2">{g.title}</div>
            <p className="text-sm text-slate-400 mt-1">{g.tag}</p>
            <div className="mt-3 text-violet-400 text-sm">Play →</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
