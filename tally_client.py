"""Tally Client - functions to communicate with Tally via HTTP/XML"""
import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()
TALLY_HOST = os.getenv("TALLY_HOST", "http://192.168.31.65:9000")


def get_closing_balance(ledger_name: str) -> float:
    xml_request = f"""<ENVELOPE>
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
</ENVELOPE>"""

    try:
        response = requests.post(TALLY_HOST, data=xml_request, headers={"Content-Type": "application/xml"}, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Tally returned status code {response.status_code}")
        
        root = ET.fromstring(response.text)
        closing_balance = None
        balance_tags = [".//CLOSINGBALANCE", ".//CLOSINGBALANCE-CREDIT", ".//CLOSINGBALANCE-DEBIT", ".//CURRBALANCE"]
        
        for tag in balance_tags:
            element = root.find(tag)
            if element is not None and element.text:
                try:
                    balance_text = element.text.strip().replace(",", "").replace("Rs.", "").replace("₹", "")
                    closing_balance = float(balance_text)
                    break
                except ValueError:
                    continue
        
        if closing_balance is None:
            for elem in root.iter():
                if "BALANCE" in elem.tag.upper() and elem.text:
                    try:
                        balance_text = elem.text.strip().replace(",", "").replace("Rs.", "").replace("₹", "")
                        closing_balance = float(balance_text)
                        break
                    except ValueError:
                        continue
        
        if closing_balance is None:
            raise Exception(f"Could not find closing balance for ledger: {ledger_name}")
        return closing_balance
        
    except requests.exceptions.Timeout:
        raise Exception(f"Tally server timeout - could not reach {TALLY_HOST}")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Could not connect to Tally at {TALLY_HOST}")
    except Exception as e:
        raise Exception(f"Error fetching Tally data: {str(e)}")