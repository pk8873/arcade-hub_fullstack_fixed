import { Link } from "@tanstack/react-router";

export function VerifiedPage() {
  return (
    <div className="max-w-md mx-auto card mt-10 text-center">
      <div className="text-5xl mb-3 text-emerald-400">✓</div>
      <h1 className="text-2xl font-bold">Email verified!</h1>
      <p className="text-slate-400 mt-1">You're all set. Time to play.</p>
      <div className="mt-5 flex gap-2 justify-center">
        <Link to="/dashboard" className="btn-primary">Go to dashboard</Link>
      </div>
    </div>
  );
}
