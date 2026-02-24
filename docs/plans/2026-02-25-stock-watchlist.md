# Stock Watchlist Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Dash web app at port 8052 for tracking a personal stock portfolio with live prices, P&L stats, and pie/bar charts.

**Architecture:** Single-page Dash app with two Python modules — `data.py` handles JSON persistence and yfinance batch fetching, `app.py` defines layout and a single master callback that rewrites the portfolio file and refreshes all UI components on each user action.

**Tech Stack:** Python 3.14, Dash 2.14+, Dash Bootstrap Components (DARKLY), Plotly, yfinance, pandas

---

### Task 1: Project scaffolding & dependencies

**Files:**
- Create: `requirements.txt`
- Create: `portfolio.json`

**Step 1: Create requirements.txt**

```
dash>=2.14
dash-bootstrap-components>=1.5
plotly>=5.18
yfinance>=0.2.36
pandas>=2.0
```

**Step 2: Create empty portfolio.json**

```json
[]
```

**Step 3: Install dependencies**

Run: `pip3 install -r /Users/ph/stock_watchlist/requirements.txt`
Expected: All packages install without error.

**Step 4: Commit**

```bash
cd /Users/ph/stock_watchlist
git add requirements.txt portfolio.json
git commit -m "feat: add project scaffolding and dependencies"
```

---

### Task 2: data.py — JSON persistence helpers

**Files:**
- Create: `data.py`

**Step 1: Write data.py**

```python
"""data.py — portfolio JSON read/write helpers."""
import json
import os
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
```

**Step 2: Smoke-test in REPL**

Run:
```bash
cd /Users/ph/stock_watchlist
python3 -c "
from data import load_portfolio, save_portfolio, add_holding, remove_holding
h = add_holding([], 'AAPL', 10, 150.0, 200.0)
save_portfolio(h)
loaded = load_portfolio()
assert loaded[0]['ticker'] == 'AAPL'
h2 = remove_holding(loaded, 'AAPL')
assert h2 == []
print('data.py OK')
"
```
Expected: `data.py OK`

**Step 3: Commit**

```bash
git add data.py
git commit -m "feat: add portfolio JSON persistence helpers"
```

---

### Task 3: data.py — yfinance price & info fetch

**Files:**
- Modify: `data.py` (append functions below)

**Step 1: Add fetch functions to data.py**

Append to the bottom of `data.py`:

```python
import yfinance as yf


def fetch_prices(tickers: list[str]) -> dict[str, dict]:
    """
    Batch-fetch current price, name, and sector for a list of tickers.
    Returns dict keyed by ticker:
      {"price": float | None, "name": str, "sector": str}
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
    Fetch live prices & metadata and return enriched holding dicts with:
      current_price, market_value, pnl, pnl_pct, name, sector
    """
    tickers = [h["ticker"] for h in holdings]
    prices = fetch_prices(tickers)
    enriched = []
    for h in holdings:
        h = h.copy()
        info = prices.get(h["ticker"], {})
        if h.get("name") == "" or not h.get("name"):
            h["name"] = info.get("name", h["ticker"])
        if h.get("sector") == "" or not h.get("sector"):
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
```

**Step 2: Smoke-test fetch (needs network)**

Run:
```bash
cd /Users/ph/stock_watchlist
python3 -c "
from data import fetch_prices
r = fetch_prices(['AAPL', 'MSFT'])
print(r)
assert r['AAPL']['price'] is not None
print('fetch OK')
"
```
Expected: dict printed with prices, `fetch OK`

**Step 3: Commit**

```bash
git add data.py
git commit -m "feat: add yfinance batch price and enrichment helpers"
```

---

### Task 4: app.py — layout skeleton

**Files:**
- Create: `app.py`

**Step 1: Create app.py with layout (no callbacks yet)**

