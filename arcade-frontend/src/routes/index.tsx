import { Link } from "@tanstack/react-router";
import { useAuth } from "../lib/auth";

export function HomePage() {
  const { isAuthenticated } = useAuth();
  return (
    <div className="space-y-10">
      <section className="text-center py-16">
        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight">
          Play. Score. <span className="text-violet-400">Earn coins.</span>
        </h1>
        <p className="mt-4 text-slate-400 max-w-xl mx-auto">
          A casual arcade hub with leaderboards and a virtual coin wallet. 100% free, no real-money gambling.
        </p>
        <div className="mt-8 flex gap-3 justify-center">
          {isAuthenticated
            ? <Link to="/games" className="btn-primary">Play now</Link>
            : <><Link to="/signup" className="btn-primary">Create account</Link>
                <Link to="/login" className="btn-ghost">Log in</Link></>}
        </div>
      </section>
      <section className="grid sm:grid-cols-3 gap-4">
        {[
          { t: "Fruit Slice", d: "Slice fruit, dodge bombs, climb the board." },
          { t: "Memory Match", d: "Find pairs faster than anyone else." },
          { t: "2048", d: "Combine tiles, hit the high score." },
        ].map(g => (
          <div key={g.t} className="card">
            <h3 className="text-xl font-bold">{g.t}</h3>
            <p className="text-slate-400 mt-1">{g.d}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
