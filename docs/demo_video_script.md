# SENTINEL-RISK | Demo Video Script (5 to 10 Minutes Flow)
### Submission for S&P Global & CRISIL Campus Hackathon

---

## Video Outline & Timing Breakdown
- **Part 1: Introduction (~30 - 45 seconds):** The core problem, latency in risk management, and Sentinel-Risk solution.
- **Part 2: Setup & Installation Verification (~30 - 45 seconds):** Commands from README, test suite passing 14/14, server launch.
- **Part 3: End-to-End Walkthrough (~2.5 - 3.5 minutes):**
  - Unstructured Feed ingestion (News & Twitter/X)
  - Unified AI/NLP Risk Engine (Sentiment Score, Event Classification, Impact Score)
  - Interactive Event Tester with live breaking news injection
  - Downstream Module B: Automated Stress Testing on $1.25B Wholesale Banking Book
  - FastAPI Swagger REST API verification
- **Part 4: Results & Domain Impact (~45 - 60 seconds):**
  - Waterfall charts, Basel III RWA expansion, Capital Adequacy Ratio (CAR) breach detection
  - Business impact for wholesale banks and credit rating agencies.

---

## Detailed Script (Word-for-Word Narration & Screen Directions)

### ⏱️ Part 1: Intro (~30s)
**[Screen Action: Display Title Slide or Dashboard Hero Banner]**

**Narrator:**
> "Hello judges and evaluation committee of the S&P Global & CRISIL Campus Hackathon. My name is [Your Name], and today I am demonstrating **Sentinel-Risk**, a unified platform that transforms real-time unstructured news and social feeds into quantitative wholesale banking risk signals.
> 
> Traditional risk management suffers from an information latency problem—shocks like geopolitical blockades or debt defaults hit news feeds intraday, but bank risk models often only reprice on an end-of-day or monthly cycle. Sentinel-Risk solves this by coupling an AI/NLP Risk Engine with an automated, event-driven portfolio stress testing tool under Basel III guidelines."

---

### ⏱️ Part 2: Setup & Run (~30s)
**[Screen Action: Open Terminal Window at repository root]**

**Narrator:**
> "Starting directly from our mandatory README instructions, setting up and running Sentinel-Risk requires just a few simple steps.
> 
> First, let's verify our environment by running our automated verification suite:
> `python run_tests.py`
> 
> Notice that all 14 comprehensive tests pass with 100% success—covering our financial sentiment analyzer, event classifier, impact scorer, wholesale portfolio manager, and FastAPI REST endpoints.
> 
> To launch the entire platform, we can execute our Windows 1-click script `run_demo.bat` or launch our FastAPI backend and Streamlit executive dashboard. Within three seconds, both our REST API on port 8000 and our interactive executive terminal on port 8501 are live and operational."

---

### ⏱️ Part 3: End-to-End Walkthrough (~3 min)

