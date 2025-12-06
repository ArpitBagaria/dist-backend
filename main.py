"""Main FastAPI application"""
import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import database
import schemas
from models import Retailer, Product, PrmInventorySnapshot, PrmSyncRunLog, PriceHistory, TallyLedgerCache
from prm_importer import import_prm_imei_file
from tally_cache import get_closing_balance_with_cache

# FIXED: Single app initialization with proper configuration
app = FastAPI(
    title="Distribution Backend API",
    version="1.5.0",
    description="Distribution Backend Service - Phase 1.5"
)

# FIXED: CORS middleware configured properly BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NEW: Read Tally Sync API Key from environment
TALLY_SYNC_API_KEY = os.getenv("TALLY_SYNC_API_KEY", "")


@app.on_event("startup")
def startup_event():
    """Initialize database on application startup"""
    print("=" * 60)
    print("Distribution Backend Service - Phase 1.5")
    print("=" * 60)
    database.init_db()
    print("Application ready!")
    print("=" * 60)


@app.get("/")
def root():
    """Root endpoint - API information"""
    return {
        "message": "Distribution Backend API - Phase 1.5",
        "version": "1.5.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.post("/run/prm-sync", response_model=schemas.PrmSyncResponse)
def run_prm_sync(db: Session = Depends(database.get_db)):
    """
    Run PRM IMEI file import synchronization
    
    Imports data from prm_imei_sample.xlsx file and updates:
    - Retailers
    - Products
    - Inventory snapshots
    - Activations
    """
    # Create run log entry
    run_log = PrmSyncRunLog(started_at=datetime.now(), status="running")
    db.add(run_log)
    db.commit()
    db.refresh(run_log)
    
    try:
        # Execute import
        result = import_prm_imei_file("prm_imei_sample.xlsx", db)
        
        # Update run log with success
        run_log.finished_at = datetime.now()
        run_log.status = "success"
        run_log.rows_imported = sum([
            result['retailers_upserted'],
            result['products_upserted'],
            result['inventory_rows'],
            result['activations_rows']
        ])
        db.commit()
        
        return {"run_id": run_log.id, "status": "success", **result}
        
    except Exception as e:
        # Update run log with error
        run_log.finished_at = datetime.now()
        run_log.status = "error"
        run_log.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"PRM sync failed: {str(e)}")


@app.post("/admin/products/prices", response_model=schemas.ProductPriceUpdateResponse)
def update_product_prices(
    request: schemas.ProductPriceUpdateRequest,
    db: Session = Depends(database.get_db)
):
    """
    Update product prices and metadata
    
    - Updates existing products or creates new ones
    - Tracks price changes in price_history table
    - Supports bulk updates
    """
    updated_count = 0
    price_changes = 0
    
    for update in request.updates:
        product = db.query(Product).filter_by(goods_id=update.goods_id).first()
        
        if product:
            # Update existing product
            if update.name is not None:
                product.name = update.name
            if update.category is not None:
                product.category = update.category
            if update.price is not None and product.current_price != update.price:
                # Log price change
                history = PriceHistory(
                    product_id=product.id,
                    old_price=product.current_price,
                    new_price=update.price,
                    source='admin_api'
                )
                db.add(history)
                price_changes += 1
                print(f"Price changed: {product.goods_id} from {product.current_price} to {update.price}")
                product.current_price = update.price
                product.last_price_update = datetime.now()
            updated_count += 1
        else:
            # Create new product
            product = Product(
                goods_id=update.goods_id,
                name=update.name,
                category=update.category,
                current_price=update.price,
                last_price_update=datetime.now()
            )
            db.add(product)
            db.flush()
            
            # Log initial price
            if update.price is not None:
                history = PriceHistory(
                    product_id=product.id,
                    old_price=None,
                    new_price=update.price,
                    source='admin_api'
                )
                db.add(history)
                price_changes += 1
            updated_count += 1
    
    db.commit()
    print(f"Updated {updated_count} products, logged {price_changes} price changes")
    return {"updated": updated_count}


@app.get("/tally/closing-balance", response_model=schemas.TallyClosingBalanceResponse)
def get_tally_closing_balance(
    ledger: str = Query(..., description="Ledger name to query"),
    db: Session = Depends(database.get_db)
):
    """
    Get closing balance for a Tally ledger
    
    Uses caching to reduce Tally API calls (2-hour TTL)
    """
    try:
        balance = get_closing_balance_with_cache(db, ledger)
        return {"ledger": ledger, "closing_balance": balance}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get closing balance for '{ledger}': {str(e)}"
        )


