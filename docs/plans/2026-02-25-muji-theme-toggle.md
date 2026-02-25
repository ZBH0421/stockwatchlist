# MUJI Theme Toggle Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a MUJI warm-light theme alongside the Bloomberg dark theme, switchable via a header toggle button with no page reload.

**Architecture:** CSS custom properties are scoped under `.theme-dark` / `.theme-light` on `document.body`; a `dcc.Store` holds the current theme; a clientside callback applies the class instantly; the master chart callback re-selects the correct Plotly template based on theme.

**Tech Stack:** Plotly Dash, dash-bootstrap-components (DARKLY), Plotly, CSS custom properties, clientside callbacks

---

## Task 1: Restructure CSS variables into theme classes

**Files:**
- Modify: `assets/style.css`

Current code has all tokens in `:root {}`. We must move them into scoped classes so toggling body className swaps all tokens at once.

**Step 1: Replace `:root` block**

In `assets/style.css`, replace lines 5–18 (the `:root { ... }` block) with:

```css
/* ── Design Tokens: Dark (Bloomberg Terminal) ───────────────────── */
.theme-dark {
  --bg:          #0f1117;
  --bg-card:     #181b24;
  --bg-hover:    #1e2230;
  --border:      #F0B429;
  --border-dim:  rgba(240,180,41,0.3);
  --accent:      #F0B429;
  --gain:        #10B981;
  --loss:        #EF4444;
  --text:        #F0F0F0;
  --text-muted:  #7a8494;
  --font-display: 'Barlow Condensed', sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
  --font-serif:   'Barlow Condensed', sans-serif;
}

/* ── Design Tokens: Light (MUJI Natural) ────────────────────────── */
.theme-light {
  --bg:          #F5F3EF;
  --bg-card:     #EDEAE3;
  --bg-hover:    #E4E0D8;
  --border:      #2C2A27;
  --border-dim:  rgba(44,42,39,0.15);
  --accent:      #2C2A27;
  --gain:        #2C2A27;
  --loss:        #9C9890;
  --text:        #2C2A27;
  --text-muted:  #9C9890;
  --font-display: 'Barlow Condensed', sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
  --font-serif:   'Source Serif 4', serif;
}
```

**Step 2: Add Source Serif 4 to the font import**

Replace line 2 (the `@import` line):

```css
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&family=Source+Serif+4:wght@300;400&display=swap');
```

**Step 3: Add transition to body for smooth swap**

After the `body { ... }` block, add:

```css
body {
  transition: background-color 0.3s ease, color 0.3s ease;
}
```

**Step 4: Neutralise the dark dot pattern in light mode**

Add after the existing `body { ... }` block:

```css
.theme-light body,
body.theme-light {
  background-image: none;
}
```

**Step 5: Verify no `:root` block remains**

Search for `:root` in `assets/style.css` — it must be gone. All tokens must be under `.theme-dark` or `.theme-light`.

**Step 6: Commit**

```bash
git add assets/style.css
git commit -m "style: move CSS tokens into theme-dark / theme-light classes"
```

---

## Task 2: Add light-mode typography and gain/loss overrides

**Files:**
- Modify: `assets/style.css`

**Step 1: Add light-mode typography overrides at end of file**

```css
/* ── Light Mode: MUJI Typography Overrides ─────────────────────── */
.theme-light .panel-label,
.theme-light .stat-label,
.theme-light .holdings-table th,
.theme-light .form-label {
  font-family: var(--font-serif) !important;
  text-transform: none;
  letter-spacing: 0.04em;
  font-weight: 400;
}

.theme-light .page-title {
  font-family: var(--font-serif) !important;
  font-weight: 300;
  text-transform: none;
  letter-spacing: 0.02em;
  font-size: 2rem;
}

.theme-light .page-title span {
  font-family: var(--font-serif) !important;
  letter-spacing: 0.04em;
}
```

**Step 2: Add light-mode gain/loss weight overrides**

```css
/* ── Light Mode: P&L Direction via Weight, Not Color ────────────── */
.theme-light .gain-cell {
  color: var(--gain) !important;
  font-weight: 600;
}
.theme-light .loss-cell {
  color: var(--loss) !important;
  font-weight: 400;
}
```

