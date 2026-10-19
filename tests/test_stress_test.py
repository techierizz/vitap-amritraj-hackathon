"""
Unit Tests for Module B: Strategic Portfolio Stress Testing.
Validates synthetic portfolio composition, Basel III risk metrics, and shock simulation.
"""

from src.stress_testing.portfolio_manager import WholesalePortfolioManager
from src.stress_testing.risk_metrics import PortfolioRiskMetrics
from src.stress_testing.shock_engine import PortfolioStressTestingEngine


def test_portfolio_manager_loads_assets():
    mgr = WholesalePortfolioManager()
    summary = mgr.get_portfolio_summary()
    assert summary["total_assets_count"] >= 10
    assert summary["total_market_value_usd"] > 500_000_000.0
    assert "Loan" in summary["asset_class_breakdown"]
    assert "Bond" in summary["asset_class_breakdown"]
    assert "Derivative" in summary["asset_class_breakdown"]


def test_risk_metrics_var_cvar():
    val = 1_000_000_000.0
    metrics = PortfolioRiskMetrics.calculate_var_cvar(val, daily_volatility=0.012, horizon_days=10)
    assert metrics["var_99_10d_usd"] > 0
    assert metrics["cvar_99_10d_usd"] > metrics["var_99_10d_usd"]


def test_stress_test_trigger_threshold():
    engine = PortfolioStressTestingEngine(impact_threshold=7.0)

    # Moderate event below threshold without force_run
    res_low = engine.run_stress_test("Macroeconomic", impact_score=5.5, force_run=False)
    assert res_low["triggered"] is False
    assert res_low["total_loss_usd"] == 0.0

    # High severity event exceeding threshold
    res_high = engine.run_stress_test("Geopolitical", impact_score=8.5, force_run=False)
    assert res_high["triggered"] is True
    assert res_high["valuation_summary"]["total_loss_usd"] > 0
    assert res_high["capital_and_regulatory_impact"]["post_stress_car_percent"] < res_high["capital_and_regulatory_impact"]["pre_stress_car_percent"]
