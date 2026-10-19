"""
Configuration module for Sentinel-Risk Platform.
Centralizes paths, thresholds, taxonomy, and model configurations.
"""

from pathlib import Path

# Base Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

PORTFOLIO_PATH = DATA_DIR / "synthetic_portfolio.json"
NEWS_FEED_PATH = DATA_DIR / "sample_news_feed.json"
TWEETS_FEED_PATH = DATA_DIR / "sample_tweets_feed.json"
SHOCK_SCENARIOS_PATH = DATA_DIR / "shock_scenarios.json"

# Stress Test Activation Threshold
DEFAULT_IMPACT_THRESHOLD = 7.0

# Event Taxonomy
EVENT_TAXONOMY = [
    "Geopolitical",
    "Credit Event",
    "Macroeconomic",
    "Regulatory/Legal",
    "Cyber/Systemic Risk",
    "Merger/Acquisition",
    "Product Launch"
]

# API Configuration
API_HOST = "127.0.0.1"
API_PORT = 8000
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

# Streamlit Dashboard Configuration
DASHBOARD_PORT = 8501

# Financial Institution Baseline Constraints
DEFAULT_BANK_EQUITY_CAPITAL = 135_000_000.0  # $135M Common Equity Tier 1 (CET1)
DEFAULT_MIN_CAR_RATIO = 10.5                  # Minimum 10.5% regulatory threshold under Basel III
