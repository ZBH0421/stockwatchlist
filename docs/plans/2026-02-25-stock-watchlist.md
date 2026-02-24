# Stock Watchlist Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Dash web app at port 8052 for tracking a personal stock portfolio with live prices, P&L stats, and pie/bar charts.

**Architecture:** Single-page Dash app with two Python modules — `data.py` handles JSON persistence and yfinance batch fetching, `app.py` defines layout and a single master callback that rewrites the portfolio file and refreshes all UI components on each user action. A custom `assets/style.css` provides the design system; Dash auto-serves the `assets/` folder.

**Tech Stack:** Python 3.14, Dash 2.14+, Dash Bootstrap Components (DARKLY as base reset), Plotly, yfinance, pandas

**Design Direction — "Bloomberg Terminal"**
- Background: `#050609` near-black with subtle dot-grid texture
- Accent: `#F0B429` amber-gold borders, icons, highlights
- Gain: `#10B981` emerald · Loss: `#EF4444` red
- Display font: `Barlow Condensed` (condensed industrial sans) from Google Fonts
- Data/number font: `JetBrains Mono` (monospaced) from Google Fonts
- Zero border-radius on all containers · Thin 1px gold borders · Glow on hover
- Charts: dark Plotly template with amber/emerald/red palette

---

### Task 1: Project scaffolding & dependencies

**Files:**
- Create: `requirements.txt`
- Create: `portfolio.json`
- Create: `assets/` directory

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

**Step 3: Create assets directory**

```bash
mkdir -p /Users/ph/stock_watchlist/assets
```

**Step 4: Install dependencies**

Run: `pip3 install -r /Users/ph/stock_watchlist/requirements.txt`
Expected: All packages install without error.

**Step 5: Commit**

```bash
cd /Users/ph/stock_watchlist
git add requirements.txt portfolio.json assets/
git commit -m "feat: add project scaffolding and dependencies"
```

---

### Task 2: Design system — assets/style.css

**Files:**
- Create: `assets/style.css`

**Step 1: Create assets/style.css**

