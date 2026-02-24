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
