"""
Approval Engine

Pure rule-based auto-approval with numeric risk score.
Uses existing tables:
- retailers
- products
- prm_inventory_snapshot
- activations
- tally_ledger_cache (via tally_cache.get_closing_balance_with_cache)
"""

from datetime import datetime, timedelta
from typing import List, Tuple

from sqlalchemy.orm import Session

from models import Retailer, Product, PrmInventorySnapshot, Activation
from tally_cache import get_closing_balance_with_cache


def compute_order_value(db: Session, items: List[dict]) -> Tuple[float, List[str]]:
    """
    Compute total order value from goods_id and quantity, using Product.current_price.

    Returns (order_value, rules_triggered_updates)
    """
    total = 0.0
    rules = []

    for item in items:
        goods_id = item["goods_id"]
        qty = item["quantity"]

        product = db.query(Product).filter_by(goods_id=goods_id).first()
        if not product or product.current_price is None:
            rules.append(
                f"Warning: No price found for goods_id {goods_id}, treated as ₹0 in order value."
            )
            continue

        line_value = (product.current_price or 0.0) * qty
        total += line_value

    return float(total), rules


def compute_stock_value(db: Session, retailer_id: int) -> float:
    """
    Compute stock value for a retailer, same logic as negative report.
    """
    stock_value = 0.0
    items = db.query(PrmInventorySnapshot).filter_by(retailer_id=retailer_id).all()

    for item in items:
        product = db.query(Product).filter_by(goods_id=item.goods_id).first()
        if product and product.current_price:
            stock_value += item.quantity * product.current_price

    return float(stock_value)


def compute_recent_sales_value(db: Session, retailer_id: int, days: int = 30) -> float:
    """
    Approximate recent sales value from activations over given days.
    """
    since = datetime.now() - timedelta(days=days)
    total = 0.0

    activations = (
        db.query(Activation)
        .filter(
            Activation.retailer_id == retailer_id,
            Activation.activation_time != None,
            Activation.activation_time >= since,
        )
        .all()
    )

    for act in activations:
        product = db.query(Product).filter_by(goods_id=act.goods_id).first()
        if product and product.current_price:
            total += product.current_price

    return float(total)


def compute_risk_and_decision(
    *,
    order_value: float,
    od_amount: float,
    recent_sales_30d_value: float,
) -> tuple[str, float, list[str]]:
    """
    Compute risk_score (0+), rules_triggered, and map to decision:
    APPROVE / HOLD / REJECT
    """

    risk = 0.0
    reasons: list[str] = []

    # --- A. OD contribution ---
    if od_amount <= 0:
        reasons.append(f"OD {od_amount:.0f} ≤ 0 → +0 risk")
    elif od_amount <= 25_000:
        risk += 20
        reasons.append(f"OD ₹{od_amount:.0f} in 0–25k band → +20 risk")
    elif od_amount <= 50_000:
        risk += 35
        reasons.append(f"OD ₹{od_amount:.0f} in 25k–50k band → +35 risk")
    elif od_amount <= 100_000:
        risk += 55
        reasons.append(f"OD ₹{od_amount:.0f} in 50k–100k band → +55 risk")
    else:
        risk += 75
        reasons.append(f"OD ₹{od_amount:.0f} > 100k → +75 risk")

    # --- B. Order vs recent 30d sales ---
    sales_base = max(recent_sales_30d_value, 1.0)
    ratio = order_value / sales_base

    if ratio <= 0.5:
        reasons.append(f"Order is {ratio:.2f}x of last 30d sales → +0 risk")
    elif ratio <= 1.0:
        risk += 5
        reasons.append(f"Order is {ratio:.2f}x of last 30d sales → +5 risk")
    elif ratio <= 1.5:
        risk += 10
        reasons.append(f"Order is {ratio:.2f}x of last 30d sales → +10 risk")
    elif ratio <= 2.0:
        risk += 20
        reasons.append(f"Order is {ratio:.2f}x of last 30d sales → +20 risk")
    else:
        risk += 30
        reasons.append(f"Order is {ratio:.2f}x of last 30d sales → +30 risk")

    # --- C. Absolute order size ---
    if order_value > 200_000:
        risk += 20
        reasons.append(f"Order value ₹{order_value:.0f} > 2L → +20 risk")
    elif order_value > 100_000:
        risk += 10
        reasons.append(f"Order value ₹{order_value:.0f} > 1L → +10 risk")

    # --- Decision mapping ---

    # 1) Always auto-approve small clean orders
    if order_value <= 20_000 and od_amount <= 10_000:
        decision = "APPROVE"
        reasons.append(
            f"Small order (≤20k) and OD ≤10k → auto-approve safety rule."
        )
        return decision, float(risk), reasons

    # 2) Otherwise threshold-based
    if risk <= 30:
        decision = "APPROVE"
    elif risk <= 60:
        decision = "HOLD"
    else:
        decision = "REJECT"

    return decision, float(risk), reasons


def run_auto_approval(
    db: Session,
    retailer_code: str,
    items: List[dict],
) -> dict:
    """
    High-level function used by API.

    Returns a dict matching AutoApprovalDecision.
    """

    # 1) Find retailer
    retailer = db.query(Retailer).filter_by(retailer_code=retailer_code).first()
    if not retailer:
        raise ValueError(f"Retailer with code {retailer_code} not found")

    # 2) Compute numbers
    order_value, pricing_warnings = compute_order_value(db, items)
    stock_value = compute_stock_value(db, retailer.id)

    try:
        closing_balance = get_closing_balance_with_cache(db, retailer_code)
    except Exception as e:
        # If Tally unreachable, treat OD as large and HOLD
        closing_balance = stock_value
        pricing_warnings.append(
            f"Warning: Could not fetch Tally for {retailer_code}: {e}"
        )

    od_amount = closing_balance - stock_value
    recent_sales_30d_value = compute_recent_sales_value(db, retailer.id, days=30)

    # 3) Compute risk + decision
    decision, risk_score, reasons = compute_risk_and_decision(
        order_value=order_value,
        od_amount=od_amount,
        recent_sales_30d_value=recent_sales_30d_value,
    )

    rules_triggered = pricing_warnings + reasons

    return {
        "decision": decision,
        "risk_score": risk_score,
        "order_value": order_value,
        "od_amount": od_amount,
        "recent_sales_30d_value": recent_sales_30d_value,
        "rules_triggered": rules_triggered,
    }
