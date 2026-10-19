"""
Financial Sentiment Analyzer Module.
Computes a granular financial sentiment score in [-1.0, 1.0] using domain-specific
financial terminology, Loughran-McDonald weights, intensifiers, and emoji handling.
"""

import re
from typing import Dict, Any, Tuple
from textblob import TextBlob

# Domain-specific Loughran-McDonald inspired financial dictionary
FINANCIAL_NEGATIVE_WORDS = {
    "default": 2.5, "bankrupt": 2.5, "bankruptcy": 2.5, "insolvent": 2.4,
    "downgrade": 2.0, "downgraded": 2.0, "distress": 2.0, "distressed": 2.0,
    "crisis": 2.2, "freeze": 2.1, "frozen": 2.1, "plummet": 2.0, "plummeted": 2.0,
    "crash": 2.3, "collapse": 2.4, "contagion": 2.5, "subprime": 2.2,
    "haircut": 1.8, "liquidation": 2.0, "shortfall": 1.9, "outage": 1.8,
    "escalate": 1.8, "escalates": 1.8, "war": 2.0, "blockade": 2.0,
    "hawkish": 1.5, "inflation": 1.4, "hike": 1.4, "sanction": 1.9, "sanctions": 1.9,
    "loss": 1.5, "losses": 1.6, "surcharge": 1.6, "lawsuit": 1.6, "probe": 1.5,
    "penalty": 1.7, "investigation": 1.4, "recession": 2.0, "slump": 1.7,
    "blowout": 1.9, "distressed": 2.0, "panic": 2.2, "write-down": 2.1,
    "writedown": 2.1, "curtailment": 1.5, "curb": 1.3, "plunge": 2.0
}

FINANCIAL_POSITIVE_WORDS = {
    "surge": 1.8, "record": 1.5, "profit": 1.6, "profits": 1.6,
    "upgrade": 2.0, "upgraded": 2.0, "growth": 1.5, "rally": 1.8,
    "bullish": 2.0, "gain": 1.4, "gains": 1.5, "outperform": 1.9,
    "recovery": 1.7, "rebound": 1.8, "approval": 1.8, "approved": 1.8,
    "expansion": 1.5, "breakthrough": 2.1, "easing": 1.4, "rate cut": 1.5,
    "inflow": 1.6, "dividend": 1.4, "solvency": 1.7, "resilience": 1.7,
    "stimulus": 1.6, "deal": 1.3, "alliance": 1.4, "exceed": 1.6, "exceeded": 1.6
}

INTENSIFIERS = {
    "massive": 1.5, "critical": 1.6, "urgent": 1.4, "unprecedented": 1.7,
    "emergency": 1.6, "severe": 1.6, "acute": 1.5, "sharp": 1.3,
    "extremely": 1.5, "hugely": 1.4, "record": 1.4
}

EMOJI_SENTIMENT = {
    "🚨": -1.5, "⚠️": -1.2, "🔴": -0.8, "📉": -1.0, "💥": -1.2,
    "🚀": 1.5, "🟢": 0.8, "📈": 1.0, "🔥": 0.5, "💎": 0.8
}


class FinancialSentimentAnalyzer:
    """Specialized financial sentiment engine returning continuous scores from -1.0 to +1.0."""

    def __init__(self):
        self.neg_words = FINANCIAL_NEGATIVE_WORDS
        self.pos_words = FINANCIAL_POSITIVE_WORDS
        self.intensifiers = INTENSIFIERS
        self.emoji_map = EMOJI_SENTIMENT

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the financial sentiment of a news text or tweet.

        Returns:
            Dict containing:
                - sentiment_score: float in [-1.0, 1.0]
                - sentiment_label: str
                - confidence: float in [0.0, 1.0]
                - raw_components: details on pos/neg counts and modifiers
        """
        if not text or not text.strip():
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "Neutral",
                "confidence": 0.5,
                "raw_components": {}
            }

        clean_text = text.lower()
        words = re.findall(r"\b[a-z0-9\-]+\b", clean_text)

        # Baseline semantic polarity from TextBlob
        blob_polarity = TextBlob(text).sentiment.polarity

        pos_score = 0.0
        neg_score = 0.0
        multiplier = 1.0

        # Scan for intensifiers
        for word in words:
            if word in self.intensifiers:
                multiplier = max(multiplier, self.intensifiers[word])

        # Scan financial dictionary
        for i, word in enumerate(words):
            # Check single word
            if word in self.pos_words:
                pos_score += self.pos_words[word]
            elif word in self.neg_words:
                neg_score += self.neg_words[word]

            # Check two-word bigrams
            if i < len(words) - 1:
                bigram = f"{word} {words[i+1]}"
                if bigram in self.pos_words:
                    pos_score += self.pos_words[bigram]
                elif bigram in self.neg_words:
                    neg_score += self.neg_words[bigram]

        # Scan emojis in original text
        for emoji, val in self.emoji_map.items():
            if emoji in text:
                if val > 0:
                    pos_score += val
                else:
                    neg_score += abs(val)

        # Apply intensifier multiplier
        pos_score *= multiplier
        neg_score *= multiplier

        # Compute raw weighted balance
        total_signal = pos_score + neg_score
        if total_signal > 0:
            dict_score = (pos_score - neg_score) / (total_signal + 1.0)
            # Combine lexicon with NLP polarity (lexicon weighted 70%, general NLP 30%)
            combined = 0.75 * dict_score + 0.25 * blob_polarity
        else:
            combined = blob_polarity

        # Clamp tightly to [-1.0, 1.0]
        final_score = max(-1.0, min(1.0, float(combined)))
        final_score = round(final_score, 4)

        # Label classification
        if final_score <= -0.55:
            label = "Extremely Bearish"
        elif final_score <= -0.15:
            label = "Bearish"
        elif final_score >= 0.55:
            label = "Extremely Bullish"
        elif final_score >= 0.15:
            label = "Bullish"
        else:
            label = "Neutral"

        # Confidence calculation
        confidence = min(0.98, max(0.60, round(0.55 + (abs(final_score) * 0.35) + (min(len(words), 30) / 100), 2)))

        return {
            "sentiment_score": final_score,
            "sentiment_label": label,
            "confidence": confidence,
            "raw_components": {
                "pos_weight": round(pos_score, 2),
                "neg_weight": round(neg_score, 2),
                "intensifier": multiplier,
                "textblob_polarity": round(blob_polarity, 4)
            }
        }
