"""
Wholesale Portfolio Manager Module.
Loads, manages, and aggregates the synthetic wholesale banking book ($1.25B notional).
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from ..config import PORTFOLIO_PATH, DEFAULT_BANK_EQUITY_CAPITAL
from .risk_metrics import PortfolioRiskMetrics


class WholesalePortfolioManager:
    """Manages wholesale banking assets, calculates distributions, and aggregates risk."""

    def __init__(self, portfolio_path: Optional[Path] = None):
        self.portfolio_path = portfolio_path or PORTFOLIO_PATH
        self.raw_data = self._load_data()
        self.assets = self.raw_data.get("assets", [])
        self.portfolio_name = self.raw_data.get("portfolio_name", "Wholesale Banking Book")
        self.as_of_date = self.raw_data.get("as_of_date", "2026-10-19")

    def _load_data(self) -> Dict[str, Any]:
        """Loads the synthetic portfolio JSON file."""
        if not self.portfolio_path.exists():
            raise FileNotFoundError(f"Portfolio dataset not found at: {self.portfolio_path}")
        with open(self.portfolio_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_assets(self) -> List[Dict[str, Any]]:
        """Returns the complete list of portfolio assets."""
        return self.assets

    def to_dataframe(self) -> pd.DataFrame:
        """Converts assets list into a Pandas DataFrame."""
        return pd.DataFrame(self.assets)

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Generates comprehensive baseline portfolio statistics."""
        total_notional = sum(a.get("notional_usd", 0.0) for a in self.assets)
        total_market_value = sum(a.get("market_value_usd", 0.0) for a in self.assets)

        # Baseline Credit Metrics
        base_el = PortfolioRiskMetrics.calculate_credit_expected_loss(self.assets)
        base_rwa = PortfolioRiskMetrics.calculate_basel_rwa(self.assets)
        base_car = PortfolioRiskMetrics.calculate_capital_adequacy(
            tier1_capital=DEFAULT_BANK_EQUITY_CAPITAL,
            rwa=base_rwa,
            stressed_loss=0.0
        )
        base_var = PortfolioRiskMetrics.calculate_var_cvar(
            portfolio_value=total_market_value,
            daily_volatility=0.010,
            horizon_days=10
        )

        # Asset Class Breakdown
        df = self.to_dataframe()
        asset_class_breakdown = (
            df.groupby("asset_type")["market_value_usd"].sum().round(2).to_dict()
        )
        sector_breakdown = (
            df.groupby("sector")["market_value_usd"].sum().round(2).to_dict()
        )
        rating_breakdown = (
            df.groupby("credit_rating")["market_value_usd"].sum().round(2).to_dict()
        )

        return {
            "portfolio_name": self.portfolio_name,
            "as_of_date": self.as_of_date,
            "total_assets_count": len(self.assets),
            "total_notional_usd": round(total_notional, 2),
            "total_market_value_usd": round(total_market_value, 2),
            "baseline_rwa_usd": base_rwa,
            "baseline_capital_ratio_percent": base_car["car_percent"],
            "baseline_expected_loss_usd": base_el,
            "baseline_var_99_10d_usd": base_var["var_99_10d_usd"],
            "baseline_cvar_99_10d_usd": base_var["cvar_99_10d_usd"],
            "asset_class_breakdown": asset_class_breakdown,
            "sector_breakdown": sector_breakdown,
            "rating_breakdown": rating_breakdown
        }