```python
"""app.py — Stock Watchlist Dash application."""
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="股票觀察清單",
)

# ── Input Form ──────────────────────────────────────────────────────
input_form = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dbc.Label("代碼", html_for="input-ticker"),
                dbc.Input(id="input-ticker", placeholder="AAPL", type="text",
                          style={"textTransform": "uppercase"}),
            ], width=2),
            dbc.Col([
                dbc.Label("股數", html_for="input-shares"),
                dbc.Input(id="input-shares", placeholder="10", type="number", min=0.0001),
            ], width=2),
            dbc.Col([
                dbc.Label("成本價 (USD)", html_for="input-cost"),
                dbc.Input(id="input-cost", placeholder="150.00", type="number", min=0.0001),
            ], width=2),
            dbc.Col([
                dbc.Label("目標價 (選填)", html_for="input-target"),
                dbc.Input(id="input-target", placeholder="200.00", type="number", min=0),
            ], width=2),
            dbc.Col([
                dbc.Label("\u00a0"),
                dbc.ButtonGroup([
                    dbc.Button("新增持倉", id="btn-add", color="primary", n_clicks=0),
                    dbc.Button("重新整理報價", id="btn-refresh", color="secondary", n_clicks=0),
                ], style={"display": "flex"}),
            ], width=4),
        ], align="end"),
        html.Div(id="form-error", className="text-danger mt-2"),
    ]),
    className="mb-3",
)

# ── Holdings Table ───────────────────────────────────────────────────
holdings_table = dbc.Card(
    dbc.CardBody([
        html.H5("持倉明細", className="card-title"),
        html.Div(id="holdings-table"),
    ]),
    className="mb-3",
)

# ── Charts ───────────────────────────────────────────────────────────
charts_section = dbc.Row([
    dbc.Col(dcc.Graph(id="chart-market-value"), width=4),
    dbc.Col(dcc.Graph(id="chart-sector"),       width=4),
    dbc.Col(dcc.Graph(id="chart-pnl"),          width=4),
])

# ── Summary Stats ────────────────────────────────────────────────────
summary_bar = dbc.Row(
    id="summary-stats",
    className="mb-3 text-center",
)

app.layout = dbc.Container([
    html.H3("股票觀察清單", className="my-3"),
    input_form,
    summary_bar,
    holdings_table,
    charts_section,
    # Hidden store for delete trigger
    dcc.Store(id="delete-store", data=None),
], fluid=True)

if __name__ == "__main__":
    app.run(debug=True, port=8052)
```

**Step 2: Verify layout loads**

Run: `python3 /Users/ph/stock_watchlist/app.py`
Open browser at `http://127.0.0.1:8052`
Expected: Dark-themed page with form and empty sections, no Python errors.
Stop with Ctrl-C.

**Step 3: Commit**

```bash
cd /Users/ph/stock_watchlist
git add app.py
git commit -m "feat: add Dash app layout skeleton"
```

---

### Task 5: app.py — helper renderers (table + charts)

**Files:**
- Modify: `app.py` (add helpers before `if __name__ == "__main__"`)

**Step 1: Add rendering helpers to app.py**

Insert the following before the `if __name__ == "__main__":` line:

