import { useEffect, useState } from 'react';
import { api, NegativeReportRow } from '../api/client';

interface Stats {
  totalRetailers: number;
  odRetailers: number;
  totalOdAmount: number;
  lastSyncTime: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [topOdRetailers, setTopOdRetailers] = useState<NegativeReportRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError('');

      const [retailers, report, syncLogs] = await Promise.all([
        api.get<Array<{ id: number }>>('/retailers'),
        api.get<{ rows: NegativeReportRow[] }>('/reports/negative'),
        api.get<{ logs: Array<{ finished_at: string | null }> }>('/debug/sync-logs?limit=1'),
      ]);

      const totalOd = report.rows.reduce((sum, row) => sum + row.od_amount, 0);
      const lastSync = syncLogs.logs[0]?.finished_at || 'Never';

      setStats({
        totalRetailers: retailers.length,
        odRetailers: report.rows.length,
        totalOdAmount: totalOd,
        lastSyncTime: lastSync,
      });

      setTopOdRetailers(report.rows.slice(0, 5));
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>Dashboard</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>Overview of your distribution system</p>
      </div>

      <div className="grid grid-4" style={{ marginBottom: '32px' }}>
        <StatCard
          title="Total Retailers"
          value={stats?.totalRetailers || 0}
          color="var(--color-primary)"
        />
        <StatCard
          title="OD Retailers"
          value={stats?.odRetailers || 0}
          color="var(--color-danger)"
        />
        <StatCard
          title="Total OD Amount"
          value={`₹${(stats?.totalOdAmount || 0).toLocaleString()}`}
          color="var(--color-warning)"
        />
        <StatCard
          title="Last Sync"
          value={stats?.lastSyncTime === 'Never' ? 'Never' : new Date(stats?.lastSyncTime || '').toLocaleDateString()}
          color="var(--color-success)"
          isText
        />
      </div>

      <div className="card">
        <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>
          Top 5 OD Retailers
        </h2>
        {topOdRetailers.length === 0 ? (
          <p style={{ color: 'var(--color-text-secondary)', textAlign: 'center', padding: '32px' }}>
            No OD retailers found
          </p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Retailer Code</th>
                <th>Name</th>
                <th>Closing Balance</th>
                <th>Stock Value</th>
                <th>OD Amount</th>
              </tr>
            </thead>
            <tbody>
              {topOdRetailers.map((row) => (
                <tr key={row.retailer_code}>
                  <td style={{ fontWeight: '600' }}>{row.retailer_code}</td>
                  <td>{row.retailer_name}</td>
                  <td>₹{row.closing_balance.toLocaleString()}</td>
                  <td>₹{row.stock_value.toLocaleString()}</td>
                  <td style={{ color: 'var(--color-danger)', fontWeight: '600' }}>
                    ₹{row.od_amount.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, color, isText = false }: { title: string; value: string | number; color: string; isText?: boolean }) {
  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <div style={{ color: 'var(--color-text-secondary)', fontSize: '14px', marginBottom: '8px' }}>
        {title}
      </div>
      <div style={{
        fontSize: isText ? '18px' : '32px',
        fontWeight: '700',
        color: color,
      }}>
        {value}
      </div>
    </div>
  );
}
