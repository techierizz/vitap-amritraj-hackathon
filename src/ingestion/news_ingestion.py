"""
Financial News Ingestion Module.
Ingests structured and unstructured news feeds from local JSON caches,
GDELT style event streams, and optional live RSS feeds.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from ..config import NEWS_FEED_PATH


class FinancialNewsIngester:
    """Ingests and standardizes financial news articles from multiple sources."""

    def __init__(self, feed_path: Optional[Path] = None):
        self.feed_path = feed_path or NEWS_FEED_PATH

    def load_cached_feed(self) -> List[Dict[str, Any]]:
        """Loads curated financial news items from repository data."""
        if not self.feed_path.exists():
            return []
        with open(self.feed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def fetch_live_rss(self, rss_url: str = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Attempts to fetch live RSS headlines.
        Falls back seamlessly to local curated articles if offline or timeout.
        """
        try:
            resp = requests.get(rss_url, timeout=4.0, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                items = []
                for idx, item in enumerate(root.findall(".//item")[:limit]):
                    title = item.findtext("title") or "Financial Market Update"
                    desc = item.findtext("description") or title
                    pub_date = item.findtext("pubDate") or ""
                    items.append({
                        "id": f"LIVE-RSS-{idx+1:03d}",
                        "source": "Live Yahoo Finance RSS",
                        "timestamp": pub_date,
                        "headline": title,
                        "content": desc
                    })
                if items:
                    return items
        except Exception:
            pass
        # Fallback to local curated feed
        return self.load_cached_feed()[:limit]