```css
/* ── Google Fonts ──────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Design Tokens ─────────────────────────────────────────────── */
:root {
  --bg:          #050609;
  --bg-card:     #0c0e13;
  --bg-hover:    #12151c;
  --border:      #F0B429;
  --border-dim:  rgba(240,180,41,0.2);
  --accent:      #F0B429;
  --gain:        #10B981;
  --loss:        #EF4444;
  --text:        #E8E8E8;
  --text-muted:  #5a6070;
  --font-display: 'Barlow Condensed', sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
}

/* ── Reset & Base ───────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

body {
  background-color: var(--bg);
  background-image: radial-gradient(rgba(240,180,41,0.04) 1px, transparent 1px);
  background-size: 28px 28px;
  color: var(--text);
  font-family: var(--font-display);
  min-height: 100vh;
  letter-spacing: 0.01em;
}

/* Override Bootstrap/DBC */
.container-fluid { background: transparent !important; }
.card { background: transparent !important; border: none !important; }

/* ── Typography ─────────────────────────────────────────────────── */
h1, h2, h3, h4, h5 {
  font-family: var(--font-display);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text);
}
.mono { font-family: var(--font-mono) !important; }

/* ── Page Title ─────────────────────────────────────────────────── */
.page-title {
  font-family: var(--font-display);
  font-size: 2.4rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  border-bottom: 1px solid var(--border-dim);
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}
.page-title span {
  color: var(--text-muted);
  font-weight: 300;
  font-size: 0.9rem;
  letter-spacing: 0.18em;
  display: block;
  margin-top: 0.15rem;
}

/* ── Panel Card ─────────────────────────────────────────────────── */
.panel {
  background: var(--bg-card);
  border: 1px solid var(--border-dim);
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
  position: relative;
  transition: border-color 0.2s;
}
.panel::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px; height: 100%;
  background: var(--accent);
}
.panel:hover { border-color: var(--border); }

.panel-label {
  font-family: var(--font-display);
  font-size: 0.65rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

/* ── Summary Stat Cards ─────────────────────────────────────────── */
.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-dim);
  padding: 1rem 1.25rem;
  position: relative;
  overflow: hidden;
  transition: border-color 0.25s, background 0.25s;
}
.stat-card:hover {
  border-color: var(--accent);
  background: var(--bg-hover);
}
.stat-card::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent), transparent);
}
.stat-label {
  font-size: 0.6rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.3rem;
}
.stat-value {
  font-family: var(--font-mono);
  font-size: 1.45rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1;
}
.stat-value.gain { color: var(--gain); }
.stat-value.loss { color: var(--loss); }

/* ── Input Form ─────────────────────────────────────────────────── */
.form-label {
  font-size: 0.6rem !important;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-muted) !important;
  margin-bottom: 0.35rem;
}
.form-control, .form-control:focus {
  background: #0a0c11 !important;
  border: 1px solid #1e2230 !important;
  border-radius: 0 !important;
  color: var(--text) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.85rem !important;
  box-shadow: none !important;
  transition: border-color 0.2s;
}
.form-control:focus {
  border-color: var(--accent) !important;
}
.form-control::placeholder { color: #2a2f3a !important; }

/* ── Buttons ────────────────────────────────────────────────────── */
.btn-terminal {
  background: transparent;
  border: 1px solid var(--accent);
  color: var(--accent);
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  border-radius: 0;
  padding: 0.55rem 1.1rem;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  white-space: nowrap;
}
.btn-terminal:hover {
  background: var(--accent);
  color: var(--bg);
  box-shadow: 0 0 12px rgba(240,180,41,0.4);
}
.btn-terminal.secondary {
  border-color: #1e2230;
  color: var(--text-muted);
}
.btn-terminal.secondary:hover {
  border-color: var(--text-muted);
  color: var(--text);
  background: transparent;
  box-shadow: none;
}
.btn-delete {
  background: transparent !important;
  border: 1px solid #1e2230 !important;
  color: var(--text-muted) !important;
  font-size: 0.7rem !important;
  border-radius: 0 !important;
  padding: 0.2rem 0.5rem !important;
  transition: border-color 0.2s, color 0.2s !important;
}
.btn-delete:hover {
  border-color: var(--loss) !important;
  color: var(--loss) !important;
}

/* ── Holdings Table ─────────────────────────────────────────────── */
.holdings-table { width: 100%; border-collapse: collapse; }
.holdings-table th {
  font-family: var(--font-display);
  font-size: 0.58rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-dim);
  padding: 0.5rem 0.75rem;
  white-space: nowrap;
}
.holdings-table td {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: var(--text);
  vertical-align: middle;
  transition: background 0.15s;
}
.holdings-table tr:hover td { background: var(--bg-hover); }
.ticker-cell {
  font-weight: 600;
  color: var(--accent);
  letter-spacing: 0.08em;
}
.name-cell {
  font-family: var(--font-display);
  font-size: 0.8rem;
  color: var(--text-muted);
  letter-spacing: 0.03em;
}
.gain-cell { color: var(--gain) !important; }
.loss-cell { color: var(--loss) !important; }
.alert-badge {
  display: inline-block;
  background: rgba(240,180,41,0.15);
  border: 1px solid var(--accent);
  color: var(--accent);
  font-size: 0.55rem;
  letter-spacing: 0.12em;
  padding: 0.1rem 0.35rem;
  margin-left: 0.4rem;
  text-transform: uppercase;
  vertical-align: middle;
}

/* ── Charts ─────────────────────────────────────────────────────── */
.chart-container {
  background: var(--bg-card);
  border: 1px solid var(--border-dim);
  padding: 0.5rem;
  position: relative;
}
.chart-container::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 2px;
  background: linear-gradient(90deg, var(--accent), transparent);
}

/* ── Error Alert ────────────────────────────────────────────────── */
.error-msg {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--loss);
  letter-spacing: 0.06em;
  margin-top: 0.5rem;
  min-height: 1.2rem;
}

/* ── Empty State ────────────────────────────────────────────────── */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
  font-size: 0.75rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  border: 1px dashed rgba(240,180,41,0.15);
}

/* ── Page Load Animation ────────────────────────────────────────── */
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.panel, .stat-card, .chart-container {
  animation: fadeSlideIn 0.35s ease both;
}
.stat-card:nth-child(1) { animation-delay: 0.05s; }
.stat-card:nth-child(2) { animation-delay: 0.10s; }
.stat-card:nth-child(3) { animation-delay: 0.15s; }
.stat-card:nth-child(4) { animation-delay: 0.20s; }
```

**Step 2: Verify file exists**

```bash
ls /Users/ph/stock_watchlist/assets/style.css
```
Expected: file listed.

**Step 3: Commit**

```bash
cd /Users/ph/stock_watchlist
git add assets/style.css
git commit -m "feat: add Bloomberg Terminal design system CSS"
```

---

### Task 3: data.py — JSON persistence helpers

**Files:**
- Create: `data.py`

**Step 1: Write data.py**

