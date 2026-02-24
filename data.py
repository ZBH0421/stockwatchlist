"""data.py — portfolio JSON read/write helpers."""
import json
from pathlib import Path

PORTFOLIO_PATH = Path(__file__).parent / "portfolio.json"


def load_portfolio() -> list[dict]:
    """Return list of holding dicts from portfolio.json."""
    if not PORTFOLIO_PATH.exists():
        return []
    with open(PORTFOLIO_PATH) as f:
        return json.load(f)


def save_portfolio(holdings: list[dict]) -> None:
    """Persist list of holding dicts to portfolio.json."""
    with open(PORTFOLIO_PATH, "w") as f:
        json.dump(holdings, f, indent=2, ensure_ascii=False)


def add_holding(holdings: list[dict], ticker: str, shares: float,
                cost_price: float, target_price: float | None = None) -> list[dict]:
    """Add or replace a holding by ticker. Returns updated list."""
    ticker = ticker.upper().strip()
    holdings = [h for h in holdings if h["ticker"] != ticker]
    holdings.append({
        "ticker": ticker,
        "name": "",
        "sector": "",
        "shares": shares,
        "cost_price": cost_price,
        "target_price": target_price,
    })
    return holdings


def remove_holding(holdings: list[dict], ticker: str) -> list[dict]:
    """Remove holding by ticker. Returns updated list."""
    return [h for h in holdings if h["ticker"] != ticker.upper()]


import yfinance as yf


def fetch_prices(tickers: list[str]) -> dict[str, dict]:
    """
    Batch-fetch current price, name, and sector for a list of tickers.
    Returns dict keyed by ticker: {"price": float|None, "name": str, "sector": str}
    """
    if not tickers:
        return {}
    result = {}
    try:
        data = yf.download(tickers, period="2d", auto_adjust=True, progress=False)
        closes = data["Close"] if len(tickers) > 1 else data["Close"].rename(tickers[0])
    except Exception:
        closes = None

    for t in tickers:
        price = None
        if closes is not None:
            try:
                col = closes[t] if len(tickers) > 1 else closes
                price = float(col.dropna().iloc[-1])
            except Exception:
                pass

        name, sector = "", ""
        try:
            info = yf.Ticker(t).info
            name = info.get("shortName", info.get("longName", ""))
            sector = info.get("sector", "")
        except Exception:
            pass

        result[t] = {"price": price, "name": name, "sector": sector}

    return result


def enrich_holdings(holdings: list[dict]) -> list[dict]:
    """
    Fetch live prices & metadata. Returns enriched dicts with:
    current_price, market_value, pnl, pnl_pct, name, sector
    """
    tickers = [h["ticker"] for h in holdings]
    prices = fetch_prices(tickers)
    enriched = []
    for h in holdings:
        h = h.copy()
        info = prices.get(h["ticker"], {})
        if not h.get("name"):
            h["name"] = info.get("name", h["ticker"])
        if not h.get("sector"):
            h["sector"] = info.get("sector", "Unknown")
        current = info.get("price")
        h["current_price"] = current
        if current is not None:
            h["market_value"] = current * h["shares"]
            h["pnl"] = (current - h["cost_price"]) * h["shares"]
            h["pnl_pct"] = (current - h["cost_price"]) / h["cost_price"] * 100
        else:
            h["market_value"] = None
            h["pnl"] = None
            h["pnl_pct"] = None
        enriched.append(h)
    return enriched
