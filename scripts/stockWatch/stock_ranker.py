"""
stock_ranker.py — S&P 500 Growth Ranker
-----------------------------------------
Fetches 6-month price history for every ticker in tickers.py,
calculates 3-month and 6-month growth, ranks all stocks,
and saves results to CSV + prints a summary table.

Usage:
    python stock_ranker.py [--top N] [--sort {3m,6m}] [--csv]

Requirements:
    pip install yfinance pandas tabulate requests
"""

import argparse
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
    import pandas as pd
    from tabulate import tabulate
except ImportError:
    print("Missing dependencies. Run:\n  pip install yfinance pandas tabulate requests")
    sys.exit(1)

from tickers import TICKERS

# ── Config ────────────────────────────────────────────────────────────────────
BATCH_SIZE = 50          # tickers per yfinance batch download
SLEEP_BETWEEN_BATCHES = 1.0  # seconds — be polite to Yahoo
OUTPUT_CSV = "sp500_growth_rankings.csv"


# ── Helpers ───────────────────────────────────────────────────────────────────

def date_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def compute_growth(series: pd.Series, start_offset_days: int) -> float | None:
    """
    Given a price series (indexed by date), return % growth
    from `start_offset_days` ago to the most recent date.
    """
    cutoff = series.index[-1] - pd.Timedelta(days=start_offset_days)
    subset = series[series.index >= cutoff]
    if len(subset) < 2:
        return None
    p_start = float(subset.iloc[0])
    p_end   = float(subset.iloc[-1])
    if p_start == 0:
        return None
    return ((p_end - p_start) / p_start) * 100