```python
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

### Task 4: data.py — yfinance price & info fetch

**Files:**
- Modify: `data.py` (append to bottom)

**Step 1: Append fetch functions to data.py**

```python
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
```

**Step 2: Smoke-test (needs network)**

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
Expected: dict with prices, `fetch OK`

**Step 3: Commit**

```bash
git add data.py
git commit -m "feat: add yfinance batch price and enrichment helpers"
```

---

### Task 5: app.py — Plotly chart template

**Files:**
- Create: `app.py` (initial file with chart template only)

**Step 1: Create app.py with template definition**

```python
"""app.py — Stock Watchlist Dash application."""
import plotly.graph_objects as go
import plotly.io as pio

# ── Bloomberg Terminal Plotly Theme ─────────────────────────────────
_COLORS = ["#F0B429", "#10B981", "#3B82F6", "#8B5CF6",
           "#EC4899", "#14B8A6", "#F97316", "#EF4444"]

pio.templates["bloomberg"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", color="#E8E8E8", size=11),
        title=dict(font=dict(family="Barlow Condensed, sans-serif",
                             size=13, color="#5a6070"),
                   x=0.01, xanchor="left"),
        colorway=_COLORS,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.06)",
                    borderwidth=1),
        margin=dict(l=30, r=20, t=40, b=30),
        xaxis=dict(gridcolor="#1a1d26", linecolor="#1a1d26",
                   tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#1a1d26", linecolor="#1a1d26",
                   tickfont=dict(size=10)),
        hoverlabel=dict(bgcolor="#0c0e13", bordercolor="#F0B429",
                        font=dict(family="JetBrains Mono", size=11)),
    )
)
pio.templates.default = "bloomberg"
```

**Step 2: Verify template loads**

Run:
```bash
cd /Users/ph/stock_watchlist
python3 -c "import app; print('template OK')"
```
Expected: `template OK`

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add Bloomberg Plotly chart theme"
```

---

### Task 6: app.py — layout

**Files:**
- Modify: `app.py` (append layout after template)

**Step 1: Append imports and layout to app.py**

```python
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="WATCHLIST",
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
)

# ── Input Form ───────────────────────────────────────────────────────
input_form = html.Div(className="panel", children=[
    html.Div("New Position", className="panel-label"),
    dbc.Row([
        dbc.Col([
            html.Label("Ticker", className="form-label"),
            dbc.Input(id="input-ticker", placeholder="AAPL", type="text",
                      className="form-control",
                      style={"textTransform": "uppercase"}),
        ], width=2),
        dbc.Col([
            html.Label("Shares", className="form-label"),
            dbc.Input(id="input-shares", placeholder="10", type="number",
                      min=0.0001, className="form-control"),
        ], width=2),
        dbc.Col([
            html.Label("Cost Price (USD)", className="form-label"),
            dbc.Input(id="input-cost", placeholder="150.00", type="number",
                      min=0.0001, className="form-control"),
        ], width=2),
        dbc.Col([
            html.Label("Target Price (opt.)", className="form-label"),
            dbc.Input(id="input-target", placeholder="200.00", type="number",
                      min=0, className="form-control"),
        ], width=2),
        dbc.Col([
            html.Label("\u00a0", className="form-label"),
            html.Div([
                html.Button("+ Add Position", id="btn-add", n_clicks=0,
                            className="btn-terminal me-2"),
                html.Button("↺ Refresh", id="btn-refresh", n_clicks=0,
                            className="btn-terminal secondary"),
            ], style={"display": "flex", "alignItems": "center"}),
        ], width=4, className="d-flex align-items-end"),
    ], align="end"),
    html.Div(id="form-error", className="error-msg"),
])

# ── Summary Stats ─────────────────────────────────────────────────────
summary_bar = dbc.Row(id="summary-stats", className="mb-3 g-2")

# ── Holdings Table ────────────────────────────────────────────────────
holdings_section = html.Div(className="panel", children=[
    html.Div("Portfolio Positions", className="panel-label"),
    html.Div(id="holdings-table"),
])

# ── Charts ────────────────────────────────────────────────────────────
charts_section = dbc.Row([
    dbc.Col(html.Div(dcc.Graph(id="chart-market-value",
                               config={"displayModeBar": False}),
                     className="chart-container"), width=4),
    dbc.Col(html.Div(dcc.Graph(id="chart-sector",
                               config={"displayModeBar": False}),
                     className="chart-container"), width=4),
    dbc.Col(html.Div(dcc.Graph(id="chart-pnl",
                               config={"displayModeBar": False}),
                     className="chart-container"), width=4),
], className="g-2 mb-3")

app.layout = dbc.Container([
    # Header
    html.Div([
        html.Div([
            html.Span("WATCHLIST", style={"color": "#F0B429"}),
            html.Span(" /  PORTFOLIO TRACKER"),
        ], className="page-title"),
    ]),
    input_form,
    summary_bar,
    holdings_section,
    charts_section,
], fluid=True, style={"padding": "1.5rem 2rem"})

if __name__ == "__main__":
    app.run(debug=True, port=8052)
```

