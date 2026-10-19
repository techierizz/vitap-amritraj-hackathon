"""
Unit Tests for Unified AI/NLP Risk Engine.
Validates Sentiment Scoring, Event Classification, and Impact Scoring accuracy.
"""

from src.nlp_engine.sentiment_analyzer import FinancialSentimentAnalyzer
from src.nlp_engine.event_classifier import FinancialEventClassifier
from src.nlp_engine.impact_scorer import MarketImpactScorer
from src.nlp_engine.risk_pipeline import RiskSignalPipeline


def test_sentiment_analyzer_negative():
    analyzer = FinancialSentimentAnalyzer()
    text = "Massive default wave hits commercial real estate debt as regional bank freezes redemptions."
    res = analyzer.analyze(text)
    assert res["sentiment_score"] < -0.30
    assert "Bearish" in res["sentiment_label"]
    assert 0.0 <= res["confidence"] <= 1.0


def test_sentiment_analyzer_positive():
    analyzer = FinancialSentimentAnalyzer()
    text = "Record profit growth and sovereign capital expansion drives strong bullish market rally."
    res = analyzer.analyze(text)
    assert res["sentiment_score"] > 0.30
    assert "Bullish" in res["sentiment_label"]


def test_event_classifier_geopolitical():
    classifier = FinancialEventClassifier()
    text = "Strait of Hormuz naval blockade escalates defense tensions and crude oil prices."
    res = classifier.classify(text)
    assert res["primary_category"] == "Geopolitical"
    assert res["confidence"] >= 0.50


def test_event_classifier_credit():
    classifier = FinancialEventClassifier()
    text = "Tier-1 bank faces acute liquidity freeze and commercial loan default wave."
    res = classifier.classify(text)
    assert res["primary_category"] == "Credit Event"


def test_impact_scorer_high_severity():
    scorer = MarketImpactScorer()
    text = "Critical emergency: zero-day exploit triggers systemic failure in SWIFT clearing network."
    res = scorer.score(text=text, sentiment_score=-0.85, category="Cyber/Systemic Risk", entities=["SWIFT"])
    assert res["impact_score"] >= 7.0
    assert res["trigger_stress_test"] is True


def test_risk_pipeline_end_to_end():
    pipeline = RiskSignalPipeline()
    text = "Federal Reserve signals aggressive 75 bps emergency rate hike as inflation reaches 6.2%."
    signal = pipeline.process_text(text, source="Financial News Wire")

    # Verify all required hackathon output fields are present
    assert "signal_id" in signal
    assert "timestamp" in signal
    assert "source" in signal
    assert "sentiment_score" in signal
    assert -1.0 <= signal["sentiment_score"] <= 1.0
    assert "event_classification" in signal
    assert signal["event_classification"] in [
        "Geopolitical", "Credit Event", "Macroeconomic",
        "Regulatory/Legal", "Cyber/Systemic Risk", "Merger/Acquisition", "Product Launch"
    ]
    assert "impact_score" in signal
    assert 1.0 <= signal["impact_score"] <= 10.0
    assert "trigger_stress_test" in signal
    assert isinstance(signal["trigger_stress_test"], bool)
