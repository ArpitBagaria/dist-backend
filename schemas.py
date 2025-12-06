"""Pydantic schemas for API request/response validation"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class PrmSyncResponse(BaseModel):
    run_id: int
    retailers_upserted: int
    products_upserted: int
    inventory_rows: int
    activations_rows: int
    status: str


class ProductPriceUpdate(BaseModel):
    goods_id: str
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None


class ProductPriceUpdateRequest(BaseModel):
    updates: List[ProductPriceUpdate]


class ProductPriceUpdateResponse(BaseModel):
    updated: int


class TallyClosingBalanceResponse(BaseModel):
    ledger: str
    closing_balance: float


class NegativeReportRow(BaseModel):
    retailer_code: str
    retailer_name: str
    closing_balance: float
    stock_value: float
    od_amount: float


class NegativeReportResponse(BaseModel):
    generated_at: datetime
    rows: List[NegativeReportRow]


# NEW: Retailer list API schema
class RetailerOut(BaseModel):
    id: int
    retailer_code: str
    name: str

    class Config:
        orm_mode = True


# NEW: Tally sync schemas
class TallySyncEntry(BaseModel):
    retailer_code: str
    closing_balance: float
    as_of: datetime


class TallySyncRequest(BaseModel):
    api_key: str
    entries: List[TallySyncEntry]


class TallySyncResponse(BaseModel):
    synced: int


# Auto-approval engine schemas
class OrderItemInput(BaseModel):
    goods_id: str
    quantity: int


class AutoApprovalRequest(BaseModel):
    retailer_code: str
    items: List[OrderItemInput]


class AutoApprovalDecision(BaseModel):
    decision: Literal["APPROVE", "HOLD", "REJECT"]
    risk_score: float
    order_value: float
    od_amount: float
    recent_sales_30d_value: float
    rules_triggered: List[str]
