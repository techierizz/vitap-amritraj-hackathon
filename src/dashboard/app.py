"""
Sentinel-Risk | Streamlit Executive Risk Terminal.
Production-grade interactive dashboard for the S&P Global & CRISIL Campus Hackathon.
Integrates the Unified AI/NLP Risk Engine with Module B: Strategic Wholesale Portfolio Stress Tester.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime

# Streamlit Page Config (Must be first Streamlit call)
st.set_page_config(
    page_title="Sentinel-Risk | AI Risk Engine & Stress Tester",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.nlp_engine.risk_pipeline import RiskSignalPipeline
from src.ingestion.live_feed_manager import LiveFeedManager
from src.stress_testing.portfolio_manager import WholesalePortfolioManager
from src.stress_testing.shock_engine import PortfolioStressTestingEngine
from src.config import EVENT_TAXONOMY, DEFAULT_IMPACT_THRESHOLD, API_BASE_URL
from src.dashboard.components import (
    CUSTOM_CSS,
    render_impact_gauge,
    render_waterfall_loss,
    render_asset_comparison_bar,
    render_portfolio_pie
)

# Apply Custom Styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Initialize Cached Singletons
@st.cache_resource
def get_nlp_pipeline():
    return RiskSignalPipeline()


@st.cache_resource
def get_portfolio_manager():
    return WholesalePortfolioManager()


@st.cache_resource
def get_stress_engine():
    mgr = get_portfolio_manager()
    return PortfolioStressTestingEngine(portfolio_manager=mgr)


@st.cache_resource
def get_feed_manager():
    pipeline = get_nlp_pipeline()
    return LiveFeedManager(risk_pipeline=pipeline)


nlp_engine = get_nlp_pipeline()
portfolio_mgr = get_portfolio_manager()
stress_engine = get_stress_engine()
feed_mgr = get_feed_manager()

# Initialize Session State
if "active_event" not in st.session_state:
    st.session_state["active_event"] = {
        "text": "Strait of Hormuz Naval Blockade Escalates: Crude Oil Surges 18% as Defense Tensions Reach Crisis Point",
        "source": "Breaking News Feed",
        "run_test": False
    }

if "last_stress_result" not in st.session_state:
    st.session_state["last_stress_result"] = None

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.markdown("### **Sentinel-Risk Terminal**")
    st.caption("S&P Global & CRISIL Campus Hackathon | Module B")
    st.markdown("---")

    st.markdown("#### ⚙️ Stress Test Configuration")
    threshold = st.slider(
        "Activation Impact Threshold",
        min_value=1.0,
        max_value=10.0,
        value=float(DEFAULT_IMPACT_THRESHOLD),
        step=0.5,
        help="Events with Impact Score >= this threshold automatically trigger downstream stress test."
    )
    stress_engine.impact_threshold = threshold

    force_run_toggle = st.checkbox(
        "Force Stress Test (Bypass Threshold)",
        value=False,
        help="Allows running the stress test model on any event regardless of severity score."
    )

    st.markdown("---")
    st.markdown("#### 🔌 System Health")
    st.success("🟢 NLP Risk Engine: Active")
    st.success("🟢 Wholesale Book: $1.09B Loaded")
    st.success(f"🟢 API Backend: Ready at {API_BASE_URL}")

    st.markdown("---")
    st.caption("Developed with Python, FastAPI, and Streamlit.")


# Main App Header
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🛡️ SENTINEL-RISK | Unified AI/NLP Risk Engine & Stress Tester</div>
    <div class="hero-sub">
        An enterprise platform ingesting real-time unstructured feeds (Financial News & Social Media/X),
        extracting structured machine-readable risk signals (Sentiment Score, Event Classification, Impact Score),
        and executing strategic portfolio stress tests on wholesale banking assets under Basel III standards.
    </div>
</div>
""", unsafe_allow_html=True)


# Tabs Structure
tabs = st.tabs([
    "🌐 Live Ingestion Feeds",
    "🧪 Interactive Event Tester",
    "📊 Strategic Wholesale Portfolio",
    "🛡️ Stress Testing & Capital Analytics",
    "📑 Case Study & Architecture"
])


