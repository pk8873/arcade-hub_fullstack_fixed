import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";

interface AdminUser {
  id: number; email: string; username: string;
  is_verified: boolean; is_admin: boolean; is_active: boolean;
  balance: number; created_at: string;
}
interface Stats { total_users:number; verified_users:number; total_scores:number; total_coins_in_circulation:number; }

export function AdminPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    setErr(null);
    try {
      setStats(await api<Stats>("/api/admin/stats"));
      setUsers(await api<AdminUser[]>("/api/admin/users"));
    } catch (e: any) { setErr(e.message); }
  }
  useEffect(() => { void load(); }, []);

  async function adjust(u: AdminUser) {
    const v = prompt(`Adjust balance for ${u.username}. Positive=credit, negative=debit:`, "100");
    if (!v) return;
    const n = parseInt(v, 10); if (Number.isNaN(n)) return;
    try { await api("/api/admin/wallet/adjust", { method: "POST", body: JSON.stringify({ user_id: u.id, amount: n, note: "admin UI" }) }); await load(); }
    catch (e: any) { setErr(e.message); }
  }
  async function toggle(u: AdminUser) {
    try { await api(`/api/admin/users/${u.id}/toggle-active`, { method: "POST" }); await load(); }
    catch (e: any) { setErr(e.message); }
  }
  async function verify(u: AdminUser) {
    try { await api(`/api/admin/users/${u.id}/force-verify`, { method: "POST" }); await load(); }
    catch (e: any) { setErr(e.message); }
  }

  if (!user?.is_admin) return <div className="card">Admins only.</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Admin</h1>
      {err && <div className="card text-rose-400">{err}</div>}
      {stats && (
        <div className="grid sm:grid-cols-4 gap-3">
          <Stat label="Users" value={stats.total_users} />
          <Stat label="Verified" value={stats.verified_users} />
          <Stat label="Scores" value={stats.total_scores} />
          <Stat label="Coins" value={stats.total_coins_in_circulation} />
        </div>
      )}
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-slate-400 text-xs uppercase">
            <tr><th className="text-left p-2">User</th><th>Email</th><th>Verified</th><th>Active</th><th>Balance</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="border-t border-slate-800">
                <td className="p-2">{u.username}{u.is_admin && <span className="ml-1 text-violet-400">★</span>}</td>
                <td className="p-2">{u.email}</td>
                <td className="text-center">{u.is_verified ? "✓" : "—"}</td>
                <td className="text-center">{u.is_active ? "✓" : "—"}</td>
                <td className="text-center font-mono">{u.balance}</td>
                <td className="p-2 text-right space-x-1">
                  {!u.is_verified && <button className="btn-ghost !py-1 !px-2 text-xs" onClick={() => verify(u)}>Verify</button>}
                  <button className="btn-ghost !py-1 !px-2 text-xs" onClick={() => toggle(u)}>{u.is_active ? "Disable" : "Enable"}</button>
                  <button className="btn-primary !py-1 !px-2 text-xs" onClick={() => adjust(u)}>± Coins</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="card !p-4">
      <div className="text-xs uppercase text-slate-400">{label}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}
