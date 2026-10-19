"""
Pydantic Schemas for API Data Contracts.
Strictly defines the input/output schemas for the AI/NLP Risk Engine and Stress Testing Module.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RiskAnalysisRequest(BaseModel):
    """Input payload for raw unstructured text risk analysis."""
    text: str = Field(
        ...,
        description="Raw financial news article, headline, or social media tweet",
        example="Federal Reserve signals emergency 75 bps rate hike amid stubborn 6.2% CPI inflation."
    )
    source: Optional[str] = Field(
        "Direct API Client",
        description="Source identifier (e.g., 'Reuters', 'Twitter/X', 'Bloomberg')"
    )


class RiskSignalResponse(BaseModel):
    """Structured machine-readable risk signal emitted by the AI/NLP Risk Engine."""
    signal_id: str
    timestamp: str
    source: str
    headline_or_text: str
    entity_mentioned: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score in [-1.0, 1.0]")
    sentiment_label: str
    sentiment_confidence: float
    event_classification: str = Field(..., description="Categorical label: Geopolitical, Credit Event, Macroeconomic, etc.")
    category_confidence: float
    impact_score: float = Field(..., ge=1.0, le=10.0, description="Predicted market severity score [1.0 - 10.0]")
    severity_level: str
    trigger_stress_test: bool
    rationale: str
    raw_details: Optional[Dict[str, Any]] = None


class StressTestRequest(BaseModel):
    """Input payload for portfolio stress testing simulation."""
    event_classification: str = Field(..., example="Geopolitical")
    impact_score: float = Field(..., ge=1.0, le=10.0, example=8.8)
    force_run: Optional[bool] = Field(False, description="Force simulation even if impact < 7.0")
    custom_shocks: Optional[Dict[str, float]] = None


class SimulateEventRequest(BaseModel):
    """End-to-end pipeline payload: unstructured text -> risk signal -> stress test execution."""
    text: str = Field(
        ...,
        example="European banking authority intervenes as major regional bank freezes redemptions on $4.5B commercial property debt."
    )
    source: Optional[str] = Field("Breaking News Terminal")
    force_stress_test: Optional[bool] = Field(False)
