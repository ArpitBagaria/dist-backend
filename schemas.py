"""Pydantic schemas for API request/response validation"""
from typing import Optional, List
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