**Step 2: Verify layout renders**

Run: `python3 /Users/ph/stock_watchlist/app.py`
Open `http://127.0.0.1:8052`
Expected: Dark terminal-style page with amber accents, dot-grid background, custom fonts. Stop with Ctrl-C.

**Step 3: Commit**

```bash
cd /Users/ph/stock_watchlist
git add app.py
git commit -m "feat: add terminal-style Dash layout"
```

---

### Task 7: app.py — rendering helpers

**Files:**
- Modify: `app.py` (insert helpers before `if __name__`)

**Step 1: Add rendering helpers before the `if __name__` line**

```python
import pandas as pd
import plotly.express as px
from dash import callback, Input, Output, State, ALL, ctx
from data import (load_portfolio, save_portfolio, add_holding,
                  remove_holding, enrich_holdings)


def _pct_span(v):
    if v is None:
        return html.Span("N/A", style={"color": "#5a6070"})
    cls = "gain-cell" if v >= 0 else "loss-cell"
    sign = "+" if v >= 0 else ""
    return html.Span(f"{sign}{v:.2f}%", className=cls)


def _usd_span(v):
    if v is None:
        return html.Span("N/A", style={"color": "#5a6070"})
    cls = "gain-cell" if v >= 0 else "loss-cell"
    sign = "+" if v >= 0 else ""
    return html.Span(f"{sign}${v:,.2f}", className=cls)


def build_table(enriched: list[dict]):
    if not enriched:
        return html.Div("No positions. Add your first stock above.",
                        className="empty-state")

    header = html.Thead(html.Tr([
        html.Th(t) for t in
        ["TICKER", "NAME", "SHARES", "COST", "PRICE",
         "MKT VALUE", "P&L", "RETURN", "TARGET", ""]
    ]))

    rows = []
    for h in enriched:
        t = h["ticker"]
        target = h.get("target_price")
        cp = h.get("current_price")

        target_cell = []
        if target:
            target_cell.append(f"${target:,.2f}")
            if cp and cp >= target:
                target_cell.append(
                    html.Span("TARGET HIT", className="alert-badge"))

        row = html.Tr([
            html.Td(t, className="ticker-cell"),
            html.Td(h.get("name", ""), className="name-cell"),
            html.Td(f"{h['shares']:g}"),
            html.Td(f"${h['cost_price']:,.2f}"),
            html.Td(f"${cp:,.2f}" if cp else "—"),
            html.Td(f"${h['market_value']:,.2f}" if h["market_value"] else "—"),
            html.Td(_usd_span(h.get("pnl"))),
            html.Td(_pct_span(h.get("pnl_pct"))),
            html.Td(target_cell),
            html.Td(html.Button("✕", id={"type": "btn-delete", "ticker": t},
                                className="btn-delete", n_clicks=0)),
        ])
        rows.append(row)

    return html.Table([header, html.Tbody(rows)], className="holdings-table")


def build_summary(enriched: list[dict]):
    total_cost = sum(h["cost_price"] * h["shares"] for h in enriched)
    total_value = sum(h["market_value"] for h in enriched
                      if h["market_value"] is not None)
    total_pnl = sum(h["pnl"] for h in enriched if h["pnl"] is not None)
    total_pct = (total_pnl / total_cost * 100) if total_cost else 0

    def stat(label, value, extra_class=""):
        return dbc.Col(
            html.Div([
                html.Div(label, className="stat-label"),
                html.Div(value, className=f"stat-value {extra_class}"),
            ], className="stat-card"),
            width=3,
        )

    pnl_class = "gain" if total_pnl >= 0 else "loss"
    return [
        stat("TOTAL COST",     f"${total_cost:,.2f}"),
        stat("MARKET VALUE",   f"${total_value:,.2f}"),
        stat("TOTAL P&L",      f"{'+'if total_pnl>=0 else ''}${total_pnl:,.2f}",
             pnl_class),
        stat("TOTAL RETURN",
             f"{'+'if total_pct>=0 else ''}{total_pct:.2f}%", pnl_class),
    ]


def _empty_fig(label="NO DATA"):
    fig = go.Figure()
    fig.add_annotation(text=label, showarrow=False,
                       font=dict(size=11, color="#5a6070",
                                 family="Barlow Condensed"),
                       xref="paper", yref="paper", x=0.5, y=0.5)
    return fig


def build_charts(enriched: list[dict]):
    if not enriched:
        return _empty_fig(), _empty_fig(), _empty_fig()

    df = pd.DataFrame(enriched)

    # Chart 1: market value pie
    mv_df = df[df["market_value"].notna()]
    fig1 = px.pie(mv_df, values="market_value", names="ticker",
                  title="MARKET VALUE", hole=0.42,
                  color_discrete_sequence=_COLORS)
    fig1.update_traces(textfont_family="JetBrains Mono",
                       hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<extra></extra>")

    # Chart 2: sector pie
    s_df = mv_df.copy()
    s_df["sector"] = s_df["sector"].fillna("Unknown")
    sector_agg = s_df.groupby("sector")["market_value"].sum().reset_index()
    fig2 = px.pie(sector_agg, values="market_value", names="sector",
                  title="SECTOR", hole=0.42,
                  color_discrete_sequence=_COLORS[1:] + _COLORS[:1])
    fig2.update_traces(textfont_family="JetBrains Mono")

    # Chart 3: P&L bar
    pnl_df = df[df["pnl"].notna()].sort_values("pnl")
    colors = [("#10B981" if v >= 0 else "#EF4444") for v in pnl_df["pnl"]]
    fig3 = go.Figure(go.Bar(
        x=pnl_df["ticker"], y=pnl_df["pnl"],
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>P&L: $%{y:,.2f}<extra></extra>",
    ))
    fig3.update_layout(title_text="P&L", bargap=0.35,
                       yaxis_tickprefix="$")

    return fig1, fig2, fig3
```

