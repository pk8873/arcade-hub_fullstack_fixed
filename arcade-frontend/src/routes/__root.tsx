import { Link, Outlet } from "@tanstack/react-router";
import { useAuth } from "../lib/auth";

export function RootLayout() {
  const { user, isAuthenticated, logout } = useAuth();
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center gap-4">
          <Link to="/" className="font-bold text-lg text-violet-400">ArcadeHub</Link>
          <nav className="flex gap-3 text-sm text-slate-300">
            {isAuthenticated && <Link to="/dashboard" activeProps={{ className: "text-violet-400" }}>Dashboard</Link>}
            {isAuthenticated && <Link to="/games" activeProps={{ className: "text-violet-400" }}>Games</Link>}
            {isAuthenticated && <Link to="/wallet" activeProps={{ className: "text-violet-400" }}>Wallet</Link>}
            {isAuthenticated && user?.is_admin && <Link to="/admin" activeProps={{ className: "text-violet-400" }}>Admin</Link>}
          </nav>
          <div className="ml-auto flex items-center gap-2 text-sm">
            {isAuthenticated ? (
              <>
                <span className="text-slate-400 hidden sm:inline">{user?.username}</span>
                <button className="btn-ghost" onClick={logout}>Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn-ghost">Login</Link>
                <Link to="/signup" className="btn-primary">Sign up</Link>
              </>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1"><div className="max-w-6xl mx-auto p-4 sm:p-6">{<Outlet />}</div></main>
      <footer className="border-t border-slate-800 py-4 text-center text-xs text-slate-500">
        ArcadeHub — virtual coins only, not real money.
      </footer>
    </div>
  );
}