#### Step 3A: Live Ingestion Feeds & Structured Risk Signals
**[Screen Action: Switch to Browser at http://localhost:8501 -> Tab 1: Live Ingestion Feeds]**

**Narrator:**
> "Here on the executive terminal, Tab 1 displays our live multi-source ingestion pipeline.
> 
> We are ingesting unstructured text from two distinct sources:
> 1. Financial News feeds from Reuters and Bloomberg.
> 2. Social media feeds from Twitter/X with financial cashtags and trader alerts.
> 
> For every piece of unstructured text, our unified NLP Risk Engine extracts the exact required triad of fields:
> - A continuous **Sentiment Score** ranging from -1.0 to +1.0, paired with an institutional sentiment label.
> - An **Event Classification** mapped across our 7 standardized financial taxonomies: Geopolitical, Credit Event, Macroeconomic, Regulatory, Cyber Risk, M&A, and Product Launch.
> - A calibrated **Market Impact Score** from 1.0 to 10.0, evaluating systemic market disruption potential.
> 
> Notice the color-coded pill indicators: events scoring 7.0 or higher instantly switch the stress test trigger flag to 'ACTIVE'."

#### Step 3B: Interactive Event Tester & Live Breaking Event Injection
**[Screen Action: Click Tab 2: Interactive Event Tester]**

**Narrator:**
> "Now let's demonstrate the interactive capabilities in Tab 2. As a risk analyst or jury member, we can inject any custom breaking headline or select a preset scenario.
> 
> Let's select: *'Strait of Hormuz Naval Blockade Escalates: Crude Oil Surges 18% as Defense Tensions Reach Crisis Point'*.
> 
> When we click 'Analyze Risk Signal & Execute Stress Test', the NLP engine processes the text in under 45 milliseconds:
> - **Sentiment Score:** -0.68 (Extremely Bearish)
> - **Event Classification:** Geopolitical (Entity identified: Crude Oil / Middle East)
> - **Impact Score:** 9.1 out of 10 (Critical Tail Risk)
> 
> Because 9.1 exceeds our 7.0 threshold, the system immediately sounds an alert and automatically activates Downstream Module B: Strategic Wholesale Portfolio Stress Testing!"

#### Step 3C: Downstream Module B - Strategic Wholesale Portfolio Stress Testing
**[Screen Action: Scroll down Tab 2 or click Tab 4: Stress Testing & Capital Analytics]**

**Narrator:**
> "This brings us to Downstream Module B.
> 
> Our underlying synthetic portfolio represents a realistic **$1.25 Billion wholesale banking book** across Commercial Real Estate loans, Energy project finance, US Treasuries, Subordinated Tier-2 debt, Interest Rate Swaps, and CLO mezzanine tranches.
> 
> Look at the quantitative results calculated by our multi-factor shock engine:
> - **Pre-Stress Portfolio Value:** $1,094.35 Million
> - **Post-Stress Portfolio Value:** $1,011.75 Million
> - **Total Dollar Loss:** -$82.60 Million, representing a -7.55% capital drawdown.
> - **Basel III RWA Expansion:** Risk-Weighted Assets expand by +$189 Million as credit ratings migrate downward.
> - **Capital Adequacy Ratio (CAR):** Drops sharply from 11.5% down to 8.1%. Because our regulatory minimum threshold is 10.5%, the system immediately flags a **Basel Regulatory Capital Breach**!
> 
> Our Plotly Waterfall chart provides instant transparency into where losses occurred: $38M in Loans, $28M in Fixed Income Duration hits, and $11M in Structured Credit. Analysts can drill down into individual asset losses and export the full audit report as JSON with a single click."

#### Step 3D: FastAPI REST Endpoints & Developer Integration
**[Screen Action: Switch to Tab at http://localhost:8000/docs]**

**Narrator:**
> "For programmatic consumption by algorithmic trading desks or core banking systems, our FastAPI backend exposes production-ready REST endpoints:
> - `/api/v1/analyze-risk`: Accepts raw text and returns our machine-readable Pydantic schema.
> - `/api/v1/stress-test`: Executes portfolio stress tests given an event classification and impact score.
> - `/api/v1/simulate-event`: Connects the full pipeline from raw text to quantitative loss calculation."

---

### ⏱️ Part 4: Key Results & Domain Impact (~45s)
**[Screen Action: Return to Dashboard Overview or Slide Deck]**

**Narrator:**
> "To conclude, Sentinel-Risk delivers three transformative capabilities:
> 1. **Speed:** It shrinks risk detection latency from overnight batch runs to under 45 milliseconds.
> 2. **Institutional Rigor:** It bridges qualitative NLP with quantitative Basel III capital and RWA metrics on a $1.25B wholesale book.
> 3. **Actionability:** It empowers Chief Risk Officers to proactively hedge loan portfolios, evaluate capital buffers, and defend institutional solvency before market shocks metastasize.
> 
> Thank you for your time, and I look forward to your questions!"
