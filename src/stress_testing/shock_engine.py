"""
Portfolio Stress Testing Simulation Engine (Module B).
Applies event-driven macroeconomic and credit factor shocks to the wholesale banking portfolio
based on structured NLP risk signals (Event Classification & Impact Score).
"""

import copy
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from ..config import (
    SHOCK_SCENARIOS_PATH,
    DEFAULT_IMPACT_THRESHOLD,
    DEFAULT_BANK_EQUITY_CAPITAL
)
from .portfolio_manager import WholesalePortfolioManager
from .risk_metrics import PortfolioRiskMetrics


class PortfolioStressTestingEngine:
    """Simulates market, credit, and capital shocks on a wholesale banking portfolio."""

    def __init__(
        self,
        portfolio_manager: Optional[WholesalePortfolioManager] = None,
        shock_path: Optional[Path] = None,
        impact_threshold: float = DEFAULT_IMPACT_THRESHOLD
    ):
        self.portfolio_manager = portfolio_manager or WholesalePortfolioManager()
        self.shock_path = shock_path or SHOCK_SCENARIOS_PATH
        self.impact_threshold = impact_threshold
        self.scenarios = self._load_scenarios()

    def _load_scenarios(self) -> Dict[str, Any]:
        """Loads calibrated shock matrices."""
        if not self.shock_path.exists():
            raise FileNotFoundError(f"Shock scenarios file not found at: {self.shock_path}")
        with open(self.shock_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_stress_test(
        self,
        event_classification: str,
        impact_score: float,
        force_run: bool = False,
        custom_shocks: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Executes an event-driven stress test simulation.

        Args:
            event_classification: Category label (e.g. 'Geopolitical', 'Credit Event')
            impact_score: Severity score [1.0 to 10.0]
            force_run: If True, executes even if impact_score < threshold
            custom_shocks: Optional overrides for specific shock parameters

        Returns:
            Comprehensive stress test audit report including pre/post values, losses,
            RWA expansion, capital ratio hit, and asset-by-asset revaluations.
        """
        # Determine if test should run
        is_triggered = (impact_score >= self.impact_threshold) or force_run

        # Baseline portfolio metrics
        base_summary = self.portfolio_manager.get_portfolio_summary()
        base_assets = self.portfolio_manager.get_assets()
        pre_stress_val = base_summary["total_market_value_usd"]

        if not is_triggered:
            return {
                "triggered": False,
                "reason": (
                    f"Impact score {impact_score:.1f} is below activation threshold "
                    f"({self.impact_threshold:.1f}). Stress test remains in standby."
                ),
                "event_classification": event_classification,
                "impact_score": impact_score,
                "pre_stress_market_value_usd": pre_stress_val,
                "post_stress_market_value_usd": pre_stress_val,
                "total_loss_usd": 0.0,
                "percentage_loss": 0.0
            }

        # Retrieve base scenario parameters
        scenario = self.scenarios.get(
            event_classification,
            self.scenarios.get("Macroeconomic")
        )
        scenario_params = copy.deepcopy(scenario)
        if custom_shocks:
            scenario_params.update(custom_shocks)

        # Intensity Scaling Factor: scales proportionally with Impact Score (e.g. 8.5/10.0 = 0.85)
        scale = max(0.20, impact_score / 10.0)

        # Scaled shock magnitudes
        eq_shock = (scenario_params.get("equity_shock_percent", -10.0) / 100.0) * scale
        ir_shock_bps = scenario_params.get("interest_rate_shock_bps", 100.0) * scale
        ir_shock_pct = ir_shock_bps / 10000.0
        ig_spread_bps = scenario_params.get("ig_spread_widening_bps", 80.0) * scale
        ig_spread_pct = ig_spread_bps / 10000.0
        hy_spread_bps = scenario_params.get("hy_spread_widening_bps", 300.0) * scale
        hy_spread_pct = hy_spread_bps / 10000.0
        cre_discount = (scenario_params.get("cre_loan_discount_percent", -8.0) / 100.0) * scale
        pd_mult = 1.0 + (scenario_params.get("pd_multiplier", 2.0) - 1.0) * scale
        lgd_mult = 1.0 + (scenario_params.get("lgd_multiplier", 1.15) - 1.0) * scale
        haircut = (scenario_params.get("derivative_counterparty_haircut_percent", 5.0) / 100.0) * scale

        # Asset-by-asset revaluation
        stressed_assets = []
        for asset in copy.deepcopy(base_assets):
            a_type = asset.get("asset_type")
            rating = asset.get("credit_rating", "BBB")
            val = asset.get("market_value_usd", 0.0)
            dur = asset.get("duration_years", 3.0)

            asset_loss = 0.0
            loss_mechanism = "Unchanged"

            if a_type == "Equity":
                # Direct Equity shock
                asset_loss = val * eq_shock
                loss_mechanism = f"Equity market drawdown of {eq_shock*100:.2f}%"

            elif a_type == "Bond":
                # Fixed income duration and credit spread repricing
                # dP/P ~= - Duration * (delta_y + delta_spread)
                is_hy = rating in ["BB+", "BB", "BB-", "B+", "B", "CCC"]
                is_sov = "Sovereign" in asset.get("sub_type", "")

                spread_chg = 0.0 if is_sov else (hy_spread_pct if is_hy else ig_spread_pct)
                total_yield_chg = ir_shock_pct + spread_chg
                pct_chg = -1.0 * dur * total_yield_chg
                asset_loss = val * pct_chg
                loss_mechanism = (
                    f"Duration {dur:.1f}y hit by +{ir_shock_bps:.0f}bps IR & "
                    f"+{spread_chg*10000:.0f}bps credit spread"
                )

            elif a_type == "Loan":
                # Loan provisioning, cap rate discount, and spread widening
                is_cre = "Real Estate" in asset.get("sub_type", "")
                is_lbo = "Leveraged" in asset.get("sub_type", "")

                if is_cre:
                    pct_chg = cre_discount
                elif is_lbo:
                    pct_chg = -1.0 * (hy_spread_pct * dur * 0.8)
                else:
                    pct_chg = -1.0 * (ig_spread_pct * dur * 0.6)

                asset_loss = val * pct_chg
                loss_mechanism = f"Credit discount factor ({pct_chg*100:.2f}%) & risk provision surge"

            elif a_type == "Derivative":
                # Counterparty haircut and interest rate delta
                pct_chg = -haircut
                # Rate swap delta sensitivity
                if "Pay-Fixed" in asset.get("asset_name", ""):
                    # Benefits from higher rates, offsets haircut
                    ir_gain = (ir_shock_bps / 100.0) * 0.02 * val
                    asset_loss = (val * pct_chg) + ir_gain
                    loss_mechanism = f"Counterparty haircut ({haircut*100:.1f}%) adjusted for rate delta"
                else:
                    asset_loss = val * pct_chg
                    loss_mechanism = f"Counterparty liquidity haircut of {haircut*100:.1f}%"

            elif a_type == "Structured Credit":
                # CLO spread blowout
                clo_spread_bps = scenario_params.get("clo_spread_widening_bps", 250.0) * scale
                pct_chg = -1.0 * dur * (clo_spread_bps / 10000.0)
                asset_loss = val * pct_chg
                loss_mechanism = f"CLO mezzanine spread widening of +{clo_spread_bps:.0f}bps"

            # Compute stressed values
            new_val = max(0.0, val + asset_loss)
            actual_loss = val - new_val

            # Stressed Credit Risk parameters
            old_pd = asset.get("base_pd_percent", 1.0)
            stressed_pd = min(100.0, old_pd * pd_mult)
            old_lgd = asset.get("lgd_percent", 45.0)
            stressed_lgd = min(100.0, old_lgd * lgd_mult)

            # Rating migration impact on Basel Risk Weight (+25% to +50% under stress)
            old_rw = asset.get("basel_risk_weight_percent", 100.0)
            stressed_rw = min(250.0, old_rw * (1.0 + 0.35 * scale))

            asset["market_value_usd_pre"] = val
            asset["market_value_usd"] = round(new_val, 2)
            asset["loss_usd"] = round(actual_loss, 2)
            asset["loss_percent"] = round((actual_loss / val * 100.0) if val > 0 else 0.0, 2)
            asset["stressed_pd_percent"] = round(stressed_pd, 2)
            asset["stressed_lgd_percent"] = round(stressed_lgd, 2)
            asset["basel_risk_weight_percent"] = round(stressed_rw, 2)
            asset["loss_mechanism"] = loss_mechanism

            stressed_assets.append(asset)

        # Aggregate Stressed Portfolio
        post_stress_val = sum(a["market_value_usd"] for a in stressed_assets)
        total_dollar_loss = pre_stress_val - post_stress_val
        percentage_loss = (total_dollar_loss / pre_stress_val * 100.0) if pre_stress_val > 0 else 0.0

        # Post-stress Credit Risk Metrics
        stressed_el = PortfolioRiskMetrics.calculate_credit_expected_loss(stressed_assets)
        stressed_rwa = PortfolioRiskMetrics.calculate_basel_rwa(stressed_assets)

        # Post-stress Capital Adequacy
        capital_eval = PortfolioRiskMetrics.calculate_capital_adequacy(
            tier1_capital=DEFAULT_BANK_EQUITY_CAPITAL,
            rwa=stressed_rwa,
            stressed_loss=total_dollar_loss
        )

        # Stressed VaR and CVaR (with volatility expansion under stress)
        stressed_vol = 0.010 * (1.0 + 0.85 * scale)
        stressed_var = PortfolioRiskMetrics.calculate_var_cvar(
            portfolio_value=post_stress_val,
            daily_volatility=stressed_vol,
            horizon_days=10
        )

        # Asset Class Losses Breakdown
        df_stressed = pd.DataFrame(stressed_assets)
        asset_class_losses = (
            df_stressed.groupby("asset_type")["loss_usd"].sum().round(2).to_dict()
        )
        sector_losses = (
            df_stressed.groupby("sector")["loss_usd"].sum().round(2).to_dict()
        )

        # Top 5 most impacted assets
        top_impacted = df_stressed.sort_values(by="loss_usd", ascending=False).head(5)[
            ["asset_id", "asset_name", "asset_type", "sector", "market_value_usd_pre", "market_value_usd", "loss_usd", "loss_percent", "loss_mechanism"]
        ].to_dict(orient="records")

        return {
            "triggered": True,
            "simulation_id": f"SIM-{event_classification[:3].upper()}-{int(impact_score*10)}",
            "event_classification": event_classification,
            "impact_score": impact_score,
            "scenario_name": scenario_params.get("name", "Macro Stress Scenario"),
            "scenario_narrative": scenario_params.get("description", ""),
            "applied_shocks": {
                "equity_shock_percent": round(eq_shock * 100, 2),
                "interest_rate_shock_bps": round(ir_shock_bps, 1),
                "ig_spread_widening_bps": round(ig_spread_bps, 1),
                "hy_spread_widening_bps": round(hy_spread_bps, 1),
                "pd_multiplier": round(pd_mult, 2),
                "lgd_multiplier": round(lgd_mult, 2),
                "derivative_haircut_percent": round(haircut * 100, 2)
            },
            "valuation_summary": {
                "pre_stress_market_value_usd": round(pre_stress_val, 2),
                "post_stress_market_value_usd": round(post_stress_val, 2),
                "total_loss_usd": round(total_dollar_loss, 2),
                "percentage_loss": round(percentage_loss, 2)
            },
            "capital_and_regulatory_impact": {
                "pre_stress_rwa_usd": base_summary["baseline_rwa_usd"],
                "post_stress_rwa_usd": stressed_rwa,
                "rwa_expansion_usd": round(stressed_rwa - base_summary["baseline_rwa_usd"], 2),
                "pre_stress_car_percent": base_summary["baseline_capital_ratio_percent"],
                "post_stress_car_percent": capital_eval["car_percent"],
                "car_drawdown_bps": round((base_summary["baseline_capital_ratio_percent"] - capital_eval["car_percent"]) * 100, 1),
                "regulatory_minimum_car_percent": capital_eval["regulatory_minimum_percent"],
                "capital_buffer_remaining_percent": capital_eval["capital_buffer_percent"],
                "capital_breach_detected": capital_eval["capital_breach"]
            },
            "credit_and_var_impact": {
                "pre_stress_expected_loss_usd": base_summary["baseline_expected_loss_usd"],
                "post_stress_expected_loss_usd": stressed_el,
                "expected_loss_surge_usd": round(stressed_el - base_summary["baseline_expected_loss_usd"], 2),
                "pre_stress_var_99_10d_usd": base_summary["baseline_var_99_10d_usd"],
                "post_stress_var_99_10d_usd": stressed_var["var_99_10d_usd"],
                "post_stress_cvar_99_10d_usd": stressed_var["cvar_99_10d_usd"]
            },
            "loss_breakdown_by_asset_class": asset_class_losses,
            "loss_breakdown_by_sector": sector_losses,
            "top_impacted_assets": top_impacted,
            "full_stressed_assets": stressed_assets
        }
