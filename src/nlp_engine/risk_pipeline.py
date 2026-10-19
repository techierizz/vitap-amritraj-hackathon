"""
Unified AI/NLP Risk Engine Pipeline.
Coordinates Sentiment Analysis, Event Classification, and Impact Scoring to generate
standardized, machine-readable financial risk signals.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .sentiment_analyzer import FinancialSentimentAnalyzer
from .event_classifier import FinancialEventClassifier
from .impact_scorer import MarketImpactScorer


class RiskSignalPipeline:
    """Unified AI/NLP Risk Engine processing unstructured text into risk signals."""

    def __init__(self):
        self.sentiment_analyzer = FinancialSentimentAnalyzer()
        self.event_classifier = FinancialEventClassifier()
        self.impact_scorer = MarketImpactScorer()

    def process_text(
        self,
        text: str,
        source: str = "Unspecified",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processes a single unstructured text and outputs a structured risk signal.

        Returns dictionary conforming to the required hackathon fields:
            - sentiment_score: float [-1.0 to 1.0]
            - event_classification: str
            - impact_score: float [1 to 10]
        plus extended enterprise audit fields.
        """
        metadata = metadata or {}
        timestamp = metadata.get("timestamp") or datetime.now(timezone.utc).isoformat()
        signal_id = f"SIG-{uuid.uuid4().hex[:8].upper()}"

        # 1. Financial Sentiment Analysis
        sentiment_res = self.sentiment_analyzer.analyze(text)
        sentiment_score = sentiment_res["sentiment_score"]
        sentiment_label = sentiment_res["sentiment_label"]
        sentiment_conf = sentiment_res["confidence"]

        # 2. Event Classification & Entity Extraction
        event_res = self.event_classifier.classify(text)
        category = event_res["primary_category"]
        category_conf = event_res["confidence"]
        entities = event_res["entities"]

        # 3. Market Impact Scoring
        impact_res = self.impact_scorer.score(
            text=text,
            sentiment_score=sentiment_score,
            category=category,
            entities=entities
        )
        impact_score = impact_res["impact_score"]
        severity_level = impact_res["severity_level"]
        trigger_stress_test = impact_res["trigger_stress_test"]

        # 4. Generate Audit Rationale
        rationale = (
            f"Detected {category} with {sentiment_label.lower()} sentiment "
            f"({sentiment_score:+.2f}). Impact score assessed at {impact_score}/10 "
            f"({severity_level}). Stress test trigger: {'ACTIVE' if trigger_stress_test else 'STANDBY'}."
        )

        return {
            "signal_id": signal_id,
            "timestamp": timestamp,
            "source": source,
            "headline_or_text": text,
            "entity_mentioned": ", ".join(entities) if entities else "Broad Market / Systemic",
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "sentiment_confidence": sentiment_conf,
            "event_classification": category,
            "category_confidence": category_conf,
            "impact_score": impact_score,
            "severity_level": severity_level,
            "trigger_stress_test": trigger_stress_test,
            "rationale": rationale,
            "raw_details": {
                "sentiment_components": sentiment_res["raw_components"],
                "impact_breakdown": impact_res["score_breakdown"],
                "all_category_matches": event_res["all_scores"]
            }
        }

    def process_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes a collection of text records in batch."""
        results = []
        for item in items:
            text = item.get("content") or item.get("headline") or item.get("tweet_text") or item.get("text", "")
            source = item.get("source") or "Feed Stream"
            signal = self.process_text(text=text, source=source, metadata=item)
            results.append(signal)
        return results