def fetch_batch(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Downloads Close prices for a batch of tickers. Returns a DataFrame."""
    try:
        data = yf.download(
            tickers,
            start=start,
            end=end,
            progress=False,
            auto_adjust=True,
            threads=True,
        )
        if data.empty:
            return pd.DataFrame()

        close = data["Close"] if "Close" in data.columns else data
        # Ensure DataFrame even for single-ticker downloads
        if isinstance(close, pd.Series):
            close = close.to_frame(name=tickers[0])
        return close
    except Exception as e:
        print(f"  [Warning] Batch download error: {e}")
        return pd.DataFrame()


# ── Core logic ────────────────────────────────────────────────────────────────

def build_rankings(tickers: list[str]) -> pd.DataFrame:
    end_dt    = datetime.today()
    start_dt  = end_dt - timedelta(days=200)   # ~6.5 months of history
    start_str = date_str(start_dt)
    end_str   = date_str(end_dt)

    batches = [tickers[i:i + BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    total   = len(tickers)

    print(f"\n  Fetching 6-month history for {total} tickers "
          f"in {len(batches)} batches of up to {BATCH_SIZE}...\n")

    rows = []
    fetched = 0

    for batch_num, batch in enumerate(batches, 1):
        print(f"  Batch {batch_num}/{len(batches)} — tickers {fetched+1}–{fetched+len(batch)}", end=" ... ", flush=True)

        close_df = fetch_batch(batch, start_str, end_str)

        for ticker in batch:
            # Normalise ticker column name (yfinance may use original dots)
            col = ticker
            if col not in close_df.columns:
                col_dot = ticker.replace("-", ".")
                col = col_dot if col_dot in close_df.columns else None

            if col is None or close_df.empty:
                rows.append({"Ticker": ticker, "3M Growth (%)": None, "6M Growth (%)": None})
                continue

            series = close_df[col].dropna()
            g3  = compute_growth(series, 90)
            g6  = compute_growth(series, 180)
            rows.append({"Ticker": ticker, "3M Growth (%)": g3, "6M Growth (%)": g6})

        fetched += len(batch)
        ok = sum(1 for r in rows[-len(batch):] if r["3M Growth (%)"] is not None)
        print(f"{ok}/{len(batch)} OK")

        if batch_num < len(batches):
            time.sleep(SLEEP_BETWEEN_BATCHES)

    df = pd.DataFrame(rows)
    df["3M Growth (%)"] = pd.to_numeric(df["3M Growth (%)"], errors="coerce").round(2)
    df["6M Growth (%)"] = pd.to_numeric(df["6M Growth (%)"], errors="coerce").round(2)
    return df


def display_rankings(df: pd.DataFrame, sort_by: str = "3m", top_n: int = 30) -> None:
    col_map = {"3m": "3M Growth (%)", "6m": "6M Growth (%)"}
    sort_col = col_map[sort_by]

    ranked = (
        df[df[sort_col].notna()]
        .sort_values(sort_col, ascending=False)
        .reset_index(drop=True)
    )
    ranked.index += 1  # 1-based rank

    def fmt(val, is_sort=False):
        if pd.isna(val):
            return "  N/A"
        arrow = "▲" if val >= 0 else "▼"
        bold  = "*" if is_sort else " "
        return f"{bold}{arrow} {val:+.2f}%"

    display = ranked.copy()
    display["3M Growth (%)"] = display["3M Growth (%)"].apply(
        lambda v: fmt(v, sort_by == "3m"))
    display["6M Growth (%)"] = display["6M Growth (%)"].apply(
        lambda v: fmt(v, sort_by == "6m"))
    display["Rank"] = display.index

    # ── Top N ──
    top    = display.head(top_n)
    bottom = display.tail(top_n).iloc[::-1]

    header = f"  S&P 500 — Ranked by {sort_col}  (as of {datetime.today().strftime('%Y-%m-%d')})"
    sep    = "═" * 60

    print(f"\n{sep}")
    print(f"  🏆  TOP {top_n} — {header}")
    print(sep)
    print(tabulate(
        top[["Rank", "Ticker", "3M Growth (%)", "6M Growth (%)"]],
        headers="keys", tablefmt="rounded_outline",
        colalign=("right", "center", "right", "right"), showindex=False,
    ))

    print(f"\n{sep}")
    print(f"  📉  BOTTOM {top_n} — {header}")
    print(sep)
    print(tabulate(
        bottom[["Rank", "Ticker", "3M Growth (%)", "6M Growth (%)"]],
        headers="keys", tablefmt="rounded_outline",
        colalign=("right", "center", "right", "right"), showindex=False,
    ))

    # ── Summary stats ──
    valid = df[sort_col].dropna()
    print(f"\n  Summary ({sort_col.upper()}):")
    print(f"    Tickers analysed : {len(df)}")
    print(f"    Data available   : {len(valid)}")
    print(f"    Positive growth  : {(valid > 0).sum()} ({(valid > 0).mean()*100:.1f}%)")
    print(f"    Negative growth  : {(valid < 0).sum()} ({(valid < 0).mean()*100:.1f}%)")
    print(f"    Average growth   : {valid.mean():+.2f}%")
    print(f"    Median growth    : {valid.median():+.2f}%")


def save_csv(df: pd.DataFrame, path: str) -> None:
    ranked = df.sort_values("3M Growth (%)", ascending=False).reset_index(drop=True)
    ranked.index += 1
    ranked.index.name = "Rank (3M)"
    ranked.to_csv(path)
    print(f"\n  💾  Full rankings saved to: {Path(path).resolve()}")


# ── Entry point ───────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="S&P 500 Growth Ranker")
    p.add_argument("--top",  type=int, default=30,  help="How many top/bottom tickers to display (default: 30)")
    p.add_argument("--sort", choices=["3m", "6m"],  default="3m", help="Sort by 3-month or 6-month growth (default: 3m)")
    p.add_argument("--csv",  action="store_true",   help="Save full results to CSV")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print("=" * 60)
    print("  S&P 500 GROWTH RANKER")
    print("=" * 60)

    df = build_rankings(TICKERS)
    display_rankings(df, sort_by=args.sort, top_n=args.top)

    if args.csv:
        save_csv(df, OUTPUT_CSV)

    # Always auto-save CSV
    save_csv(df, OUTPUT_CSV)