```python
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, Input, Output, State, ALL, ctx
from data import (load_portfolio, save_portfolio, add_holding,
                  remove_holding, enrich_holdings)


def _fmt_pct(v):
    if v is None:
        return "N/A"
    color = "green" if v >= 0 else "red"
    sign = "+" if v >= 0 else ""
    return html.Span(f"{sign}{v:.2f}%", style={"color": color, "fontWeight": "bold"})


def _fmt_usd(v):
    if v is None:
        return "N/A"
    color = "green" if v >= 0 else "red"
    sign = "+" if v >= 0 else ""
    return html.Span(f"{sign}${v:,.2f}", style={"color": color})


def build_table(enriched: list[dict]):
    if not enriched:
        return dbc.Alert("尚無持倉，請新增股票。", color="info")

    header = html.Thead(html.Tr([
        html.Th("代碼"), html.Th("名稱"), html.Th("股數"),
        html.Th("成本"), html.Th("現價"), html.Th("市值"),
        html.Th("損益"), html.Th("報酬率"), html.Th("目標價"), html.Th(""),
    ]))

    rows = []
    for h in enriched:
        t = h["ticker"]
        target = h.get("target_price")
        cp = h.get("current_price")
        alert_badge = ""
        if target and cp and cp >= target:
            alert_badge = dbc.Badge("⚠️ 目標", color="warning", className="ms-1")

        row = html.Tr([
            html.Td(html.B(t)),
            html.Td(h.get("name", "")),
            html.Td(f"{h['shares']:g}"),
            html.Td(f"${h['cost_price']:,.2f}"),
            html.Td([f"${cp:,.2f}" if cp else "N/A", alert_badge]),
            html.Td(f"${h['market_value']:,.2f}" if h["market_value"] else "N/A"),
            html.Td(_fmt_usd(h.get("pnl"))),
            html.Td(_fmt_pct(h.get("pnl_pct"))),
            html.Td(f"${target:,.2f}" if target else "—"),
            html.Td(dbc.Button("✕", id={"type": "btn-delete", "ticker": t},
                               color="danger", size="sm", n_clicks=0)),
        ])
        rows.append(row)

    return dbc.Table([header, html.Tbody(rows)],
                     bordered=True, hover=True, responsive=True, size="sm")


def build_summary(enriched: list[dict]):
    total_cost = sum(h["cost_price"] * h["shares"] for h in enriched)
    total_value = sum(h["market_value"] for h in enriched if h["market_value"])
    total_pnl = sum(h["pnl"] for h in enriched if h["pnl"] is not None)
    total_pct = (total_pnl / total_cost * 100) if total_cost else 0

    def card(label, value_el):
        return dbc.Col(dbc.Card(dbc.CardBody([
            html.Small(label, className="text-muted"),
            html.Div(value_el, style={"fontSize": "1.3rem"}),
        ])), width=3)

    return [
        card("總成本", f"${total_cost:,.2f}"),
        card("總市值", f"${total_value:,.2f}"),
        card("總損益", _fmt_usd(total_pnl)),
        card("總報酬率", _fmt_pct(total_pct)),
    ]


def build_charts(enriched: list[dict]):
    bg = "rgba(0,0,0,0)"
    font_color = "#dee2e6"

    if not enriched:
        empty = go.Figure()
        empty.update_layout(paper_bgcolor=bg, plot_bgcolor=bg,
                            font_color=font_color,
                            annotations=[{"text": "無資料", "showarrow": False,
                                          "font": {"size": 16}}])
        return empty, empty, empty

    df = pd.DataFrame(enriched)

    # Chart 1: market value pie
    fig1 = px.pie(df[df["market_value"].notna()],
                  values="market_value", names="ticker",
                  title="市值分布", hole=0.35)
    fig1.update_layout(paper_bgcolor=bg, font_color=font_color)

    # Chart 2: sector pie
    sector_df = df[df["market_value"].notna()].copy()
    sector_df["sector"] = sector_df["sector"].fillna("Unknown")
    sector_agg = sector_df.groupby("sector")["market_value"].sum().reset_index()
    fig2 = px.pie(sector_agg, values="market_value", names="sector",
                  title="產業配置", hole=0.35)
    fig2.update_layout(paper_bgcolor=bg, font_color=font_color)

    # Chart 3: P&L bar
    pnl_df = df[df["pnl"].notna()].sort_values("pnl")
    colors = ["#e74c3c" if v < 0 else "#2ecc71" for v in pnl_df["pnl"]]
    fig3 = go.Figure(go.Bar(x=pnl_df["ticker"], y=pnl_df["pnl"],
                            marker_color=colors, name="損益"))
    fig3.update_layout(title="各股損益 (USD)", paper_bgcolor=bg,
                       plot_bgcolor=bg, font_color=font_color,
                       yaxis={"gridcolor": "#444"})

    return fig1, fig2, fig3
```

**Step 2: Verify no import errors**

