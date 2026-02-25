# Design: Bloomberg ↔ MUJI Theme Toggle

**Date:** 2026-02-25
**Status:** Approved

## Goal

Add a MUJI-inspired light theme alongside the existing Bloomberg Terminal dark theme, with a toggle button to switch between them instantly without page reload.

## Architecture

```
dcc.Store(id="theme-store", data="dark")
    ↓
clientside_callback → sets body className ("theme-dark" or "theme-light")
    ↓
CSS variables switch under .theme-dark / .theme-light
    ↓
master_callback gains Input("theme-store") → switches Plotly template for charts
```

A small toggle callback handles: button click → flip theme-store value.
A clientside callback handles: theme-store value → body className (instant, no round-trip).

## CSS Token Map

| Token         | Dark (Bloomberg)     | Light (MUJI)         |
|---------------|----------------------|----------------------|
| `--bg`        | `#0f1117`            | `#F5F3EF` warm ecru  |
| `--bg-card`   | `#181b24`            | `#EDEAE3` cream      |
| `--bg-hover`  | `#1e2230`            | `#E4E0D8` light sand |
| `--border`    | `#F0B429` gold       | `#2C2A27` charcoal   |
| `--border-dim`| `rgba(240,180,41,.3)`| `rgba(44,42,39,.15)` |
| `--accent`    | `#F0B429`            | `#2C2A27`            |
| `--text`      | `#F0F0F0`            | `#2C2A27`            |
| `--text-muted`| `#7a8494`            | `#9C9890`            |
| `--gain`      | `#10B981` green      | `#2C2A27` bold       |
| `--loss`      | `#EF4444` red        | `#9C9890` light      |

## Typography (light mode only)

- Add Google Font: `Source Serif 4` (weights 300, 400)
- Panel labels, column headers, page title → `Source Serif 4`
- Numbers, tickers, amounts → keep `JetBrains Mono`
- Page title in light mode: `Source Serif 4` weight 300, natural case (not uppercase)

## P&L Direction (light mode)

No green/red colors. Direction shown by:
- Gain: `font-weight: 600`, `color: var(--text)`, prefix `+`
- Loss: `font-weight: 400`, `color: var(--text-muted)`, prefix `−`

## Toggle Button

Placed in the header row, right-aligned, same line as `WATCHLIST` title:

```
WATCHLIST  /  PORTFOLIO TRACKER          [● TERMINAL  ○ MUJI]
```

- Two labels side by side, active one underlined
- No background fill, no border box
- Dark mode: gold color; Light mode: charcoal color
- Smooth 0.3s CSS transition on color change

## Plotly Chart Theme

- Add a `"muji"` Plotly template alongside the existing `"bloomberg"` template
- `paper_bgcolor` / `plot_bgcolor`: `"rgba(0,0,0,0)"` (inherits from CSS)
- Font: `Source Serif 4` for titles, `JetBrains Mono` for tick labels
- `colorway`: muted earth tones `["#A0998E", "#6B6560", "#C4B9AA", "#8C8882", "#D4CEC6", "#4A4540", "#B8AFA6", "#7A7470"]`
- Grid lines: `#D4CEC6`
- master_callback selects template based on `theme-store` value

## Files Changed

- `assets/style.css` — add `.theme-dark` / `.theme-light` variable blocks, new font import, gain/loss light-mode rules, toggle button styles, CSS transitions
- `app.py` — add `dcc.Store`, toggle button in header, clientside_callback, muji Plotly template, theme input to master_callback
