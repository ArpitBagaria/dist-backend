import { useEffect, useState } from 'react';
import { getRetailers } from '../api/retailers';

interface Retailer {
  id: number;
  retailer_code: string;
  name: string;
}

export default function Retailers() {
  const [retailers, setRetailers] = useState<Retailer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadRetailers();
  }, []);

  async function loadRetailers() {
    try {
      setLoading(true);
      setError('');
      const data = await getRetailers();
      setRetailers(data);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to load retailers');
    } finally {
      setLoading(false);
    }
  }

  const filteredRetailers = retailers.filter(
    (r) =>
      r.retailer_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="loading">Loading retailers...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>Retailers</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            {filteredRetailers.length} retailer{filteredRetailers.length !== 1 ? 's' : ''} found
          </p>
        </div>
        <input
          type="text"
          className="input"
          placeholder="Search retailers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ width: '300px' }}
        />
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Retailer Code</th>
              <th>Name</th>
            </tr>
          </thead>
          <tbody>
            {filteredRetailers.map((retailer) => (
              <tr key={retailer.id}>
                <td>{retailer.id}</td>
                <td style={{ fontWeight: '600', color: 'var(--color-primary)' }}>
                  {retailer.retailer_code}
                </td>
                <td>{retailer.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
