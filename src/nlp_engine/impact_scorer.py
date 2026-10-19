"""
Market Impact Scorer Module.
Predicts a calibrated severity score from 1.0 to 10.0 indicating the potential
financial market disruption, systemic contagion risk, and capital impact.
"""

import re
from typing import Dict, Any, List

CATEGORY_IMPACT_WEIGHTS = {
    "Geopolitical": 1.35,
    "Credit Event": 1.40,
    "Macroeconomic": 1.25,
    "Cyber/Systemic Risk": 1.30,
    "Regulatory/Legal": 1.10,
    "Merger/Acquisition": 0.95,
    "Product Launch": 0.80
}

HIGH_IMPACT_MARKERS = [
    "unprecedented", "catastrophic", "emergency", "crisis", "contagion",
    "liquidity freeze", "default wave", "soared", "plummeted", "war",
    "blockade", "shutdown", "halt", "halts", "halted", "collapse",
    "critical", "outage", "spiking", "zero-day", "downgraded to junk",
    "systemic"
]

FINANCIAL_SCALE_MARKERS = [
    r"\$\d+(\.\d+)?\s*(billion|trillion|b|t)\b",
    r"\b(fed|federal reserve|ecb|imf|swift|central bank)\b",
    r"\b(crude oil|brent|wti|treasury)\b"
]


class MarketImpactScorer:
    """Computes a predicted market impact score from 1.0 to 10.0."""

    def __init__(self):
        self.category_weights = CATEGORY_IMPACT_WEIGHTS
        self.impact_markers = HIGH_IMPACT_MARKERS
        self.scale_patterns = [re.compile(p, re.IGNORECASE) for p in FINANCIAL_SCALE_MARKERS]

    def score(
        self,
        text: str,
        sentiment_score: float,
        category: str,
        entities: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates the calibrated 1.0 to 10.0 impact score.
        """
        text_lower = text.lower()

        # Component 1: Sentiment Magnitude [0.0 to 3.5]
        # Strong negative news carries higher downside disruption than positive news
        abs_sent = abs(sentiment_score)
        if sentiment_score < 0:
            sentiment_component = abs_sent * 3.5
        else:
            sentiment_component = abs_sent * 2.2

        # Component 2: Category Base Weight [1.5 to 3.0]
        cat_weight = self.category_weights.get(category, 1.0)
        category_component = cat_weight * 2.0

        # Component 3: Marker & Urgency Intensity [0.0 to 2.5]
        marker_hits = sum(1 for m in self.impact_markers if m in text_lower)
        marker_component = min(2.5, marker_hits * 0.75)

        # Component 4: Systemic Scale & Entity Prominence [0.0 to 1.5]
        scale_hits = sum(1 for pattern in self.scale_patterns if pattern.search(text))
        entity_bonus = min(0.7, len(entities) * 0.25)
        scale_component = min(1.5, (scale_hits * 0.6) + entity_bonus)

        # Raw aggregation
        raw_score = 1.0 + sentiment_component + category_component + marker_component + scale_component

        # Normalization and clamping to [1.0, 10.0]
        final_impact = max(1.0, min(10.0, float(raw_score)))
        final_impact = round(final_impact, 1)

        # Qualitative classification
        if final_impact >= 8.5:
            severity = "Critical Tail Risk"
        elif final_impact >= 7.0:
            severity = "High Systemic Risk"
        elif final_impact >= 5.0:
            severity = "Elevated Risk"
        elif final_impact >= 3.0:
            severity = "Moderate Risk"
        else:
            severity = "Low / Informational"

        # Auto-trigger determination (threshold >= 7.0)
        trigger_stress_test = final_impact >= 7.0

        return {
            "impact_score": final_impact,
            "severity_level": severity,
            "trigger_stress_test": trigger_stress_test,
            "score_breakdown": {
                "sentiment_contribution": round(sentiment_component, 2),
                "category_base": round(category_component, 2),
                "urgency_markers": round(marker_component, 2),
                "systemic_scale": round(scale_component, 2)
            }
        }
