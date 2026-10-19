"""
Integration Tests for FastAPI Backend.
Validates all REST endpoints using FastAPI TestClient.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["nlp_engine_ready"] is True


def test_api_analyze_risk():
    payload = {
        "text": "Strait of Hormuz naval conflict drives severe crude oil spike and defense escalation.",
        "source": "Reuters Test Client"
    }
    response = client.post("/api/v1/analyze-risk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "sentiment_score" in data
    assert -1.0 <= data["sentiment_score"] <= 1.0
    assert data["event_classification"] == "Geopolitical"
    assert data["impact_score"] >= 7.0
    assert data["trigger_stress_test"] is True


def test_api_portfolio():
    response = client.get("/api/v1/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["total_notional_usd"] > 0
    assert len(data["assets"]) > 0


def test_api_stress_test():
    payload = {
        "event_classification": "Credit Event",
        "impact_score": 8.5,
        "force_run": True
    }
    response = client.post("/api/v1/stress-test", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["triggered"] is True
    assert data["valuation_summary"]["total_loss_usd"] > 0


def test_api_simulate_event_end_to_end():
    payload = {
        "text": "European regional bank halts redemptions amid $4.5B commercial real estate debt default wave.",
        "source": "Breaking Market Stream"
    }
    response = client.post("/api/v1/simulate-event", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["risk_signal"]["event_classification"] == "Credit Event"
    assert data["stress_test_result"]["triggered"] is True
