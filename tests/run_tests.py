"""
Sentinel-Risk Test Runner (Standalone & Unittest compatible).
Runs all tests with pure standard library or pytest.
"""

import sys
import traceback
from pathlib import Path

# Ensure project root is in sys.path regardless of execution directory
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_all_tests():
    print("=" * 65)
    print("SENTINEL-RISK SYSTEM VERIFICATION SUITE")
    print("=" * 65)

    total = 0
    passed = 0
    failed = 0

    # 1. NLP Engine Tests
    from tests.test_nlp_engine import (
        test_sentiment_analyzer_negative,
        test_sentiment_analyzer_positive,
        test_event_classifier_geopolitical,
        test_event_classifier_credit,
        test_impact_scorer_high_severity,
        test_risk_pipeline_end_to_end
    )
    nlp_tests = [
        ("Sentiment Analyzer (Negative)", test_sentiment_analyzer_negative),
        ("Sentiment Analyzer (Positive)", test_sentiment_analyzer_positive),
        ("Event Classifier (Geopolitical)", test_event_classifier_geopolitical),
        ("Event Classifier (Credit Event)", test_event_classifier_credit),
        ("Impact Scorer (High Severity)", test_impact_scorer_high_severity),
        ("Unified Risk Signal Pipeline", test_risk_pipeline_end_to_end),
    ]

    print("\n[Suite 1: Unified AI/NLP Risk Engine]")
    for name, test_func in nlp_tests:
        total += 1
        try:
            test_func()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name} -> {e}")
            traceback.print_exc()
            failed += 1

    # 2. Stress Testing Engine Tests
    from tests.test_stress_test import (
        test_portfolio_manager_loads_assets,
        test_risk_metrics_var_cvar,
        test_stress_test_trigger_threshold
    )
    stress_tests = [
        ("Portfolio Manager Loads $1.25B Book", test_portfolio_manager_loads_assets),
        ("Risk Metrics 10-Day VaR & CVaR", test_risk_metrics_var_cvar),
        ("Event-Driven Stress Test & Threshold Trigger", test_stress_test_trigger_threshold)
    ]

    print("\n[Suite 2: Module B - Strategic Portfolio Stress Tester]")
    for name, test_func in stress_tests:
        total += 1
        try:
            test_func()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name} -> {e}")
            traceback.print_exc()
            failed += 1

    # 3. API Integration Tests
    from tests.test_api import (
        test_api_health,
        test_api_analyze_risk,
        test_api_portfolio,
        test_api_stress_test,
        test_api_simulate_event_end_to_end
    )
    api_tests = [
        ("FastAPI /health Endpoint", test_api_health),
        ("FastAPI /api/v1/analyze-risk Endpoint", test_api_analyze_risk),
        ("FastAPI /api/v1/portfolio Endpoint", test_api_portfolio),
        ("FastAPI /api/v1/stress-test Endpoint", test_api_stress_test),
        ("FastAPI /api/v1/simulate-event E2E Endpoint", test_api_simulate_event_end_to_end)
    ]

    print("\n[Suite 3: FastAPI REST Endpoints & Schemas]")
    for name, test_func in api_tests:
        total += 1
        try:
            test_func()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name} -> {e}")
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 65)
    print(f"SUMMARY: {passed}/{total} Passed | {failed} Failed")
    print("=" * 65)

    if failed > 0:
        sys.exit(1)
    else:
        print("ALL SYSTEMS PASSING 100%!")


if __name__ == "__main__":
    run_all_tests()
