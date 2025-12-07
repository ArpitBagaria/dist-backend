import { useEffect, useState } from 'react';
import api from '../api/client';

interface SyncLog {
  id: number;
  started_at: string;
  finished_at: string | null;
  status: string;
  rows_imported: number | null;
  duration_seconds: number | null;
  error_message: string | null;
}

interface PrmSyncResponse {
  run_id: number;
  retailers_upserted: number;
  products_upserted: number;
  inventory_rows: number;
  activations_rows: number;
  status: string;
}

export default function Sync() {
  const [syncLogs, setSyncLogs] = useState<SyncLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState('');
  const [lastResult, setLastResult] = useState<PrmSyncResponse | null>(null);

  useEffect(() => {
    loadSyncLogs();
  }, []);

  async function loadSyncLogs() {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/debug/sync-logs?limit=10');
      setSyncLogs(response.data.logs);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to load sync logs');
    } finally {
      setLoading(false);
    }
  }

  async function runSync() {
    try {
      setSyncing(true);
      setError('');
      const response = await api.post('/run/prm-sync');
      setLastResult(response.data);
      await loadSyncLogs();
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to run sync');
    } finally {
      setSyncing(false);
    }
  }

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>Data Synchronization</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>
          Sync data from PRM IMEI files and Tally
        </p>
      </div>

      <div className="card" style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '4px' }}>PRM Sync</h2>
            <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
              Import retailer, product, inventory, and activation data
            </p>
          </div>
          <button
            className="btn btn-success"
            onClick={runSync}
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : 'Run Sync Now'}
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {lastResult && (
        <div className="card" style={{ marginBottom: '32px', backgroundColor: '#d1fae5', border: '1px solid #10b981' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#065f46' }}>
            Sync Completed Successfully
          </h3>
          <div className="grid grid-4">
            <div>
              <div style={{ fontSize: '12px', color: '#065f46', marginBottom: '4px' }}>Retailers</div>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#065f46' }}>
                {lastResult.retailers_upserted}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#065f46', marginBottom: '4px' }}>Products</div>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#065f46' }}>
                {lastResult.products_upserted}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#065f46', marginBottom: '4px' }}>Inventory Rows</div>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#065f46' }}>
                {lastResult.inventory_rows}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#065f46', marginBottom: '4px' }}>Activations</div>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#065f46' }}>
                {lastResult.activations_rows}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>
          Recent Sync History
        </h2>
        {loading ? (
          <div className="loading">Loading sync logs...</div>
        ) : syncLogs.length === 0 ? (
          <p style={{ color: 'var(--color-text-secondary)', textAlign: 'center', padding: '32px' }}>
            No sync history found
          </p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Started</th>
                  <th>Finished</th>
                  <th>Duration</th>
                  <th>Status</th>
                  <th>Rows Imported</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                {syncLogs.map((log) => (
                  <tr key={log.id}>
                    <td style={{ fontWeight: '600' }}>{log.id}</td>
                    <td>{new Date(log.started_at).toLocaleString()}</td>
                    <td>{log.finished_at ? new Date(log.finished_at).toLocaleString() : 'Running...'}</td>
                    <td>{log.duration_seconds ? `${log.duration_seconds}s` : '-'}</td>
                    <td>
                      <span
                        className={`badge ${
                          log.status === 'success'
                            ? 'badge-success'
                            : log.status === 'error'
                            ? 'badge-danger'
                            : 'badge-warning'
                        }`}
                      >
                        {log.status}
                      </span>
                    </td>
                    <td>{log.rows_imported || 0}</td>
                    <td style={{ fontSize: '13px', color: 'var(--color-danger)', maxWidth: '200px' }}>
                      {log.error_message ? (
                        <span title={log.error_message}>
                          {log.error_message.substring(0, 50)}
                          {log.error_message.length > 50 ? '...' : ''}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