Run:
```bash
cd /Users/ph/stock_watchlist
python3 -c "import app; print('helpers OK')"
```
Expected: `helpers OK`

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add table, summary and chart renderer helpers"
```

---

### Task 6: app.py — master callback

**Files:**
- Modify: `app.py` (append callback after helpers, before `if __name__`)

**Step 1: Append master callback to app.py**

Add after the helper functions:

```python
@callback(
    Output("holdings-table", "children"),
    Output("summary-stats", "children"),
    Output("chart-market-value", "figure"),
    Output("chart-sector", "figure"),
    Output("chart-pnl", "figure"),
    Output("form-error", "children"),
    Input("btn-add", "n_clicks"),
    Input("btn-refresh", "n_clicks"),
    Input({"type": "btn-delete", "ticker": ALL}, "n_clicks"),
    State("input-ticker", "value"),
    State("input-shares", "value"),
    State("input-cost", "value"),
    State("input-target", "value"),
    prevent_initial_call=False,
)
def master_callback(n_add, n_refresh, n_deletes,
                    ticker, shares, cost, target):
    holdings = load_portfolio()
    error = ""

    triggered_id = ctx.triggered_id

    # ── Add action ────────────────────────────────────────────────
    if triggered_id == "btn-add":
        if not ticker or not shares or not cost:
            error = "請填寫代碼、股數與成本價。"
        else:
            holdings = add_holding(holdings, ticker, float(shares),
                                   float(cost),
                                   float(target) if target else None)
            save_portfolio(holdings)

    # ── Delete action ─────────────────────────────────────────────
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-delete":
        del_ticker = triggered_id["ticker"]
        holdings = remove_holding(holdings, del_ticker)
        save_portfolio(holdings)

    # ── Refresh or initial load: just fetch prices ─────────────────
    # (falls through to enrich below)

    enriched = enrich_holdings(holdings) if holdings else []

    # Persist enriched name/sector back to file
    if enriched:
        plain = [{k: v for k, v in h.items()
                  if k not in ("current_price", "market_value", "pnl", "pnl_pct")}
                 for h in enriched]
        save_portfolio(plain)

    table = build_table(enriched)
    summary = build_summary(enriched) if enriched else []
    fig1, fig2, fig3 = build_charts(enriched)

    return table, summary, fig1, fig2, fig3, error
```

**Step 2: Full integration test**

Run: `python3 /Users/ph/stock_watchlist/app.py`
Open `http://127.0.0.1:8052`

Manual checks:
1. Add AAPL, 10 shares, cost 150 → row appears with live price
2. Add MSFT, 5 shares, cost 300 → second row + pie updates
3. Three charts visible with data
4. Summary bar shows total cost / value / P&L
5. Click ✕ on AAPL → row removed, charts update
6. Click "重新整理報價" → prices refresh
7. Close & reopen — MSFT still present (JSON persisted)

Stop with Ctrl-C.

**Step 3: Commit**

```bash
cd /Users/ph/stock_watchlist
git add app.py
git commit -m "feat: add master callback wiring add/delete/refresh actions"
```

---

### Task 7: Error handling & polish

**Files:**
- Modify: `app.py`

**Step 1: Add ticker validation in master_callback**

In the `if triggered_id == "btn-add":` block, after the blank field check, add:

```python
            # Validate ticker exists on yfinance
            from data import fetch_prices
            test = fetch_prices([ticker.upper().strip()])
            if not test or test[ticker.upper().strip()]["price"] is None:
                error = f"找不到股票代碼 '{ticker.upper()}'，請確認後重試。"
            else:
                holdings = add_holding(...)  # existing line
```

**Step 2: Add loading spinner to Refresh button**

Replace the Refresh button in `input_form`:

```python
dbc.Button(
    [dbc.Spinner(size="sm", id="spinner-refresh"), " 重新整理報價"],
    id="btn-refresh", color="secondary", n_clicks=0
),
```

**Step 3: Final smoke test**

Run: `python3 /Users/ph/stock_watchlist/app.py`
- Try adding ticker "FAKEXYZ123" → expect error message
- Add valid ticker → works normally

**Step 4: Final commit**

```bash
cd /Users/ph/stock_watchlist
git add app.py
git commit -m "feat: add ticker validation and refresh spinner"
```

---

### Task 8: Startup convenience script

**Files:**
- Create: `run.sh`

**Step 1: Create run.sh**

```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 app.py
```

**Step 2: Make executable**

```bash
chmod +x /Users/ph/stock_watchlist/run.sh
```

**Step 3: Test**

Run: `bash /Users/ph/stock_watchlist/run.sh`
Expected: Server starts on port 8052.
Stop with Ctrl-C.

**Step 4: Commit**

```bash
cd /Users/ph/stock_watchlist
git add run.sh
git commit -m "feat: add startup convenience script"
```

---

## Done Criteria

- `python3 app.py` starts without error on port 8052
- Adding a stock fetches live price, fills name/sector automatically
- Table shows 市值、損益、報酬率 in color
- Three charts: market value pie, sector pie, P&L bar
- Summary row shows totals
- Delete removes holding and refreshes charts
- Data persists across page reloads (JSON file)
- Invalid ticker shows inline error, does not crash