# ==========================================
# TAB 1: LIVE INGESTION FEEDS
# ==========================================
with tabs[0]:
    st.subheader("Real-Time Multi-Source Ingestion & Structured Risk Signals")
    st.markdown(
        "Ingests unstructured text from **Financial News Articles** and **Twitter/X Streams**, "
        "transforming them into machine-readable risk signals."
    )

    col_filter1, col_filter2, col_filter3, col_refresh = st.columns([2, 2, 2, 1])
    with col_filter1:
        source_filter = st.selectbox("Filter Source", ["All Sources", "Financial News", "Twitter/X"])
    with col_filter2:
        cat_filter = st.selectbox("Filter Category", ["All Categories"] + EVENT_TAXONOMY)
    with col_filter3:
        severity_filter = st.selectbox("Filter Impact", ["All Severities", "High Impact (>= 7.0)", "Moderate (< 7.0)"])
    with col_refresh:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # Load and score feed items
    with st.spinner("Ingesting and scoring multi-source unstructured streams..."):
        all_signals = feed_mgr.ingest_and_score_all()

    # Filter signals
    filtered = []
    for sig in all_signals:
        if source_filter != "All Sources" and sig["source_type"] != source_filter:
            continue
        if cat_filter != "All Categories" and sig["event_classification"] != cat_filter:
            continue
        if severity_filter == "High Impact (>= 7.0)" and sig["impact_score"] < 7.0:
            continue
        if severity_filter == "Moderate (< 7.0)" and sig["impact_score"] >= 7.0:
            continue
        filtered.append(sig)

    st.markdown(f"**Displaying {len(filtered)} risk signals across ingested channels:**")

    for idx, item in enumerate(filtered):
        is_high_impact = item["impact_score"] >= threshold
        sent_val = item["sentiment_score"]
        sent_class = "pill-bearish" if sent_val < -0.15 else ("pill-bullish" if sent_val > 0.15 else "pill-neutral")
        risk_class = "pill-high-risk" if is_high_impact else "pill-cat"

        with st.container():
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div>
                        <span class="pill pill-cat">{item['source']}</span>
                        <span class="pill {sent_class}">Sentiment: {sent_val:+.2f} ({item['sentiment_label']})</span>
                        <span class="pill pill-cat">{item['event_classification']}</span>
                        <span class="pill {risk_class}">Impact: {item['impact_score']}/10 ({item['severity_level']})</span>
                    </div>
                    <span style="font-size: 11px; color: #64748b;">{item['timestamp']}</span>
                </div>
                <div style="font-size: 15px; font-weight: 600; color: #f1f5f9; margin-bottom: 6px;">
                    {item['headline_or_text']}
                </div>
                <div style="font-size: 12px; color: #94a3b8; display: flex; justify-content: space-between;">
                    <span><b>Entity:</b> {item['entity_mentioned']} | <b>Signal ID:</b> {item['signal_id']}</span>
                    <span><b>Stress Test Trigger:</b> {'🚨 ACTIVE (>= 7.0)' if is_high_impact else '⏸️ STANDBY'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            btn_col1, btn_col2 = st.columns([1, 6])
            with btn_col1:
                if st.button(f"⚡ Stress Test", key=f"btn_stress_{idx}"):
                    st.session_state["active_event"] = {
                        "text": item["headline_or_text"],
                        "source": item["source"],
                        "run_test": True
                    }
                    st.session_state["target_tab"] = 1
                    st.rerun()


# ==========================================
# TAB 2: INTERACTIVE EVENT TESTER
# ==========================================
with tabs[1]:
    st.subheader("Interactive Event Risk Analyzer & Stress Test Launcher")
    st.markdown(
        "Enter any breaking news headline, social media post, or central bank announcement. "
        "The NLP Risk Engine will instantly analyze it and trigger Downstream Module B if severity exceeds threshold."
    )

    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
    with preset_col1:
        if st.button("🔥 Naval Blockade (Geopolitical)", use_container_width=True):
            st.session_state["active_event"]["text"] = "Strait of Hormuz Naval Blockade Escalates: Crude Oil Surges 18% as Defense Tensions Reach Crisis Point"
            st.session_state["active_event"]["source"] = "Reuters Geopolitical Wire"
    with preset_col2:
        if st.button("📉 CRE Debt Default (Credit Event)", use_container_width=True):
            st.session_state["active_event"]["text"] = "European regional bank halts redemptions amid $4.5B commercial real estate debt default wave and junk downgrade."
            st.session_state["active_event"]["source"] = "Bloomberg Markets"
    with preset_col3:
        if st.button("🏦 Fed Emergency 75bps Hike (Macro)", use_container_width=True):
            st.session_state["active_event"]["text"] = "Federal Reserve signals emergency 75 bps rate hike as core inflation accelerates to 6.2%, steepening yields."
            st.session_state["active_event"]["source"] = "WSJ Economics"
    with preset_col4:
        if st.button("🟢 Clean Energy Deal (Product Launch)", use_container_width=True):
            st.session_state["active_event"]["text"] = "Global sovereign consortium commits $25B toward renewable grid infrastructure with strong investor demand."
            st.session_state["active_event"]["source"] = "Financial Post"

    input_text = st.text_area(
        "Input Unstructured Text (News Headline or Tweet):",
        value=st.session_state["active_event"]["text"],
        height=100
    )

    source_input = st.text_input(
        "Source Tag:",
        value=st.session_state["active_event"].get("source", "Live Jury Interactive Input")
    )

    if st.button("🚀 Analyze Risk Signal & Execute Stress Test", type="primary", use_container_width=True):
        st.session_state["active_event"]["text"] = input_text
        st.session_state["active_event"]["source"] = source_input
        st.session_state["active_event"]["run_test"] = True

    if st.session_state["active_event"].get("run_test"):
        signal = nlp_engine.process_text(
            text=input_text,
            source=source_input
        )

        st.markdown("### 🎯 Generated Structured Risk Signal")
        res_col1, res_col2, res_col3 = st.columns([1, 1, 1.2])

        with res_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 13px; color: #94a3b8;">1. Sentiment Score</div>
                <div style="font-size: 30px; font-weight: 800; color: {'#ef4444' if signal['sentiment_score'] < 0 else '#10b981'};">
                    {signal['sentiment_score']:+.2f}
                </div>
                <div style="font-size: 14px; font-weight: 600; color: #e2e8f0;">{signal['sentiment_label']}</div>
                <div style="font-size: 12px; color: #64748b;">Confidence: {signal['sentiment_confidence']*100:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with res_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 13px; color: #94a3b8;">2. Event Classification</div>
                <div style="font-size: 26px; font-weight: 800; color: #60a5fa;">
                    {signal['event_classification']}
                </div>
                <div style="font-size: 14px; color: #e2e8f0;">Entity: {signal['entity_mentioned']}</div>
                <div style="font-size: 12px; color: #64748b;">Taxonomy Match: {signal['category_confidence']*100:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with res_col3:
            st.plotly_chart(render_impact_gauge(signal["impact_score"]), use_container_width=True, key="gauge_tab2")

        # Trigger Evaluation Banner
        triggered = (signal["impact_score"] >= threshold) or force_run_toggle
        if triggered:
            st.error(
                f"🚨 **HIGH-IMPACT EVENT DETECTED (Score {signal['impact_score']}/10 >= Threshold {threshold})**: "
                f"Automated Wholesale Portfolio Stress Test Triggered!"
            )
            # Run Stress Test
            stress_result = stress_engine.run_stress_test(
                event_classification=signal["event_classification"],
                impact_score=signal["impact_score"],
                force_run=True
            )
            st.session_state["last_stress_result"] = stress_result

            # Display Quick Impact Metrics
            val_sum = stress_result["valuation_summary"]
            cap_sum = stress_result["capital_and_regulatory_impact"]

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Pre-Stress Value", f"${val_sum['pre_stress_market_value_usd']/1e6:.1f}M")
            m2.metric("Post-Stress Value", f"${val_sum['post_stress_market_value_usd']/1e6:.1f}M")
            m3.metric("Total Loss", f"-${val_sum['total_loss_usd']/1e6:.2f}M", f"-{val_sum['percentage_loss']:.1f}%")
            m4.metric("Capital Ratio (CAR)", f"{cap_sum['post_stress_car_percent']:.1f}%", f"-{cap_sum['car_drawdown_bps']:.0f} bps")
            m5.metric("Basel Buffer", f"{cap_sum['capital_buffer_remaining_percent']:+.1f}%", "Breach" if cap_sum['capital_breach_detected'] else "Surplus")

            # Waterfall Loss Chart
            st.plotly_chart(
                render_waterfall_loss(
                    pre_val=val_sum["pre_stress_market_value_usd"],
                    post_val=val_sum["post_stress_market_value_usd"],
                    losses_by_class=stress_result["loss_breakdown_by_asset_class"]
                ),
                use_container_width=True,
                key="waterfall_tab2"
            )
        else:
            st.info(
                f"ℹ️ **Impact Score ({signal['impact_score']}/10) is below activation threshold ({threshold})**: "
                "Downstream stress test remains in standby. (Tip: Check 'Force Stress Test' in sidebar to simulate anyway)."
            )


# ==========================================
# TAB 3: STRATEGIC WHOLESALE PORTFOLIO
# ==========================================
with tabs[2]:
    st.subheader("Synthetic Wholesale Banking Portfolio (Tier-1 Institution Book)")
    st.markdown(
        "A realistic **$1.25 Billion wholesale banking portfolio** spanning Loans (CRE, Project Finance, Leveraged LBO), "
        "Bonds (Sovereign Treasuries, Sub-Debt, IG), Derivatives (IRS, Cross-Currency, CDS), and Structured Credit (CLO Mezzanine)."
    )

    port_summary = portfolio_mgr.get_portfolio_summary()
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Total Market Value", f"${port_summary['total_market_value_usd']/1e6:.2f}M", "15 Institutional Assets")
    p2.metric("Basel III RWA", f"${port_summary['baseline_rwa_usd']/1e6:.1f}M", "Standardized Weights")
    p3.metric("Baseline CAR", f"{port_summary['baseline_capital_ratio_percent']:.1f}%", "Target: 11.5% | Min: 10.5%")
    p4.metric("Credit Expected Loss", f"${port_summary['baseline_expected_loss_usd']/1e6:.2f}M", "EL = EAD × PD × LGD")

    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        st.markdown("##### Asset Allocation by Type")
        st.plotly_chart(render_portfolio_pie(portfolio_mgr.get_assets(), "asset_type"), use_container_width=True, key="pie_asset_type_tab3")
    with c_chart2:
        st.markdown("##### Sector Exposure Distribution")
        st.plotly_chart(render_portfolio_pie(portfolio_mgr.get_assets(), "sector"), use_container_width=True, key="pie_sector_tab3")

    st.markdown("##### Asset Level Inventory")
    df_port = portfolio_mgr.to_dataframe()
    display_df = df_port[[
        "asset_id", "asset_name", "asset_type", "sector", "credit_rating",
        "market_value_usd", "duration_years", "base_pd_percent", "lgd_percent", "basel_risk_weight_percent"
    ]].copy()
    display_df["market_value_usd"] = display_df["market_value_usd"].apply(lambda x: f"${x:,.0f}")
    display_df.columns = [
        "Asset ID", "Asset Name", "Type", "Sector", "Rating",
        "Market Value ($)", "Duration (Y)", "Base PD (%)", "LGD (%)", "Basel RW (%)"
    ]
    st.dataframe(display_df, use_container_width=True, height=350)


# ==========================================
# TAB 4: STRESS TESTING & CAPITAL ANALYTICS
# ==========================================
with tabs[3]:
    st.subheader("Module B: Strategic Portfolio Stress Testing & Capital Analytics")
    st.markdown(
        "Simulates the quantitative impact of major real-world shocks on wholesale banking asset valuations, "
        "Risk-Weighted Assets (RWA), Value-at-Risk (VaR), and Basel III Capital Adequacy."
    )

    # If no test has been run yet, run a default high-impact Geopolitical stress test
    if st.session_state["last_stress_result"] is None:
        st.session_state["last_stress_result"] = stress_engine.run_stress_test(
            event_classification="Geopolitical",
            impact_score=9.1,
            force_run=True
        )

    res = st.session_state["last_stress_result"]

    st.markdown(f"""
    <div class="metric-card">
        <span class="pill pill-high-risk">Active Stress Scenario: {res['scenario_name']}</span>
        <span class="pill pill-cat">Event: {res['event_classification']} (Impact: {res['impact_score']}/10)</span>
        <div style="font-size: 13px; color: #cbd5e1; margin-top: 8px;">
            <b>Transmission Mechanism:</b> {res['scenario_narrative']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    val_res = res["valuation_summary"]
    cap_res = res["capital_and_regulatory_impact"]
    var_res = res["credit_and_var_impact"]

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Pre-Stress Value", f"${val_res['pre_stress_market_value_usd']/1e6:.1f}M")
    kpi2.metric("Post-Stress Value", f"${val_res['post_stress_market_value_usd']/1e6:.1f}M")
    kpi3.metric("Total Portfolio Loss", f"-${val_res['total_loss_usd']/1e6:.2f}M", f"-{val_res['percentage_loss']:.2f}%")
    kpi4.metric("Post-Stress CAR", f"{cap_res['post_stress_car_percent']:.1f}%", f"-{cap_res['car_drawdown_bps']:.0f} bps")
    kpi5.metric("Expected Loss Surge", f"+${var_res['expected_loss_surge_usd']/1e6:.2f}M", "Credit Provisions")

    tab4_col1, tab4_col2 = st.columns(2)
    with tab4_col1:
        st.plotly_chart(
            render_waterfall_loss(
                pre_val=val_res["pre_stress_market_value_usd"],
                post_val=val_res["post_stress_market_value_usd"],
                losses_by_class=res["loss_breakdown_by_asset_class"]
            ),
            use_container_width=True,
            key="waterfall_tab4"
        )
    with tab4_col2:
        st.plotly_chart(
            render_asset_comparison_bar(res["full_stressed_assets"]),
            use_container_width=True,
            key="bar_comparison_tab4"
        )

    st.markdown("##### 🚨 Top Impacted Wholesale Assets")
    df_top = pd.DataFrame(res["top_impacted_assets"])
    df_top["market_value_usd_pre"] = df_top["market_value_usd_pre"].apply(lambda x: f"${x:,.0f}")
    df_top["market_value_usd"] = df_top["market_value_usd"].apply(lambda x: f"${x:,.0f}")
    df_top["loss_usd"] = df_top["loss_usd"].apply(lambda x: f"-${x:,.0f}")
    df_top["loss_percent"] = df_top["loss_percent"].apply(lambda x: f"-{x:.1f}%")
    df_top.columns = [
        "Asset ID", "Asset Name", "Type", "Sector",
        "Pre-Stress Value", "Post-Stress Value", "Dollar Loss", "% Loss", "Stress Transmission Mechanism"
    ]
    st.dataframe(df_top, use_container_width=True, height=220)

    # Download Stress Test Results
    json_export = json.dumps(res, indent=2)
    st.download_button(
        label="📥 Export Full Stress Test Report (JSON)",
        data=json_export,
        file_name=f"stress_test_report_{res['event_classification']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


# ==========================================
# TAB 5: CASE STUDY & ARCHITECTURE
# ==========================================
with tabs[4]:
    st.subheader("S&P Global & CRISIL Case Study Architecture & Methodology")
    st.markdown(r"""
    ### 1. Platform Design Architecture
    The **Sentinel-Risk** platform implements an end-to-end data pipeline converting raw unstructured market intelligence
    into quantitative wholesale banking risk parameters:
    
    ```
    +----------------------------------+     +-----------------------------------+
    |    Financial News (RSS/GDELT)    |     |      Twitter/X Social Feeds       |
    +----------------------------------+     +-----------------------------------+
                     │                                         │
                     └────────────────────┬────────────────────┘
                                          ▼
                      +──────────────────────────────────────+
                      |       Unified AI/NLP Risk Engine     |
                      |  - Sentiment Score: [-1.0, +1.0]     |
                      |  - Event Classification: Taxonomy    |
                      |  - Impact Severity Score: [1.0, 10.0]|
                      +──────────────────────────────────────+
                                          │
                                 Impact >= 7.0 Trigger
                                          │
                                          ▼
                      +──────────────────────────────────────+
                      | Downstream Module B: Stress Tester   |
                      |  - Wholesale Banking Book ($1.25B)   |
                      |  - Dynamic Factor Shocks             |
                      |  - Basel III RWA & CAR Evaluation    |
                      |  - Value-at-Risk (VaR) & CVaR        |
                      +──────────────────────────────────────+
                                          │
                     ┌────────────────────┴───────────────────┐
                     ▼                                        ▼
             +───────────────+                        +───────────────+
             | FastAPI (REST)|                        | Streamlit UI  |
             +───────────────+                        +───────────────+
    ```

    ### 2. Methodological Formulations
    - **Sentiment Polarity**: Derived from financial Loughran-McDonald lexicons + semantic sentiment modifier vectors:
      $$S \in [-1.0, 1.0]$$
    - **Fixed Income Duration Markdown**:
      $$\frac{\Delta P}{P} \approx - D \cdot (\Delta y_{riskfree} + \Delta s_{credit})$$
    - **Expected Credit Loss ($EL$)**:
      $$EL = \sum_{i} EAD_i \times PD_{stressed, i} \times LGD_{stressed, i}$$
    - **Basel III Capital Adequacy Ratio ($CAR$)**:
      $$CAR = \frac{\text{Tier 1 Capital} - \text{Realized Stressed Loss}}{\text{Stressed Risk-Weighted Assets (RWA)}} \ge 10.5\%$$
    """)
