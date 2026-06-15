"""
tickers.py — S&P 500 constituent loader
----------------------------------------
Fetches the current S&P 500 list from a public GitHub dataset.
Falls back to a hardcoded snapshot if the network is unavailable.
"""

import csv
import io

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

_SP500_CSV_URL = (
    "https://raw.githubusercontent.com/datasets/"
    "s-and-p-500-companies/main/data/constituents.csv"
)

# Hardcoded snapshot (top ~30) used only if the live fetch fails
_FALLBACK_TICKERS = [
    "MMM","AOS","ABT","ABBV","ACN","ADBE","AMD","AES","AFL","A",
    "APD","ABNB","AKAM","ALB","ARE","ALGN","ALLE","LNT","ALL","GOOGL",
    "GOOG","MO","AMZN","AMCR","AEE","AAL","AEP","AXP","AIG","AMT",
]


def get_sp500_tickers() -> list[str]:
    """
    Returns a list of S&P 500 ticker symbols.
    Dots in tickers are converted to hyphens (e.g. BRK.B → BRK-B)
    to match the format yfinance expects.
    """
    if _REQUESTS_AVAILABLE:
        try:
            resp = requests.get(_SP500_CSV_URL, timeout=10)
            resp.raise_for_status()
            reader = csv.DictReader(io.StringIO(resp.text))
            tickers = [row["Symbol"].replace(".", "-") for row in reader]
            if tickers:
                print(f"[tickers] Loaded {len(tickers)} S&P 500 tickers from live source.")
                return tickers
        except Exception as e:
            print(f"[tickers] Live fetch failed ({e}), using fallback list.")

    print(f"[tickers] Using fallback list ({len(_FALLBACK_TICKERS)} tickers).")
    return _FALLBACK_TICKERS


# Module-level list — import this in your scripts
TICKERS = get_sp500_tickers()