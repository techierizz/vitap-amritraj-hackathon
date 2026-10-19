"""
Twitter/X Social Media Ingestion Module.
Ingests, cleans, and standardizes social media posts and financial tweets.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..config import TWEETS_FEED_PATH


class TwitterIngester:
    """Ingests financial tweets and microblogging streams."""

    def __init__(self, feed_path: Optional[Path] = None):
        self.feed_path = feed_path or TWEETS_FEED_PATH

    def load_cached_tweets(self) -> List[Dict[str, Any]]:
        """Loads curated financial tweets from repository data."""
        if not self.feed_path.exists():
            return []
        with open(self.feed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def simulate_incoming_tweet(
        self,
        handle: str,
        tweet_text: str,
        cashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Creates a standardized tweet record for user input or automated stream simulation."""
        import uuid
        from datetime import datetime, timezone

        tags = cashtags or []
        tag_str = " ".join([f"${t.replace('$', '')}" for t in tags])
        full_text = f"{tweet_text} {tag_str}".strip()

        return {
            "id": f"TWEET-SIM-{uuid.uuid4().hex[:6].upper()}",
            "source": "Twitter/X Live Stream",
            "handle": handle if handle.startswith("@") else f"@{handle}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tweet_text": full_text
        }
