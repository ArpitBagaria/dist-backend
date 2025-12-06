"""
Tally Sync Agent

Run this on a PC that:
- Can reach Tally on LAN (e.g., http://192.168.31.65:9000)
- Can reach the backend API (local or cloud)

Flow:
1) GET /retailers from backend
2) For each retailer_code, fetch closing balance from Tally
3) POST to /tally-sync/bulk-ledger-balances with api_key and entries[]
"""

import os
from datetime import datetime
from decimal import Decimal
from typing import List

import requests
from xml.etree import ElementTree as ET

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
TALLY_HOST = os.getenv("TALLY_HOST", "http://192.168.31.65:9000")
TALLY_SYNC_API_KEY = os.getenv("TALLY_SYNC_API_KEY", "change_me_for_production")


def get_all_retailer_codes() -> List[str]:
    """Fetch all retailer codes from backend API"""
    url = f"{BACKEND_BASE_URL}/retailers"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return [r["retailer_code"] for r in data]


def get_closing_balance_from_tally(ledger_name: str) -> Decimal:
    """Fetch closing balance for a ledger from Tally"""
    xml = f"""
    <ENVELOPE>
      <HEADER>
        <TALLYREQUEST>Export</TALLYREQUEST>
      </HEADER>
      <BODY>
        <EXPORTDATA>
          <REQUESTDESC>
            <REPORTNAME>Ledger</REPORTNAME>
            <STATICVARIABLES>
              <SVFROMDATE>01-04-2024</SVFROMDATE>
              <SVTODATE>31-03-2025</SVTODATE>
              <LEDGERNAME>{ledger_name}</LEDGERNAME>
            </STATICVARIABLES>
          </REQUESTDESC>
        </EXPORTDATA>
      </BODY>
    </ENVELOPE>
    """.strip()

    resp = requests.post(TALLY_HOST, data=xml.encode("utf-8"), timeout=20)
    resp.raise_for_status()
    text = resp.text

    root = ET.fromstring(text)
    for elem in root.iter():
        if elem.tag.upper().endswith("CLOSINGBALANCE"):
            raw = elem.text or "0"
            cleaned = "".join(ch for ch in raw if ch.isdigit() or ch in "-.")
            if cleaned in ("", "-"):
                return Decimal("0")
            return Decimal(cleaned)

    return Decimal("0")


def main():
    """Main sync function"""
    print("=== Tally Sync Agent ===")
    print("Backend:", BACKEND_BASE_URL)
    print("Tally:", TALLY_HOST)

    retailer_codes = get_all_retailer_codes()
    print(f"Found {len(retailer_codes)} retailers")
    
    now_iso = datetime.utcnow().isoformat() + "Z"
    entries = []

    for code in retailer_codes:
        try:
            bal = get_closing_balance_from_tally(code)
            print(f"{code}: {bal}")
            entries.append(
                {
                    "retailer_code": code,
                    "closing_balance": float(bal),
                    "as_of": now_iso,
                }
            )
        except Exception as e:
            print(f"Error for {code}: {e}")

    if not entries:
        print("No entries to sync.")
        return

    payload = {"api_key": TALLY_SYNC_API_KEY, "entries": entries}
    url = f"{BACKEND_BASE_URL}/tally-sync/bulk-ledger-balances"
    print(f"\nSyncing {len(entries)} entries to backend...")
    
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    
    print(f"✓ Synced: {result['synced']} retailers")
    print("=== Sync Complete ===")


if __name__ == "__main__":
    main()
