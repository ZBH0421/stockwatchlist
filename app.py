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

# ── MUJI Plotly Theme ────────────────────────────────────────────────
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


def get_chart_template(theme: str) -> str:
    """Return the Plotly template name for the given theme."""
    return "bloomberg" if theme == "dark" else "muji"


def toggle_theme(n_clicks: int, current_theme: str) -> str:
    """Flip theme between dark and light; no-op if n_clicks is 0."""
    if not n_clicks:
        return current_theme
    return "light" if current_theme == "dark" else "dark"


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

import pandas as pd
import plotly.express as px
from dash import callback, clientside_callback, Input, Output, State, ALL, ctx

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


from data import (load_portfolio, save_portfolio, add_holding,
                  remove_holding, enrich_holdings, fetch_prices)


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
        stat("TOTAL P&L",      f"{'+' if total_pnl>=0 else ''}${total_pnl:,.2f}",
             pnl_class),
        stat("TOTAL RETURN",
             f"{'+' if total_pct>=0 else ''}{total_pct:.2f}%", pnl_class),
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


if __name__ == "__main__":
    app.run(debug=True, port=8052)
