const API_BASE = '/api';

export interface ApiError {
  message: string;
  status: number;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Network error' }));
    throw {
      message: error.detail || 'An error occurred',
      status: response.status,
    } as ApiError;
  }
  return response.json();
}

export const api = {
  async get<T>(path: string): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`);
    return handleResponse<T>(response);
  },

  async post<T>(path: string, data?: unknown): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined,
    });
    return handleResponse<T>(response);
  },
};

export interface Retailer {
  id: number;
  retailer_code: string;
  name: string;
}

export interface NegativeReportRow {
  retailer_code: string;
  retailer_name: string;
  closing_balance: number;
  stock_value: number;
  od_amount: number;
}

export interface NegativeReport {
  generated_at: string;
  rows: NegativeReportRow[];
}

export interface PrmSyncResponse {
  run_id: number;
  retailers_upserted: number;
  products_upserted: number;
  inventory_rows: number;
  activations_rows: number;
  status: string;
}

export interface SyncLog {
  id: number;
  started_at: string;
  finished_at: string | null;
  status: string;
  rows_imported: number | null;
  duration_seconds: number | null;
  error_message: string | null;
}

export interface AutoApprovalItem {
  goods_id: string;
  quantity: number;
}

export interface AutoApprovalRequest {
  retailer_code: string;
  items: AutoApprovalItem[];
}

export interface AutoApprovalDecision {
  decision: 'APPROVE' | 'HOLD' | 'REJECT';
  risk_score: number;
  order_value: number;
  od_amount: number;
  recent_sales_30d_value: number;
  rules_triggered: string[];
}