**Step 3: Add Bootstrap override for light mode**

Bootstrap DARKLY sets `color: #dee2e6` on inputs and other elements. Override:

```css
/* ── Light Mode: Bootstrap DARKLY overrides ─────────────────────── */
.theme-light .form-control,
.theme-light .form-control:focus {
  background: #F0EDE6 !important;
  border-color: rgba(44,42,39,0.2) !important;
  color: #2C2A27 !important;
}
.theme-light .form-control::placeholder {
  color: #B8B4AE !important;
}
.theme-light .btn-terminal {
  border-color: #2C2A27 !important;
  color: #2C2A27 !important;
}
.theme-light .btn-terminal:hover {
  background: #2C2A27 !important;
  color: #F5F3EF !important;
  box-shadow: none !important;
}
.theme-light .btn-terminal.secondary {
  border-color: rgba(44,42,39,0.25) !important;
  color: var(--text-muted) !important;
}
.theme-light .alert-badge {
  background: rgba(44,42,39,0.08) !important;
  border-color: #2C2A27 !important;
  color: #2C2A27 !important;
}
.theme-light .empty-state {
  border-color: rgba(44,42,39,0.2);
  color: var(--text-muted);
}
```

**Step 4: Add CSS transitions on panels and cards**

After existing `.panel, .stat-card, .chart-container { animation: ... }` block add:

```css
.panel, .stat-card, .chart-container, .holdings-table td {
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}
```

**Step 5: Commit**

```bash
git add assets/style.css
git commit -m "style: add MUJI light mode typography and component overrides"
```

---

## Task 3: Add toggle button styles

**Files:**
- Modify: `assets/style.css`

**Step 1: Add header layout and toggle button styles at end of file**

```css
/* ── Header Row ─────────────────────────────────────────────────── */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

/* ── Theme Toggle Button ────────────────────────────────────────── */
.btn-theme-toggle {
  background: transparent;
  border: none;
  padding: 0.25rem 0;
  cursor: pointer;
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-top: 0.6rem;
}
.btn-theme-toggle .toggle-opt {
  font-family: var(--font-display);
  font-size: 0.65rem;
  font-weight: 400;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-muted);
  transition: color 0.3s ease;
  padding-bottom: 2px;
  border-bottom: 1px solid transparent;
  transition: color 0.3s, border-color 0.3s;
}
.btn-theme-toggle .toggle-opt.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
```

**Step 2: Commit**

```bash
git add assets/style.css
git commit -m "style: add theme toggle button styles"
```

---

## Task 4: Write failing tests for theme toggle logic

**Files:**
- Create: `tests/test_theme_toggle.py`

These tests cover the Python callback logic before we write it.

**Step 1: Create test file**

```python
"""tests/test_theme_toggle.py — Unit tests for theme toggle callback."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_toggle_dark_to_light():
    """Clicking toggle while in dark mode should return light."""
    from app import toggle_theme
    result = toggle_theme(1, "dark")
    assert result == "light"


def test_toggle_light_to_dark():
    """Clicking toggle while in light mode should return dark."""
    from app import toggle_theme
    result = toggle_theme(1, "light")
    assert result == "dark"


def test_toggle_no_click():
    """n_clicks=0 on initial load should return dark (unchanged)."""
    from app import toggle_theme
    result = toggle_theme(0, "dark")
    assert result == "dark"


def test_chart_template_dark():
    """build_charts should use 'bloomberg' template in dark mode."""
    from app import get_chart_template
    assert get_chart_template("dark") == "bloomberg"


def test_chart_template_light():
    """build_charts should use 'muji' template in light mode."""
    from app import get_chart_template
    assert get_chart_template("light") == "muji"
```

**Step 2: Run tests to confirm they fail**

```bash
cd /Users/ph/stock_watchlist
python3 -m pytest tests/test_theme_toggle.py -v
```

Expected output: `ImportError` or `AttributeError: module 'app' has no attribute 'toggle_theme'` — this is correct, the functions don't exist yet.

**Step 3: Commit the failing tests**

```bash
git add tests/test_theme_toggle.py
git commit -m "test: add failing tests for theme toggle and template selection"
```

