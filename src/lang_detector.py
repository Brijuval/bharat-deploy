from langdetect import detect, DetectorFactory
from typing import Dict

# Make language detection deterministic
DetectorFactory.seed = 0

HINGLISH_KEYWORDS = {
    'banao': 'create',
    'karo': 'do',
    'hatao': 'delete',
    'dikhao': 'show',
    'suno': 'listen',
    'aao': 'come',
    'jao': 'go',
    'dekho': 'see',
    'samjho': 'understand',
}


class LanguageDetector:
    def detect_language(self, text: str) -> Dict:
        """Detect language of input text.

        Returns a dict with keys:
            language  - ISO 639-1 code ('hi', 'en', …)
            confidence - float between 0 and 1
            is_hinglish - bool
        """
        words = text.lower().split()
        is_hinglish = any(keyword in words for keyword in HINGLISH_KEYWORDS)

        try:
            lang_code = detect(text)
            if is_hinglish or lang_code == 'hi':
                return {
                    "language": "hi",
                    "confidence": 0.95,
                    "is_hinglish": is_hinglish,
                }
            return {
                "language": lang_code,
                "confidence": 0.85,
                "is_hinglish": False,
            }
        except Exception:
            return {
                "language": "en",
                "confidence": 0.7,
                "is_hinglish": False,
            }
