"""
Streamlit Dashboard Components and Visualizations.
Provides reusable Plotly charts, UI metric cards, and CSS styling for Sentinel-Risk.
"""

from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


CUSTOM_CSS = """
<style>
    /* Global Page Styling */
    .main {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #172554 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 14px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        color: #60a5fa;
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.5;
    }

    /* Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(71, 85, 105, 0.4);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: rgba(96, 165, 250, 0.8);
        transform: translateY(-2px);
    }

    /* Badge Pills */
    .pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .pill-bearish { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
    .pill-bullish { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .pill-neutral { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }
    .pill-high-risk { background: rgba(239, 68, 68, 0.25); color: #fca5a5; border: 1px solid #ef4444; font-weight: 800; }
    .pill-cat { background: rgba(59, 130, 246, 0.2); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.4); }

    /* Streamlit Tab Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 10px 18px;
        color: #94a3b8;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }
</style>
"""


def render_impact_gauge(impact_score: float) -> go.Figure:
    """Creates a sleek semi-circular gauge chart for Impact Score (1-10)."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=impact_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Market Impact Score", 'font': {'size': 18, 'color': '#e2e8f0'}},
        number={'suffix': "/10", 'font': {'size': 32, 'color': '#ffffff'}},
        gauge={
            'axis': {'range': [1, 10], 'tickwidth': 1, 'tickcolor': "#64748b", 'nticks': 10},
            'bar': {'color': "#3b82f6", 'thickness': 0.25},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 1,
            'bordercolor': "#475569",
            'steps': [
                {'range': [1, 4], 'color': "rgba(16, 185, 129, 0.3)"},
                {'range': [4, 7], 'color': "rgba(245, 158, 11, 0.3)"},
                {'range': [7, 10], 'color': "rgba(239, 68, 68, 0.4)"}
            ],
            'threshold': {
                'line': {'color': "#ef4444", 'width': 4},
                'thickness': 0.85,
                'value': 7.0
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=230,
        margin=dict(l=25, r=25, t=40, b=15)
    )
    return fig


def render_waterfall_loss(pre_val: float, post_val: float, losses_by_class: Dict[str, float]) -> go.Figure:
    """Creates a Waterfall chart showing baseline portfolio value and drawdown by asset class."""
    x_labels = ["Pre-Stress Book"]
    y_values = [pre_val / 1e6]
    measures = ["absolute"]

    for asset_class, loss in losses_by_class.items():
        x_labels.append(f"{asset_class} Shock")
        y_values.append(-abs(loss) / 1e6)
        measures.append("relative")

    x_labels.append("Post-Stress Book")
    y_values.append(post_val / 1e6)
    measures.append("total")

    fig = go.Figure(go.Waterfall(
        name="Portfolio Value Impact",
        orientation="v",
        measure=measures,
        x=x_labels,
        textposition="outside",
        text=[f"${abs(v):.1f}M" for v in y_values],
        y=y_values,
        connector={"line": {"color": "#64748b"}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#3b82f6"}}
    ))
    fig.update_layout(
        title="Wholesale Portfolio Valuation Waterfall ($ Millions)",
        title_font={"size": 16, "color": "#e2e8f0"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94a3b8"),
        yaxis=dict(title="Market Value ($M)", gridcolor="rgba(71, 85, 105, 0.2)"),
        height=380,
        margin=dict(l=20, r=20, t=50, b=30)
    )
    return fig


def render_asset_comparison_bar(stressed_assets: List[Dict[str, Any]]) -> go.Figure:
    """Pre vs Post market value comparison across asset classes."""
    df = pd.DataFrame(stressed_assets)
    grouped = df.groupby("asset_type").agg({
        "market_value_usd_pre": "sum",
        "market_value_usd": "sum"
    }).reset_index()

    grouped["market_value_usd_pre"] /= 1e6
    grouped["market_value_usd"] /= 1e6

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped["asset_type"],
        y=grouped["market_value_usd_pre"],
        name="Pre-Stress ($M)",
        marker_color="#3b82f6"
    ))
    fig.add_trace(go.Bar(
        x=grouped["asset_type"],
        y=grouped["market_value_usd"],
        name="Post-Stress ($M)",
        marker_color="#ef4444"
    ))

    fig.update_layout(
        barmode='group',
        title="Pre vs. Post Stress Market Value by Asset Class ($ Millions)",
        title_font={"size": 16, "color": "#e2e8f0"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94a3b8"),
        yaxis=dict(title="$ Millions", gridcolor="rgba(71, 85, 105, 0.2)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=340,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def render_portfolio_pie(assets: List[Dict[str, Any]], group_by: str = "asset_type") -> go.Figure:
    """Creates a donut chart representing portfolio allocation."""
    df = pd.DataFrame(assets)
    grouped = df.groupby(group_by)["market_value_usd"].sum().reset_index()
    fig = px.pie(
        grouped,
        values="market_value_usd",
        names=group_by,
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#94a3b8"),
        height=300,
        margin=dict(l=15, r=15, t=20, b=20)
    )
    return fig
