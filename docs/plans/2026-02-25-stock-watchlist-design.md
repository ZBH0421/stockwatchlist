# Stock Watchlist — Design Document
Date: 2026-02-25

## Overview
A standalone Dash web application for tracking a personal stock portfolio.
Users input ticker, shares, and cost price; the app fetches live prices via yfinance
and displays portfolio analytics including pie charts and P&L statistics.

## Tech Stack
- **Framework**: Dash (Python) + Dash Bootstrap Components (DARKLY theme)
- **Charts**: Plotly
- **Data Source**: yfinance (batch fetch on demand)
- **Storage**: Local `portfolio.json` file (server-side read/write)
- **Port**: 8052

## Project Structure
```
stock_watchlist/
├── app.py           # Dash app, layout, callbacks
├── data.py          # yfinance fetch + JSON read/write helpers
├── portfolio.json   # Persisted holdings (auto-created on first run)
├── requirements.txt
└── docs/plans/
    └── 2026-02-25-stock-watchlist-design.md
```

## Data Model

### portfolio.json schema
```json
[
  {
    "ticker": "NVDA",
    "name": "NVIDIA Corp",          // auto-filled by yfinance
    "sector": "Technology",         // auto-filled by yfinance
    "shares": 10,
    "cost_price": 450.00,
    "target_price": 600.00          // optional, for alert highlight
  }
]
```

## UI Layout

### Section 1: Input Form (top)
- Text input: Ticker symbol
- Number input: Shares
- Number input: Cost price per share
- Number input: Target price (optional)
- Buttons: "新增持倉" (Add) / "重新整理報價" (Refresh Quotes)

### Section 2: Holdings Table (middle)
Columns: 代碼 | 名稱 | 股數 | 成本 | 現價 | 市值 | 損益 | 報酬率 | 刪除

Display rules:
- 報酬率 colored red (negative) / green (positive)
- 現價 ≥ 目標價 → row highlighted with ⚠️ badge
- 市值 = shares × current_price
- 損益 = (current_price - cost_price) × shares
- 報酬率 = (current_price - cost_price) / cost_price × 100%

### Section 3: Charts (bottom, 3-column grid)
1. **市值圓餅圖** — slice per ticker, sized by market value
2. **產業配置圓餅圖** — slice per sector (from yfinance info)
3. **損益長條圖** — one bar per ticker, green=profit / red=loss

## Callback Architecture

Single callback triggered by:
- Add button click
- Delete button click (per row)
- Refresh button click

Flow:
```
Trigger → validate inputs → write/update portfolio.json
        → batch fetch prices via yfinance
        → compute derived fields (市值, 損益, 報酬率)
        → return: updated table + 3 figures
```

Price refresh: **manual only** (button-triggered). No auto-polling to avoid yfinance rate limiting.

## Error Handling
- Invalid ticker → show inline error message, do not add to portfolio
- yfinance fetch failure → show last known price or "N/A", display warning banner
- Empty portfolio → show empty state message with prompt to add first holding

## Requirements
```
dash>=2.14
dash-bootstrap-components>=1.5
plotly>=5.18
yfinance>=0.2.36
pandas>=2.0
```
