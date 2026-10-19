"""
FastAPI Enterprise Application for Sentinel-Risk.
Exposes REST endpoints for the Unified AI/NLP Risk Engine and Strategic Portfolio Stress Testing.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import uvicorn

from .schemas import (
    RiskAnalysisRequest,
    RiskSignalResponse,
    StressTestRequest,
    SimulateEventRequest
)
from ..nlp_engine.risk_pipeline import RiskSignalPipeline
from ..ingestion.live_feed_manager import LiveFeedManager
from ..stress_testing.portfolio_manager import WholesalePortfolioManager
from ..stress_testing.shock_engine import PortfolioStressTestingEngine
from ..config import API_HOST, API_PORT

# Initialize FastAPI App
app = FastAPI(
    title="Sentinel-Risk | Unified AI/NLP Risk Engine & Portfolio Stress Tester",
    description=(
        "Production-grade financial risk intelligence platform designed for the S&P Global & CRISIL Hackathon. "
        "Ingests real-time unstructured data (news, tweets), emits structured risk signals "
        "(Sentiment Score, Event Classification, Impact Score), and executes event-driven stress testing on wholesale banking books."
    ),
    version="1.0.0"
)

# Enable CORS for Streamlit and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate Core Engines
nlp_engine = RiskSignalPipeline()
feed_manager = LiveFeedManager(risk_pipeline=nlp_engine)
portfolio_mgr = WholesalePortfolioManager()
stress_engine = PortfolioStressTestingEngine(portfolio_manager=portfolio_mgr)


@app.get("/", tags=["General"])
def root():
    """Root endpoint providing platform metadata and navigation links."""
    return {
        "platform": "Sentinel-Risk Unified Platform",
        "author": "S&P Global & CRISIL Campus Hackathon Submission",
        "module_b": "Strategic Wholesale Portfolio Stress Tester",
        "documentation": "/docs",
        "health": "/health",
        "status": "OPERATIONAL"
    }


@app.get("/health", tags=["General"])
def health_check():
    """Health status and loaded engine diagnostics."""
    summary = portfolio_mgr.get_portfolio_summary()
    return {
        "status": "healthy",
        "nlp_engine_ready": True,
        "portfolio_assets_loaded": summary["total_assets_count"],
        "portfolio_notional_usd": summary["total_notional_usd"],
        "scenarios_available": list(stress_engine.scenarios.keys())
    }


@app.get("/api/v1/feed", tags=["Ingestion & Signals"])
def get_feed(scored: bool = Query(True, description="Return items with NLP risk scores")):
    """
    Fetches real-time multi-source unstructured feed (Financial News & Twitter/X).
    If scored=True, returns data augmented with NLP sentiment, category, and impact scores.
    """
    try:
        if scored:
            return feed_manager.ingest_and_score_all()
        return feed_manager.get_combined_raw_feed()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze-risk", response_model=RiskSignalResponse, tags=["AI/NLP Risk Engine"])
def analyze_risk_signal(payload: RiskAnalysisRequest):
    """
    Primary NLP Risk Engine Endpoint:
    Parses unstructured text and outputs structured, machine-readable risk signals:
    - Sentiment Score: continuous score [-1.0, 1.0]
    - Event Classification: categorical taxonomy label
    - Impact Score: predicted market severity [1.0, 10.0]
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be empty.")

    try:
        signal = nlp_engine.process_text(
            text=payload.text,
            source=payload.source or "API Request"
        )
        return signal
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP Risk Engine error: {str(e)}")


@app.get("/api/v1/portfolio", tags=["Wholesale Portfolio"])
def get_portfolio():
    """Returns baseline $1.25B wholesale banking portfolio composition and Basel metrics."""
    try:
        summary = portfolio_mgr.get_portfolio_summary()
        summary["assets"] = portfolio_mgr.get_assets()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/scenarios", tags=["Stress Testing"])
def get_stress_scenarios():
    """Returns calibrated financial stress shock matrices by event type."""
    return stress_engine.scenarios


@app.post("/api/v1/stress-test", tags=["Stress Testing"])
def execute_stress_test(payload: StressTestRequest):
    """
    Downstream Module B: Strategic Portfolio Stress Testing Tool:
    Applies calibrated multi-factor shocks to the wholesale banking portfolio
    based on Event Classification and Impact Score.
    """
    try:
        result = stress_engine.run_stress_test(
            event_classification=payload.event_classification,
            impact_score=payload.impact_score,
            force_run=payload.force_run or False,
            custom_shocks=payload.custom_shocks
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stress testing error: {str(e)}")


@app.post("/api/v1/simulate-event", tags=["End-to-End Pipeline"])
def simulate_end_to_end_event(payload: SimulateEventRequest):
    """
    Full End-to-End Pipeline Trigger:
    1. Ingests raw unstructured headline/tweet
    2. Runs NLP Risk Engine (Sentiment, Classification, Impact)
    3. If Impact Score >= 7.0 (or forced), executes automated Stress Test on Wholesale Portfolio
    """
    try:
        # Step 1: NLP Risk Engine Analysis
        signal = nlp_engine.process_text(
            text=payload.text,
            source=payload.source or "Breaking Event Stream"
        )

        # Step 2: Event-driven Stress Testing Module
        stress_result = stress_engine.run_stress_test(
            event_classification=signal["event_classification"],
            impact_score=signal["impact_score"],
            force_run=payload.force_stress_test or False
        )

        return {
            "status": "SUCCESS",
            "risk_signal": signal,
            "stress_test_result": stress_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution error: {str(e)}")


def run_server():
    """Entry point to launch Uvicorn server."""
    uvicorn.run("src.api.main:app", host=API_HOST, port=API_PORT, reload=False)


if __name__ == "__main__":
    run_server()
