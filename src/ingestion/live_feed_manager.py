"""
Live Feed Manager Module.
Aggregates multi-source feeds (Financial News & Twitter/X), manages live simulation,
and connects raw unstructured ingestion to the AI/NLP Risk Engine.
"""

from typing import List, Dict, Any, Optional
from .news_ingestion import FinancialNewsIngester
from .twitter_ingestion import TwitterIngester
from ..nlp_engine.risk_pipeline import RiskSignalPipeline


class LiveFeedManager:
    """Central coordinator for ingesting and processing multi-source unstructured streams."""

    def __init__(self, risk_pipeline: Optional[RiskSignalPipeline] = None):
        self.news_ingester = FinancialNewsIngester()
        self.twitter_ingester = TwitterIngester()
        self.risk_pipeline = risk_pipeline or RiskSignalPipeline()

    def get_combined_raw_feed(self) -> List[Dict[str, Any]]:
        """Retrieves and merges raw items from both News and Twitter sources."""
        news_items = self.news_ingester.load_cached_feed()
        tweets_items = self.twitter_ingester.load_cached_tweets()

        normalized = []
        for n in news_items:
            normalized.append({
                "feed_id": n["id"],
                "source_type": "Financial News",
                "source_name": n.get("source", "News"),
                "timestamp": n.get("timestamp"),
                "text": f"{n.get('headline', '')}. {n.get('content', '')}",
                "display_title": n.get("headline", ""),
                "original_record": n
            })

        for t in tweets_items:
            normalized.append({
                "feed_id": t["id"],
                "source_type": "Twitter/X",
                "source_name": t.get("handle", "@TwitterTrader"),
                "timestamp": t.get("timestamp"),
                "text": t.get("tweet_text", ""),
                "display_title": f"{t.get('handle')}: {t.get('tweet_text', '')[:65]}...",
                "original_record": t
            })

        # Sort chronologically if timestamps available
        normalized.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        return normalized

    def ingest_and_score_all(self) -> List[Dict[str, Any]]:
        """Processes all combined feed items through the NLP Risk Engine."""
        raw_feed = self.get_combined_raw_feed()
        processed_signals = []

        for item in raw_feed:
            signal = self.risk_pipeline.process_text(
                text=item["text"],
                source=f"{item['source_type']} ({item['source_name']})",
                metadata={"timestamp": item["timestamp"], "feed_id": item["feed_id"]}
            )
            # Attach visual metadata
            signal["display_title"] = item["display_title"]
            signal["source_type"] = item["source_type"]
            processed_signals.append(signal)

        return processed_signals
