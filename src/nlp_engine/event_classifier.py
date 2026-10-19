"""
Financial Event Classification Module.
Classifies unstructured financial news and social media texts into institutional categories:
- Geopolitical
- Credit Event
- Macroeconomic
- Regulatory/Legal
- Cyber/Systemic Risk
- Merger/Acquisition
- Product Launch
"""

import re
from typing import Dict, Any, List, Tuple

# Comprehensive taxonomy keywords and semantic anchors
TAXONOMY_PATTERNS = {
    "Geopolitical": [
        "war", "military", "blockade", "sanction", "sanctions", "strait", "hormuz", "tanker",
        "conflict", "missile", "defense", "tensions", "geopolitical", "iran", "russia", "china",
        "ukraine", "middle east", "embargo", "naval", "sovereignty", "hostilities", "treaty"
    ],
    "Credit Event": [
        "default", "defaults", "bankrupt", "bankruptcy", "downgrade", "downgrades", "liquidation",
        "credit spread", "cds", "subordinated", "non-performing", "npl", "redemptions", "freeze",
        "liquidity shortfall", "distressed debt", "haircut", "insolvency", "junk status",
        "restructuring", "covenant breach", "bad loan", "credit rating"
    ],
    "Macroeconomic": [
        "inflation", "cpi", "interest rate", "rate hike", "federal reserve", "fed", "ecb",
        "central bank", "gdp", "recession", "stagflation", "unemployment", "treasury yields",
        "yield curve", "monetary policy", "quantitative tightening", "basis points", "bps",
        "wage growth", "macroeconomic", "macro", "sofr"
    ],
    "Regulatory/Legal": [
        "regulator", "regulatory", "basel", "compliance", "lawsuit", "sec", "doj", "probe",
        "antitrust", "investigation", "surcharge", "capital buffer", "fine", "penalties",
        "subpoena", "ruling", "mandate", "supervision", "legislation"
    ],
    "Cyber/Systemic Risk": [
        "cyber", "outage", "hack", "hacked", "ransomware", "swift", "clearing", "settlement",
        "interbank", "payment network", "infrastructure disruption", "zero-day", "systemic risk",
        "cloud outage", "grid failure", "malware", "data breach"
    ],
    "Merger/Acquisition": [
        "merger", "acquisition", "acquire", "takeover", "buyout", "lbo", "deal", "antitrust block",
        "consolidation", "tender offer", "spoff", "divestiture", "megamerger", "arbitrage"
    ],
    "Product Launch": [
        "launch", "launches", "product", "rollout", "unveiled", "innovation", "quantum", "ai",
        "expansion", "contract", "partnership", "clean energy", "renewable", "capex", "initiative"
    ]
}

KNOWN_FINANCIAL_ENTITIES = [
    "Federal Reserve", "US Treasury", "ECB", "Bank of England", "Basel Committee",
    "JPMorgan Chase", "Citigroup", "Deutsche Bank", "Barclays", "BNP Paribas",
    "Morgan Stanley", "Goldman Sachs", "Apple", "Microsoft", "Nvidia", "Blackstone",
    "Carlyle", "WTI", "Brent Crude", "S&P 500", "Nasdaq", "SWIFT"
]


class FinancialEventClassifier:
    """Classifies financial texts into standardized risk event categories."""

    def __init__(self):
        self.taxonomy = TAXONOMY_PATTERNS
        self.known_entities = KNOWN_FINANCIAL_ENTITIES

    def extract_entities(self, text: str) -> List[str]:
        """Extracts recognizable financial entities, tickers, and cashtags."""
        found = []
        text_lower = text.lower()

        # Check known entities
        for entity in self.known_entities:
            if entity.lower() in text_lower:
                found.append(entity)

        # Check cashtags ($AAPL, $JPM, etc.)
        cashtags = re.findall(r"\$[A-Z]{1,5}\b", text)
        for tag in cashtags:
            if tag not in found:
                found.append(tag)

        # Check hashtags (#Geopolitics, etc.)
        hashtags = re.findall(r"#[A-Za-z0-9_]+\b", text)
        for tag in hashtags[:3]:
            if tag not in found:
                found.append(tag)

        if not found:
            # Fallback general subject extraction
            first_words = " ".join(text.split()[:4])
            found.append(first_words)

        return found

    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classifies the text and returns primary category, confidence score, and distribution.
        """
        if not text or not text.strip():
            return {
                "primary_category": "Macroeconomic",
                "confidence": 0.50,
                "all_scores": {cat: 0.0 for cat in self.taxonomy},
                "entities": []
            }

        text_lower = text.lower()
        words = set(re.findall(r"\b[a-z0-9\-]+\b", text_lower))

        scores: Dict[str, float] = {}
        for category, keywords in self.taxonomy.items():
            category_score = 0.0
            for kw in keywords:
                if " " in kw:
                    # Multi-word phrase check
                    if kw in text_lower:
                        category_score += 2.5
                else:
                    if kw in words:
                        category_score += 1.5

            scores[category] = category_score

        # Find category with highest match
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_score = sorted_cats[0]

        total_score = sum(scores.values())
        if total_score > 0:
            confidence = min(0.97, max(0.55, round((top_score / total_score) * 0.7 + 0.25, 2)))
        else:
            # Default to Macroeconomic if ambiguous
            top_cat = "Macroeconomic"
            confidence = 0.50

        entities = self.extract_entities(text)

        return {
            "primary_category": top_cat,
            "confidence": confidence,
            "all_scores": {k: round(v, 2) for k, v in scores.items()},
            "entities": entities
        }
