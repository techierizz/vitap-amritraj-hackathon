# SENTINEL-RISK | Live Jury Pitch Q&A Preparation
### S&P Global & CRISIL Campus Hackathon

This guide prepares you for deep technical, quantitative, and business questions during the Live Jury Pitch round.

---

### Category 1: NLP & Machine Learning Architecture

#### Q1: "Why did you choose a specialized financial sentiment lexicon and rules engine over a generic large language model (LLM) or raw BERT?"
**Answer:**
> "Generic NLP models fail in financial text because common words carry opposite polarities in finance. For instance, in general English, words like 'liability', 'tax', or 'expense' might be treated neutrally, while in finance, terms like 'emergency rate hike', 'liquidity freeze', or 'downgrade to junk' carry severe tail-risk implications.
> 
> Furthermore, latency and reliability are paramount in real-time risk surveillance. Our hybrid architecture combines Loughran-McDonald financial dictionaries, semantic intensifiers, and TextBlob polarity to deliver sub-50ms inference with zero external API dependencies or GPU bottlenecks. The architecture is also fully compatible with HuggingFace FinBERT pipelines as an optional plug-in for deeper offline contextual analysis."

#### Q2: "How do you handle sarcasm, emojis, and social media slang in financial tweets?"
**Answer:**
> "Our social media preprocessor in `src/nlp_engine/sentiment_analyzer.py` specifically addresses microblogging formats:
> 1. It extracts cashtags (`$JPM`, `$WTI`, `$TLT`) to identify targeted assets.
> 2. It normalizes financial slang ('blowout spreads', 'crashing', 'mooning', 'dumping').
> 3. It parses high-conviction financial emojis (e.g. 🚨, ⚠️, 📉 add negative severity multipliers; 🚀, 🟢 add bullish weighting)."

#### Q3: "How do you avoid false positive triggers when headlines mention historical crises or educational discussions?"
**Answer:**
> "Our `MarketImpactScorer` requires a confluence of three distinct signals before triggering a stress test:
> 1. Extreme sentiment polarity ($|Sentiment| > 0.50$).
> 2. Direct presence of real-time emergency and urgency markers ('unprecedented', 'halts redemptions', 'war', 'zero-day exploit').
> 3. Systemic scale indicators (e.g., billions/trillions in notional volume, sovereign institutions, or central banks).
> A casual retrospective headline lacking urgency markers will register a moderate score (<5.0) and remain in standby."

---

### Category 2: Quantitative Finance, Stress Testing & Basel III

#### Q4: "How is your synthetic wholesale banking portfolio structured, and why is it realistic?"
**Answer:**
> "Our synthetic book represents a **$1.25 Billion wholesale banking portfolio** across 15 distinct institutional instruments modeled after a Tier-1 commercial bank:
> - **Loans ($400M+):** Syndicated Commercial Real Estate (CRE), Energy Project Finance, Healthcare Corporate Loans, and Leveraged Buyout (LBO) facilities with realistic credit ratings (AAA to BB-) and loan-level probability of default ($PD$) and loss given default ($LGD$).
> - **Bonds ($385M+):** US Treasuries (duration 8.4y), Subordinated Tier-2 Banking Debt, and High-Yield Energy Notes.
> - **Derivatives ($240M notional):** 5Y Interest Rate Swaps (IRS), Cross-Currency Basis Swaps, and Credit Default Swaps (CDS).
> - **Structured Credit:** CLO Mezzanine tranches (Class C).
> Each asset includes duration, credit spread, baseline Basel III risk weight, and rating migration sensitivities."

#### Q5: "Walk us through the mathematical transmission mechanism when a Geopolitical crisis triggers a stress test."
**Answer:**
> "When a Geopolitical event scores 9.1/10 (e.g., the Strait of Hormuz blockade):
> 1. The engine calculates an intensity scaling factor: $Scale = 9.1 / 10.0 = 0.91$.
> 2. **Fixed Income Duration Shock:** Yield curves shift +85 bps and High-Yield spreads widen +340 bps. Bond prices reprice using the duration approximation:
>    $$\frac{\Delta P}{P} \approx - Duration \times (\Delta y + \Delta s)$$
> 3. **Credit Provisioning Surge:** Default probabilities increase ($PD_{stressed} = PD_{base} \times 2.2$) and loan valuations are marked down for distressed cap rates.
> 4. **Derivative Haircuts:** Counterparty risk haircuts of 8% are applied to mark-to-market valuations.
> 5. **Basel III Capital Impact:** Rating downgrades cause Risk-Weighted Assets (RWA) to expand from $594M to $783M. Combined with an $82.6M valuation loss, the bank's Capital Adequacy Ratio (CAR) drops from 11.5% to 8.1%, triggering an immediate regulatory breach warning below the 10.5% minimum."

#### Q6: "How do you calculate Value-at-Risk (VaR) and Expected Shortfall under stress?"
**Answer:**
> "We compute 10-day 99% Parametric VaR using the square root of time rule:
> $$VaR_{99, 10d} = V_{portfolio} \times 2.3263 \times \sigma_{daily} \sqrt{10}$$
> Under stress, the engine expands the baseline daily volatility from 1.0% to 1.8% to capture tail-risk kurtosis, and computes Expected Shortfall (CVaR) at 2.665 standard deviations, ensuring conservative downside capital estimation."

---

### Category 3: System Architecture & Deployment

#### Q7: "How would this system scale to handle millions of real-time market articles per day?"
**Answer:**
> "Sentinel-Risk is architected as asynchronous microservices:
> 1. Ingestion can be horizontally scaled using Apache Kafka or AWS Kinesis to partition news streams across worker pods.
> 2. The NLP Risk Engine is stateless and can be deployed on a Kubernetes cluster with autoscaling worker pools.
> 3. The FastAPI backend supports async endpoint routing, while portfolio stress testing calculations run vectorized NumPy/Pandas matrix operations taking less than 15ms per run."

#### Q8: "What is the primary business value for an institution like CRISIL or S&P Global?"
**Answer:**
> "For credit rating agencies and financial intelligence providers like S&P Global and CRISIL, this technology enables:
> - **Automated Early Warning Signals:** Identifying distressed corporate issuers hours or days before formal credit rating action.
> - **Client Analytics Value-Add:** Providing institutional clients with interactive scenario cockpits to stress test bespoke portfolios against breaking news events.
> - **Regulatory Compliance:** Generating auditable, explainable stress test reports aligned with supervisory expectations."
