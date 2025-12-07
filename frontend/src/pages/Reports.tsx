import { useState } from 'react';
import { api, NegativeReport } from '../api/client';

export default function Reports() {
  const [report, setReport] = useState<NegativeReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function generateReport() {
    try {
      setLoading(true);
      setError('');
      const data = await api.get<NegativeReport>('/reports/negative');
      setReport(data);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  }

  const totalOd = report?.rows.reduce((sum, row) => sum + row.od_amount, 0) || 0;

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>Negative/OD Report</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>
          View retailers with overdraft balances
        </p>
      </div>

      <div className="card" style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '4px' }}>Generate Report</h2>
            <p style={{ fontSize: '14px', color: 'var(--color-text-secondary)' }}>
              Compare Tally balances vs stock values
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={generateReport}
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Report'}
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {report && (
        <>
          <div className="grid grid-3" style={{ marginBottom: '32px' }}>
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ color: 'var(--color-text-secondary)', fontSize: '14px', marginBottom: '8px' }}>
                Total OD Retailers
              </div>
              <div style={{ fontSize: '32px', fontWeight: '700', color: 'var(--color-danger)' }}>
                {report.rows.length}
              </div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ color: 'var(--color-text-secondary)', fontSize: '14px', marginBottom: '8px' }}>
                Total OD Amount
              </div>
              <div style={{ fontSize: '32px', fontWeight: '700', color: 'var(--color-warning)' }}>
                ₹{totalOd.toLocaleString()}
              </div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ color: 'var(--color-text-secondary)', fontSize: '14px', marginBottom: '8px' }}>
                Generated At
              </div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: 'var(--color-primary)' }}>
                {new Date(report.generated_at).toLocaleString()}
              </div>
            </div>
          </div>

          <div className="card">
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>
              Report Details
            </h2>
            {report.rows.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)', textAlign: 'center', padding: '32px' }}>
                No OD retailers found
              </p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Retailer Code</th>
                      <th>Name</th>
                      <th>Closing Balance</th>
                      <th>Stock Value</th>
                      <th>OD Amount</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.rows.map((row) => (
                      <tr key={row.retailer_code}>
                        <td style={{ fontWeight: '600' }}>{row.retailer_code}</td>
                        <td>{row.retailer_name}</td>
                        <td>₹{row.closing_balance.toLocaleString()}</td>
                        <td>₹{row.stock_value.toLocaleString()}</td>
                        <td style={{ color: 'var(--color-danger)', fontWeight: '600' }}>
                          ₹{row.od_amount.toLocaleString()}
                        </td>
                        <td>
                          <span
                            className={`badge ${
                              row.od_amount > 100000
                                ? 'badge-danger'
                                : row.od_amount > 50000
                                ? 'badge-warning'
                                : 'badge-success'
                            }`}
                          >
                            {row.od_amount > 100000
                              ? 'High Risk'
                              : row.od_amount > 50000
                              ? 'Medium Risk'
                              : 'Low Risk'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