@app.get("/reports/negative", response_model=schemas.NegativeReportResponse)
def get_negative_report(db: Session = Depends(database.get_db)):
    """
    Generate negative/OD report
    
    Compares Tally closing balance vs stock value for each retailer
    Returns retailers where closing_balance > stock_value (OD situation)
    """
    report_rows = []
    
    # Get all retailers that have inventory
    retailers = db.query(Retailer)\
        .join(PrmInventorySnapshot, Retailer.id == PrmInventorySnapshot.retailer_id)\
        .distinct()\
        .all()
    
    for retailer in retailers:
        try:
            # Calculate stock value
            stock_value = 0.0
            items = db.query(PrmInventorySnapshot).filter_by(retailer_id=retailer.id).all()
            
            for item in items:
                product = db.query(Product).filter_by(goods_id=item.goods_id).first()
                if product and product.current_price:
                    stock_value += item.quantity * product.current_price
            
            # Get Tally closing balance
            ledger_name = retailer.retailer_code
            try:
                balance = get_closing_balance_with_cache(db, ledger_name)
            except Exception as e:
                print(f"Warning: Could not get balance for {ledger_name}: {str(e)}")
                continue
            
            # Calculate OD amount (positive means retailer owes money)
            od_amount = balance - stock_value
            
            # Only include retailers with positive OD
            if od_amount > 0:
                report_rows.append({
                    "retailer_code": retailer.retailer_code,
                    "retailer_name": retailer.name,
                    "closing_balance": round(balance, 2),
                    "stock_value": round(stock_value, 2),
                    "od_amount": round(od_amount, 2)
                })
        except Exception as e:
            print(f"Warning: Error processing retailer {retailer.retailer_code}: {str(e)}")
            continue
    
    return {
        "generated_at": datetime.now(),
        "rows": sorted(report_rows, key=lambda x: x['od_amount'], reverse=True)
    }


# NEW: Retailer list endpoint
@app.get("/retailers", response_model=List[schemas.RetailerOut])
def list_retailers(db: Session = Depends(database.get_db)):
    """
    Get list of all retailers
    
    Returns retailers sorted by retailer_code
    """
    retailers = db.query(Retailer).order_by(Retailer.retailer_code).all()
    return [schemas.RetailerOut.from_orm(r) for r in retailers]


# NEW: Bulk Tally sync endpoint
@app.post("/tally-sync/bulk-ledger-balances", response_model=schemas.TallySyncResponse)
def sync_tally_balances(
    payload: schemas.TallySyncRequest,
    db: Session = Depends(database.get_db),
):
    """
    Bulk sync Tally ledger balances
    
    This endpoint is called by the Tally Sync Agent to update
    cached ledger balances for multiple retailers at once.
    
    Requires API key authentication.
    """
    # Simple API key check
    if TALLY_SYNC_API_KEY and payload.api_key != TALLY_SYNC_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    synced = 0

    for entry in payload.entries:
        retailer = (
            db.query(Retailer)
            .filter(Retailer.retailer_code == entry.retailer_code)
            .first()
        )
        if not retailer:
            # Skip unknown retailer codes
            continue

        cache_entry = (
            db.query(TallyLedgerCache)
            .filter(TallyLedgerCache.retailer_id == retailer.id)
            .order_by(TallyLedgerCache.as_of.desc())
            .first()
        )

        if cache_entry:
            cache_entry.closing_balance = entry.closing_balance
            cache_entry.as_of = entry.as_of
            cache_entry.ledger_name = entry.retailer_code
        else:
            cache_entry = TallyLedgerCache(
                retailer_id=retailer.id,
                ledger_name=entry.retailer_code,
                closing_balance=entry.closing_balance,
                as_of=entry.as_of,
            )
            db.add(cache_entry)

        synced += 1

    db.commit()
    return schemas.TallySyncResponse(synced=synced)


@app.get("/debug/price-history")
def get_price_history(
    db: Session = Depends(database.get_db),
    limit: int = Query(50, ge=1, le=500, description="Number of records to return")
):
    """Get recent price change history"""
    history = db.query(PriceHistory)\
        .order_by(PriceHistory.changed_at.desc())\
        .limit(limit)\
        .all()
    
    result = []
    for entry in history:
        product = db.query(Product).filter_by(id=entry.product_id).first()
        result.append({
            "id": entry.id,
            "product_id": entry.product_id,
            "goods_id": product.goods_id if product else None,
            "product_name": product.name if product else None,
            "old_price": entry.old_price,
            "new_price": entry.new_price,
            "changed_at": entry.changed_at.isoformat(),
            "source": entry.source
        })
    
    return {"total": len(result), "entries": result}


@app.get("/debug/tally-cache")
def get_tally_cache(db: Session = Depends(database.get_db)):
    """View Tally cache status and entries"""
    entries = db.query(TallyLedgerCache)\
        .order_by(TallyLedgerCache.as_of.desc())\
        .all()
    
    result = []
    now = datetime.now()
    
    for entry in entries:
        age_minutes = int((now - entry.as_of).total_seconds() / 60)
        result.append({
            "id": entry.id,
            "ledger_name": entry.ledger_name,
            "closing_balance": entry.closing_balance,
            "cached_at": entry.as_of.isoformat(),
            "age_minutes": age_minutes,
            "expired": age_minutes > 120
        })
    
    return {
        "total": len(result),
        "cache_ttl_minutes": 120,
        "entries": result
    }


@app.get("/debug/sync-logs")
def get_sync_logs(
    db: Session = Depends(database.get_db),
    limit: int = Query(20, ge=1, le=100, description="Number of logs to return")
):
    """Get PRM sync run logs"""
    logs = db.query(PrmSyncRunLog)\
        .order_by(PrmSyncRunLog.started_at.desc())\
        .limit(limit)\
        .all()
    
    result = []
    for log in logs:
        duration = None
        if log.finished_at and log.started_at:
            duration = int((log.finished_at - log.started_at).total_seconds())
        
        result.append({
            "id": log.id,
            "started_at": log.started_at.isoformat(),
            "finished_at": log.finished_at.isoformat() if log.finished_at else None,
            "status": log.status,
            "rows_imported": log.rows_imported,
            "duration_seconds": duration,
            "error_message": log.error_message
        })
    
    return {"total": len(result), "logs": result}
