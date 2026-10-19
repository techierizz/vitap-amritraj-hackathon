"""
Generates high-resolution architecture.png for docs/
S&P Global & CRISIL Campus Hackathon
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_architecture_diagram():
    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "architecture.png"

    fig, ax = plt.subplots(figsize=(16, 10), dpi=300)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')

    # Title Banner
    ax.text(8.0, 9.4, "SENTINEL-RISK | SYSTEM ARCHITECTURE & DATA FLOW", 
            ha='center', va='center', fontsize=22, fontweight='bold', color='#60A5FA')
    ax.text(8.0, 9.0, "Unified AI/NLP Risk Engine & Strategic Wholesale Portfolio Stress Tester (Module B)", 
            ha='center', va='center', fontsize=13, color='#94A3B8')

    # Color Palette
    c_source = '#1E293B'
    c_nlp = '#1E1B4B'
    c_stress = '#064E3B'
    c_delivery = '#312E81'
    border_blue = '#3B82F6'
    border_indigo = '#818CF8'
    border_green = '#10B981'
    text_main = '#F8FAFC'
    text_sub = '#CBD5E1'

    # Box 1: Ingestion Sources
    box1 = patches.FancyBboxPatch((0.8, 6.2), 4.2, 2.2, boxstyle="round,pad=0.2",
                                  fc=c_source, ec=border_blue, lw=2)
    ax.add_patch(box1)
    ax.text(2.9, 8.0, "1. UNSTRUCTURED SOURCES", ha='center', va='center', fontsize=13, fontweight='bold', color='#60A5FA')
    ax.text(2.9, 7.5, "• Financial News Feeds\n  (Reuters, Bloomberg, GDELT RSS)\n• Twitter/X Social Stream\n  ($JPM, $WTI, Cashtags, Alerts)", 
            ha='center', va='center', fontsize=10.5, color=text_sub)

    # Box 2: Feed Manager
    box2 = patches.FancyBboxPatch((5.8, 6.2), 4.4, 2.2, boxstyle="round,pad=0.2",
                                  fc=c_source, ec=border_blue, lw=2)
    ax.add_patch(box2)
    ax.text(8.0, 8.0, "2. STREAM INGESTION", ha='center', va='center', fontsize=13, fontweight='bold', color='#60A5FA')
    ax.text(8.0, 7.5, "• LiveFeedManager Aggregator\n• Text Cleaning & Normalization\n• Deduplication & Metadata\n• Sub-50ms Processing Queue", 
            ha='center', va='center', fontsize=10.5, color=text_sub)

    # Box 3: AI/NLP Risk Engine
    box3 = patches.FancyBboxPatch((11.0, 6.2), 4.2, 2.2, boxstyle="round,pad=0.2",
                                  fc=c_nlp, ec=border_indigo, lw=2.5)
    ax.add_patch(box3)
    ax.text(13.1, 8.0, "3. AI/NLP RISK ENGINE", ha='center', va='center', fontsize=13, fontweight='bold', color='#A78BFA')
    ax.text(13.1, 7.5, "• Sentiment Score: [-1.0, +1.0]\n  (Loughran-McDonald Domain Lexicon)\n• Event Classification (7 Categories)\n• Market Impact Score: [1.0 - 10.0]", 
            ha='center', va='center', fontsize=10.5, color=text_sub)

    # Arrow 1 -> 2
    ax.annotate('', xy=(5.7, 7.3), xytext=(5.1, 7.3),
                arrowprops=dict(facecolor='#38BDF8', edgecolor='none', width=3, headwidth=10))

    # Arrow 2 -> 3
    ax.annotate('', xy=(10.9, 7.3), xytext=(10.3, 7.3),
                arrowprops=dict(facecolor='#38BDF8', edgecolor='none', width=3, headwidth=10))

    # Trigger Evaluation Banner
    banner = patches.FancyBboxPatch((3.5, 4.8), 9.0, 0.9, boxstyle="round,pad=0.15",
                                    fc='#450A0A', ec='#EF4444', lw=2)
    ax.add_patch(banner)
    ax.text(8.0, 5.25, "AUTOMATED STRESS TRIGGER: Impact Score >= 7.0 (or Force Override)",
            ha='center', va='center', fontsize=12, fontweight='bold', color='#FCA5A5')

    # Arrow 3 -> Banner
    ax.annotate('', xy=(8.0, 5.8), xytext=(13.1, 6.1),
                arrowprops=dict(facecolor='#EF4444', edgecolor='none', width=2.5, headwidth=9))

    # Arrow Banner -> Module B
    ax.annotate('', xy=(8.0, 3.8), xytext=(8.0, 4.7),
                arrowprops=dict(facecolor='#10B981', edgecolor='none', width=3, headwidth=10))

    # Box 4: Module B Stress Testing Engine
    box4 = patches.FancyBboxPatch((1.5, 1.8), 13.0, 1.9, boxstyle="round,pad=0.2",
                                  fc=c_stress, ec=border_green, lw=2.5)
    ax.add_patch(box4)
    ax.text(8.0, 3.4, "4. MODULE B: STRATEGIC WHOLESALE PORTFOLIO STRESS TESTER", 
            ha='center', va='center', fontsize=13, fontweight='bold', color='#34D399')
    ax.text(8.0, 2.6, 
            "• $1.25B Wholesale Banking Book: Loans (CRE, LBO), Bonds (Treasuries, Sub-Debt), Derivatives (IRS, CDS), CLOs\n"
            "• Calibrated Shock Matrices: Equity Shocks, Rate Shifts (+150-250bps), Spread Widenings, PD & LGD Multipliers\n"
            "• Basel III Metrics: Risk-Weighted Assets (RWA) Expansion, Stressed Capital Adequacy Ratio (CAR vs 10.5% Min)\n"
            "• Tail Risk Quant: 10-Day 99% Parametric VaR, Expected Shortfall (CVaR), and Expected Credit Loss (EL)",
            ha='center', va='center', fontsize=10.5, color=text_sub)

    # Box 5: Delivery & Interfaces
    box5_a = patches.FancyBboxPatch((1.5, 0.3), 6.0, 1.1, boxstyle="round,pad=0.15",
                                    fc=c_delivery, ec=border_indigo, lw=2)
    ax.add_patch(box5_a)
    ax.text(4.5, 0.95, "FASTAPI REST BACKEND", ha='center', va='center', fontsize=12, fontweight='bold', color='#818CF8')
    ax.text(4.5, 0.55, "Swagger UI (/docs) | POST /api/v1/analyze-risk\nPOST /api/v1/stress-test | GET /api/v1/portfolio",
            ha='center', va='center', fontsize=9.5, color=text_sub)

    box5_b = patches.FancyBboxPatch((8.5, 0.3), 6.0, 1.1, boxstyle="round,pad=0.15",
                                    fc=c_delivery, ec=border_indigo, lw=2)
    ax.add_patch(box5_b)
    ax.text(11.5, 0.95, "STREAMLIT EXECUTIVE DASHBOARD", ha='center', va='center', fontsize=12, fontweight='bold', color='#818CF8')
    ax.text(11.5, 0.55, "Real-time Feeds | Live Jury Interactive Tester\nPlotly Loss Waterfalls | Basel CAR Analytics",
            ha='center', va='center', fontsize=9.5, color=text_sub)

    # Arrows to Delivery
    ax.annotate('', xy=(4.5, 1.5), xytext=(4.5, 1.75),
                arrowprops=dict(facecolor='#818CF8', edgecolor='none', width=2, headwidth=8))
    ax.annotate('', xy=(11.5, 1.5), xytext=(11.5, 1.75),
                arrowprops=dict(facecolor='#818CF8', edgecolor='none', width=2, headwidth=8))

    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Architecture diagram successfully generated at: {output_path}")

if __name__ == "__main__":
    draw_architecture_diagram()