**Step 2: Verify no import errors**

```bash
python3 -c "import app; print('helpers OK')"
```
Expected: `helpers OK`

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add terminal-styled table, summary, and chart helpers"
```

---

### Task 8: app.py — master callback

**Files:**
- Modify: `app.py` (insert before `if __name__`)

**Step 1: Append master callback**

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

    if triggered_id == "btn-add":
        if not ticker or not shares or not cost:
            error = "ERR: ticker, shares, and cost are required."
        else:
            from data import fetch_prices
            t_up = ticker.upper().strip()
            test = fetch_prices([t_up])
            if not test or test[t_up]["price"] is None:
                error = f"ERR: ticker '{t_up}' not found on yfinance."
            else:
                holdings = add_holding(holdings, t_up, float(shares),
                                       float(cost),
                                       float(target) if target else None)
                save_portfolio(holdings)

    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-delete":
        holdings = remove_holding(holdings, triggered_id["ticker"])
        save_portfolio(holdings)

    enriched = enrich_holdings(holdings) if holdings else []

    # Persist auto-filled name/sector back to JSON
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
1. Page loads with dot-grid background, amber accents, custom fonts
2. Add NVDA, 10, 450 → row appears with amber ticker, live price, colored P&L
3. Add MSFT, 5, 300 → two rows, pie charts show both
4. Summary cards update with total cost/value/P&L/return
5. Click ✕ on NVDA → row removed, charts update
6. "↺ Refresh" button updates prices
7. Add "FAKEXYZ" → error message in mono font
8. Close browser → reopen → MSFT still present

Stop with Ctrl-C.

**Step 3: Commit**

```bash
cd /Users/ph/stock_watchlist
git add app.py
git commit -m "feat: wire master callback for add/delete/refresh"
```

---

### Task 9: Startup script

**Files:**
- Create: `run.sh`

**Step 1: Create run.sh**

```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 app.py
```

**Step 2: Make executable and test**

```bash
chmod +x /Users/ph/stock_watchlist/run.sh
bash /Users/ph/stock_watchlist/run.sh
```
Expected: Server on port 8052. Stop with Ctrl-C.

**Step 3: Commit**

```bash
cd /Users/ph/stock_watchlist
git add run.sh
git commit -m "feat: add startup script"
```

---

## Done Criteria

- `python3 app.py` starts on port 8052
- Bloomberg Terminal dark aesthetic: dot-grid bg, amber borders, `Barlow Condensed` + `JetBrains Mono`
- Adding a stock: validates ticker, fetches live price, auto-fills name/sector
- Table: amber ticker, muted name, colored P&L/return, TARGET HIT badge
- Three charts with Bloomberg Plotly theme: market value pie, sector pie, P&L bar
- Summary stats row: total cost, market value, P&L, return
- Delete removes holding; Refresh re-fetches prices
- Data persists across reloads via `portfolio.json`
- Invalid ticker shows `ERR:` message in mono red font
