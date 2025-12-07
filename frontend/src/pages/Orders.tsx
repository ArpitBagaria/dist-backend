import { useState } from 'react';
import { api, AutoApprovalDecision, AutoApprovalRequest } from '../api/client';

interface OrderItem {
  goods_id: string;
  quantity: number;
}

export default function Orders() {
  const [retailerCode, setRetailerCode] = useState('');
  const [items, setItems] = useState<OrderItem[]>([{ goods_id: '', quantity: 1 }]);
  const [result, setResult] = useState<AutoApprovalDecision | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function addItem() {
    setItems([...items, { goods_id: '', quantity: 1 }]);
  }

  function updateItem(index: number, field: keyof OrderItem, value: string | number) {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  }

  function removeItem(index: number) {
    setItems(items.filter((_, i) => i !== index));
  }

  async function checkApproval() {
    if (!retailerCode.trim()) {
      setError('Please enter a retailer code');
      return;
    }

    const validItems = items.filter((item) => item.goods_id.trim() && item.quantity > 0);
    if (validItems.length === 0) {
      setError('Please add at least one item with valid goods ID and quantity');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setResult(null);

      const request: AutoApprovalRequest = {
        retailer_code: retailerCode,
        items: validItems,
      };

      const decision = await api.post<AutoApprovalDecision>('/orders/auto-approval', request);
      setResult(decision);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to check order approval');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>Order Approval</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>Check if an order will be auto-approved</p>
      </div>

      <div className="grid grid-2" style={{ gap: '32px' }}>
        <div className="card">
          <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>Order Details</h2>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', fontSize: '14px' }}>
              Retailer Code
            </label>
            <input
              type="text"
              className="input"
              placeholder="Enter retailer code"
              value={retailerCode}
              onChange={(e) => setRetailerCode(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <label style={{ fontWeight: '500', fontSize: '14px' }}>Order Items</label>
              <button className="btn btn-secondary" onClick={addItem} style={{ padding: '6px 12px', fontSize: '13px' }}>
                + Add Item
              </button>
            </div>

            {items.map((item, index) => (
              <div key={index} style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                <input
                  type="text"
                  className="input"
                  placeholder="Goods ID"
                  value={item.goods_id}
                  onChange={(e) => updateItem(index, 'goods_id', e.target.value)}
                  style={{ flex: 2 }}
                />
                <input
                  type="number"
                  className="input"
                  placeholder="Qty"
                  value={item.quantity}
                  onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 0)}
                  min="1"
                  style={{ flex: 1 }}
                />
                {items.length > 1 && (
                  <button
                    className="btn btn-secondary"
                    onClick={() => removeItem(index)}
                    style={{ padding: '10px 16px' }}
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>

          {error && <div className="error" style={{ marginBottom: '16px' }}>{error}</div>}

          <button
            className="btn btn-primary"
            onClick={checkApproval}
            disabled={loading}
            style={{ width: '100%' }}
          >
            {loading ? 'Checking...' : 'Check Approval'}
          </button>
        </div>

        <div>
          {result && (
            <div className="card">
              <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>Approval Decision</h2>

              <div style={{ marginBottom: '24px' }}>
                <div
                  style={{
                    padding: '16px',
                    borderRadius: '8px',
                    textAlign: 'center',
                    fontSize: '24px',
                    fontWeight: '700',
                    backgroundColor:
                      result.decision === 'APPROVE'
                        ? '#d1fae5'
                        : result.decision === 'HOLD'
                        ? '#fef3c7'
                        : '#fee2e2',
                    color:
                      result.decision === 'APPROVE'
                        ? '#065f46'
                        : result.decision === 'HOLD'
                        ? '#92400e'
                        : '#991b1b',
                  }}
                >
                  {result.decision}
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <DetailRow label="Risk Score" value={result.risk_score.toFixed(2)} />
                <DetailRow label="Order Value" value={`₹${result.order_value.toLocaleString()}`} />
                <DetailRow label="OD Amount" value={`₹${result.od_amount.toLocaleString()}`} />
                <DetailRow label="Recent Sales (30d)" value={`₹${result.recent_sales_30d_value.toLocaleString()}`} />
              </div>

              {result.rules_triggered.length > 0 && (
                <div style={{ marginTop: '24px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
                    Rules Triggered
                  </h3>
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {result.rules_triggered.map((rule, index) => (
                      <li
                        key={index}
                        style={{
                          padding: '8px 12px',
                          backgroundColor: 'var(--color-bg)',
                          borderRadius: '6px',
                          fontSize: '14px',
                        }}
                      >
                        {rule}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '12px', borderBottom: '1px solid var(--color-border)' }}>
      <span style={{ color: 'var(--color-text-secondary)', fontSize: '14px' }}>{label}</span>
      <span style={{ fontWeight: '600', fontSize: '14px' }}>{value}</span>
    </div>
  );
}