---

## Task 5: Add MUJI Plotly template and helper functions to app.py

**Files:**
- Modify: `app.py`

**Step 1: Add MUJI Plotly template**

After line 29 (`pio.templates.default = "bloomberg"`), add:

```python
_MUJI_COLORS = ["#A0998E", "#6B6560", "#C4B9AA", "#8C8882",
                "#D4CEC6", "#4A4540", "#B8AFA6", "#7A7470"]

pio.templates["muji"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", color="#2C2A27", size=11),
        title=dict(font=dict(family="Source Serif 4, serif",
                             size=13, color="#9C9890"),
                   x=0.01, xanchor="left"),
        colorway=_MUJI_COLORS,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(44,42,39,0.15)",
                    borderwidth=1),
        margin=dict(l=30, r=20, t=40, b=30),
        xaxis=dict(gridcolor="#D4CEC6", linecolor="#D4CEC6",
                   tickfont=dict(size=10)),
        yaxis=dict(gridcolor="#D4CEC6", linecolor="#D4CEC6",
                   tickfont=dict(size=10)),
        hoverlabel=dict(bgcolor="#EDEAE3", bordercolor="#2C2A27",
                        font=dict(family="JetBrains Mono", size=11,
                                  color="#2C2A27")),
    )
)
```

**Step 2: Add the two helper functions that tests expect**

Add these two functions anywhere before the `@callback` decorator (after imports, before layout):

```python
def get_chart_template(theme: str) -> str:
    """Return the Plotly template name for the given theme."""
    return "bloomberg" if theme == "dark" else "muji"


def toggle_theme(n_clicks: int, current_theme: str) -> str:
    """Flip theme between dark and light; no-op if n_clicks is 0."""
    if not n_clicks:
        return current_theme
    return "light" if current_theme == "dark" else "dark"
```

**Step 3: Run the tests — they should pass now**

```bash
cd /Users/ph/stock_watchlist
python3 -m pytest tests/test_theme_toggle.py -v
```

Expected: all 5 tests PASS.

**Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add MUJI plotly template and theme helper functions"
```

---

## Task 6: Update layout — add dcc.Store, header toggle button, hidden dummy div

**Files:**
- Modify: `app.py`

**Step 1: Add imports at top of callback section**

After `from dash import callback, Input, Output, State, ALL, ctx` (around line 118), add `clientside_callback` to the import:

```python
from dash import callback, clientside_callback, Input, Output, State, ALL, ctx
```

**Step 2: Add dcc.Store and hidden dummy to layout**

Find `app.layout = dbc.Container([` and update it:

```python
app.layout = dbc.Container([
    dcc.Store(id="theme-store", data="dark"),
    html.Div(id="theme-dummy", style={"display": "none"}),
    html.Div([
        html.Div([
            html.Span("WATCHLIST", id="title-watchlist",
                      style={"color": "#F0B429"}),
            html.Span(" /  PORTFOLIO TRACKER"),
        ], className="page-title"),
        html.Button([
            html.Span("Terminal", id="toggle-dark-label",
                      className="toggle-opt active"),
            html.Span("Muji", id="toggle-light-label",
                      className="toggle-opt"),
        ], id="btn-theme-toggle", n_clicks=0,
           className="btn-theme-toggle"),
    ], className="header-row"),
    input_form,
    summary_bar,
    holdings_section,
    charts_section,
], fluid=True, style={"padding": "1.5rem 2rem"})
```

**Step 3: Add clientside callback to apply body className**

After the layout, add:

```python
clientside_callback(
    """
    function(theme) {
        document.body.className = 'theme-' + theme;
        return '';
    }
    """,
    Output("theme-dummy", "children"),
    Input("theme-store", "data"),
)
```

**Step 4: Add toggle callback**

```python
@callback(
    Output("theme-store", "data"),
    Output("toggle-dark-label", "className"),
    Output("toggle-light-label", "className"),
    Output("title-watchlist", "style"),
    Input("btn-theme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def cb_toggle_theme(n_clicks, current_theme):
    new_theme = toggle_theme(n_clicks, current_theme)
    dark_cls = "toggle-opt active" if new_theme == "dark" else "toggle-opt"
    light_cls = "toggle-opt active" if new_theme == "light" else "toggle-opt"
    title_color = "#F0B429" if new_theme == "dark" else "#2C2A27"
    return new_theme, dark_cls, light_cls, {"color": title_color}
```

**Step 5: Verify app starts without error**

```bash
cd /Users/ph/stock_watchlist
python3 app.py &
sleep 3
kill %1
```

No ImportError or AttributeError should appear.

**Step 6: Commit**

```bash
git add app.py
git commit -m "feat: add theme store, toggle button, and clientside body class callback"
```

---

## Task 7: Update build_charts to use correct Plotly template

**Files:**
- Modify: `app.py`

The `build_charts` function currently uses the global default template. We need it to use the theme-appropriate one.

**Step 1: Update build_charts signature**

Find `def build_charts(enriched: list[dict]):` and change to:

```python
def build_charts(enriched: list[dict], theme: str = "dark"):
```

**Step 2: Add template variable at top of build_charts**

Add as first line inside the function (after the `if not enriched:` guard):

```python
    tmpl = get_chart_template(theme)
    colors = _COLORS if theme == "dark" else _MUJI_COLORS
```

**Step 3: Update each figure to use the template**

Replace `color_discrete_sequence=_COLORS` with `color_discrete_sequence=colors` in both `px.pie()` calls.

Replace the `fig3` bar chart color logic:

```python
    bar_colors = (["#10B981" if v >= 0 else "#EF4444" for v in pnl_df["pnl"]]
                  if theme == "dark"
                  else ["#6B6560" if v >= 0 else "#B8AFA6" for v in pnl_df["pnl"]])
    fig3 = go.Figure(go.Bar(
        x=pnl_df["ticker"], y=pnl_df["pnl"],
        marker_color=bar_colors,
        hovertemplate="<b>%{x}</b><br>P&L: $%{y:,.2f}<extra></extra>",
    ))
```

Add `template=tmpl` to all three figures' `update_layout` calls:

```python
    fig1.update_layout(template=tmpl)
    fig2.update_layout(template=tmpl)
    fig3.update_layout(title_text="P&L", bargap=0.35,
                       yaxis_tickprefix="$", template=tmpl)
```

**Step 4: Update master_callback to pass theme to build_charts**

Find the `def master_callback(...)` function. Add `theme` as a new parameter by adding to the decorator and signature:

In the `@callback` decorator, add after the last `State`:
```python
    State("theme-store", "data"),
```

Change the function signature:
```python
def master_callback(n_add, n_refresh, n_deletes,
                    ticker, shares, cost, target, theme):
```

Change the call to `build_charts`:
```python
    fig1, fig2, fig3 = build_charts(enriched, theme or "dark")
```

**Step 5: Run all tests**

```bash
cd /Users/ph/stock_watchlist
python3 -m pytest tests/test_theme_toggle.py -v
```

Expected: all 5 PASS.

**Step 6: Start app and verify toggle works visually**

```bash
cd /Users/ph/stock_watchlist
bash run.sh
```

Open http://127.0.0.1:8052, click the toggle button. Verify:
- Background changes from dark to warm ecru
- Charts recolor to earth tones
- Toggle labels update (active underline moves)
- P&L numbers change weight instead of color
- Switching back to Terminal restores full Bloomberg look

**Step 7: Commit**

```bash
git add app.py
git commit -m "feat: theme-aware chart rendering with bloomberg/muji plotly templates"
```

---

## Task 8: Final check — run full test suite and clean up

**Step 1: Run all tests**

```bash
cd /Users/ph/stock_watchlist
python3 -m pytest tests/ -v
```

Expected: all pass.

**Step 2: Confirm no regressions visually**

- Add a stock (e.g. AAPL, 10 shares, cost 150)
- Toggle to MUJI — all numbers, charts, table should render in warm tones
- Toggle back to Terminal — Bloomberg style restored
- Refresh button still works in both themes

**Step 3: Final commit if any cleanup was needed**

```bash
git add -A
git commit -m "chore: final cleanup for MUJI theme toggle"
```
