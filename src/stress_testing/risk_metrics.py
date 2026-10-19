"""
Quantitative Risk Metrics Module.
Calculates Basel III Capital metrics, Value-at-Risk (VaR 99%), Expected Shortfall (CVaR),
Expected Credit Losses (EL), and Risk-Weighted Assets (RWA).
"""

import math
from typing import Dict, Any, List
from ..config import DEFAULT_BANK_EQUITY_CAPITAL, DEFAULT_MIN_CAR_RATIO


class PortfolioRiskMetrics:
    """Calculates banking and trading book market and credit risk metrics."""

    @staticmethod
    def calculate_var_cvar(
        portfolio_value: float,
        daily_volatility: float = 0.012,
        horizon_days: int = 10,
        confidence_level: float = 0.99
    ) -> Dict[str, float]:
        """
        Calculates 10-Day Parametric Value-at-Risk (VaR) and Expected Shortfall (CVaR)
        under normal distribution assumption (Z_99 = 2.326).
        """
        # Multi-day volatility scaling (square root of time rule)
        h_vol = daily_volatility * math.sqrt(horizon_days)

        # 99% confidence z-score = 2.3263
        z_score = 2.3263
        var_dollar = portfolio_value * z_score * h_vol
        var_percent = (var_dollar / portfolio_value) * 100.0 if portfolio_value > 0 else 0.0

        # Expected Shortfall (CVaR) for standard normal distribution:
        # ES = portfolio_value * (phi(z) / (1 - confidence)) * h_vol
        # For 99%, phi(2.3263) / 0.01 approx 2.665
        cvar_multiplier = 2.665
        cvar_dollar = portfolio_value * cvar_multiplier * h_vol
        cvar_percent = (cvar_dollar / portfolio_value) * 100.0 if portfolio_value > 0 else 0.0

        return {
            "var_99_10d_usd": round(var_dollar, 2),
            "var_99_10d_percent": round(var_percent, 2),
            "cvar_99_10d_usd": round(cvar_dollar, 2),
            "cvar_99_10d_percent": round(cvar_percent, 2),
            "assumed_daily_vol_percent": round(daily_volatility * 100.0, 2)
        }

    @staticmethod
    def calculate_credit_expected_loss(assets: List[Dict[str, Any]]) -> float:
        """
        Computes Expected Credit Loss: EL = sum( Exposure * PD * LGD )
        """
        total_el = 0.0
        for asset in assets:
            ead = asset.get("market_value_usd", asset.get("notional_usd", 0.0))
            pd = asset.get("base_pd_percent", 1.0) / 100.0
            lgd = asset.get("lgd_percent", 45.0) / 100.0
            total_el += ead * pd * lgd
        return round(total_el, 2)

    @staticmethod
    def calculate_basel_rwa(assets: List[Dict[str, Any]]) -> float:
        """
        Computes Total Risk-Weighted Assets (RWA) based on Basel III asset weightings.
        RWA = sum( Exposure * Risk_Weight_Percent )
        """
        total_rwa = 0.0
        for asset in assets:
            exposure = asset.get("market_value_usd", asset.get("notional_usd", 0.0))
            rw = asset.get("basel_risk_weight_percent", 100.0) / 100.0
            total_rwa += exposure * rw
        return round(total_rwa, 2)

    @staticmethod
    def calculate_capital_adequacy(
        tier1_capital: float,
        rwa: float,
        stressed_loss: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculates Capital Adequacy Ratio (CAR):
        CAR = (Tier 1 Capital - Realized Stressed Loss) / RWA
        """
        stressed_capital = max(0.0, tier1_capital - stressed_loss)
        car_percent = (stressed_capital / rwa) * 100.0 if rwa > 0 else 0.0

        is_breach = car_percent < DEFAULT_MIN_CAR_RATIO
        capital_buffer = car_percent - DEFAULT_MIN_CAR_RATIO

        return {
            "tier1_capital_usd": round(tier1_capital, 2),
            "post_stress_capital_usd": round(stressed_capital, 2),
            "rwa_usd": round(rwa, 2),
            "car_percent": round(car_percent, 2),
            "regulatory_minimum_percent": DEFAULT_MIN_CAR_RATIO,
            "capital_buffer_percent": round(capital_buffer, 2),
            "capital_breach": is_breach
        }
