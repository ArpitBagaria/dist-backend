"""Tally Cache - caches Tally ledger balances to reduce API calls"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import TallyLedgerCache, Retailer
from tally_client import get_closing_balance


CACHE_TTL_MINUTES = 120  # 2 hours


def get_closing_balance_with_cache(db: Session, ledger_name: str) -> float:
    """
    Get closing balance from cache if available and fresh, otherwise fetch from Tally
    
    Args:
        db: Database session
        ledger_name: Name of the ledger to query
        
    Returns:
        float: Closing balance
        
    Raises:
        Exception: If unable to fetch from Tally and no valid cache exists
    """
    # Try to find retailer by retailer_code (ledger_name)
    retailer = db.query(Retailer).filter_by(retailer_code=ledger_name).first()
    
    if not retailer:
        # No retailer found, fetch directly from Tally without caching
        return get_closing_balance(ledger_name)
    
    # Check if we have a valid cache entry
    cache_entry = db.query(TallyLedgerCache).filter_by(
        retailer_id=retailer.id
    ).order_by(TallyLedgerCache.as_of.desc()).first()
    
    now = datetime.now()
    cache_is_valid = False
    
    if cache_entry:
        age_minutes = (now - cache_entry.as_of).total_seconds() / 60
        cache_is_valid = age_minutes <= CACHE_TTL_MINUTES
    
    # If cache is valid, return it
    if cache_is_valid:
        print(f"✓ Cache hit for {ledger_name} (age: {int(age_minutes)} min)")
        return cache_entry.closing_balance
    
    # Cache miss or expired - fetch from Tally
    print(f"⟳ Fetching fresh data from Tally for {ledger_name}")
    try:
        balance = get_closing_balance(ledger_name)
        
        # Update or create cache entry
        if cache_entry:
            cache_entry.closing_balance = balance
            cache_entry.as_of = now
            cache_entry.ledger_name = ledger_name
        else:
            cache_entry = TallyLedgerCache(
                retailer_id=retailer.id,
                ledger_name=ledger_name,
                closing_balance=balance,
                as_of=now
            )
            db.add(cache_entry)
        
        db.commit()
        print(f"✓ Cached balance for {ledger_name}: {balance}")
        return balance
        
    except Exception as e:
        # If Tally fetch fails but we have an expired cache, use it as fallback
        if cache_entry and cache_entry.closing_balance is not None:
            print(f"⚠ Tally fetch failed, using stale cache for {ledger_name}")
            return cache_entry.closing_balance
        else:
            # No cache and fetch failed - raise the error
            raise e
