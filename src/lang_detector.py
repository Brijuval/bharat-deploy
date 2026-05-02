"""
Language Detection Module for BharatDeploy.

Detects whether input is Hindi (Devanagari), Hinglish (Roman-script Hindi),
or English and returns a structured result with confidence scores.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, Set

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Hinglish keyword sets — common Hindi words written in Roman script
# ---------------------------------------------------------------------------
HINGLISH_KEYWORDS: Set[str] = {
    # Verbs (Hindi in Roman script only — not English words)
    "banao", "bana", "karo", "kar", "hatao", "hata", "dikhao", "dikha",
    "chalao", "chala", "kholo", "khol", "band", "shuru", "roko", "rok",
    "lagao", "laga", "hatak", "dekho", "dekh",
    "badlo", "badal",
    # Pronouns / determiners
    "mera", "meri", "hamara", "hamari", "mujhe", "humein",
    "yahan", "wahan", "ab", "abhi", "kal", "aaj",
    # Auxiliary verbs / connectors
    "hai", "hain", "tha", "thi", "ho", "hoga", "hogi",
    # Adjectives
    "naya", "nayi", "purana", "purani", "chhota", "bada",
    # Conjunctions / particles
    "aur", "ya", "lekin", "kyunki", "agar", "toh", "matlab",
    "zara", "jaldi", "please",
    # Common Hinglish phrases
    "saari", "saara", "wala", "wali",
}

# ---------------------------------------------------------------------------
# Unicode range for Devanagari script (used for Hindi)
# ---------------------------------------------------------------------------
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


def _has_devanagari(text: str) -> bool:
    """Return True if the text contains any Devanagari characters."""
    return bool(_DEVANAGARI_RE.search(text))


def _hinglish_score(text: str) -> float:
    """
    Return a score in [0, 1] indicating how Hinglish the text is.

    A score of 0.0 means no Hinglish keywords were found;
    1.0 means every word is a Hinglish keyword.
    """
    words = re.findall(r"\b\w+\b", text.lower())
    if not words:
        return 0.0
    matches = sum(1 for w in words if w in HINGLISH_KEYWORDS)
    return matches / len(words)


class LangDetector:
    """Detects the language of a user's input.

    Returns a dict::

        {
            "language": "hi" | "en" | "hinglish" | "unknown",
            "confidence": float,          # 0.0 – 1.0
            "is_hinglish": bool,
        }
    """

    # Threshold above which we classify text as Hinglish
    HINGLISH_THRESHOLD: float = 0.10

    def detect(self, text: str) -> Dict[str, object]:
        """Detect the language of *text* and return a structured result."""
        if not text or not text.strip():
            return {"language": "unknown", "confidence": 0.0, "is_hinglish": False}

        text = text.strip()

        # 1. Devanagari → definitely Hindi
        if _has_devanagari(text):
            return {"language": "hi", "confidence": 0.99, "is_hinglish": False}

        # 2. Check for Hinglish keywords
        hinglish_score = _hinglish_score(text)
        if hinglish_score >= self.HINGLISH_THRESHOLD:
            confidence = min(0.95, 0.50 + hinglish_score)
            return {
                "language": "hinglish",
                "confidence": round(confidence, 2),
                "is_hinglish": True,
            }

        # 3. Try langdetect as fallback
        try:
            from langdetect import detect, DetectorFactory
            from langdetect.lang_detect_exception import LangDetectException

            # Make detection deterministic
            DetectorFactory.seed = 0

            lang_code = detect(text)
            confidence = 0.85

            # langdetect sometimes returns 'hi' for transliterated Hindi
            if lang_code == "hi":
                return {
                    "language": "hi",
                    "confidence": confidence,
                    "is_hinglish": False,
                }

            return {
                "language": lang_code,
                "confidence": confidence,
                "is_hinglish": False,
            }

        except Exception as exc:
            logger.debug("langdetect failed: %s", exc)

        # 4. Default to English
        return {"language": "en", "confidence": 0.70, "is_hinglish": False}


# Module-level convenience function
_detector = LangDetector()


def detect_language(text: str) -> Dict[str, object]:
    """Detect the language of *text*.

    Returns::

        {"language": str, "confidence": float, "is_hinglish": bool}
    """
    return _detector.detect(text)
