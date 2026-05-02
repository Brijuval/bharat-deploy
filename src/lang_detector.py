"""
Language Detector for BharatDeploy
Detects Hindi, Tamil, Kannada, English, and Hinglish (Roman script Hindi)
"""

from typing import Tuple

try:
    from langdetect import detect, detect_langs, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


# Hinglish keywords commonly used by Indian developers
HINGLISH_KEYWORDS = {
    # Action verbs
    "banao": "create",
    "bana": "create",
    "banao": "create",
    "karo": "do",
    "kar": "do",
    "hatao": "delete",
    "hata": "delete",
    "mitao": "delete",
    "dikhao": "show",
    "dekho": "show",
    "chalao": "run",
    "chala": "run",
    "shuru": "start",
    "band": "stop",
    "rokо": "stop",
    "deploy": "deploy",
    "list": "list",
    "update": "update",
    # Cloud resources
    "server": "server",
    "bucket": "bucket",
    "database": "database",
    "function": "function",
    "app": "app",
    # Common phrases
    "mera": "my",
    "mere": "my",
    "meri": "my",
    "naya": "new",
    "nayi": "new",
    "purana": "old",
    "sab": "all",
    "sabka": "all",
}

# Hindi Unicode script words
HINDI_SCRIPT_PATTERNS = [
    "बनाओ", "करो", "हटाओ", "दिखाओ", "चलाओ",
    "शुरू", "बंद", "मेरा", "नया", "सब",
    "डिप्लॉय", "सर्वर", "बकेट", "लिस्ट",
]

# Language code mapping
LANGUAGE_NAMES = {
    "hi": "Hindi",
    "ta": "Tamil",
    "kn": "Kannada",
    "en": "English",
    "hinglish": "Hinglish",
}


def detect_hinglish(text: str) -> Tuple[bool, float]:
    """
    Detect if text contains Hinglish (Roman script Hindi).

    Args:
        text: Input text to analyze

    Returns:
        Tuple of (is_hinglish, confidence_score)
    """
    text_lower = text.lower()
    words = text_lower.split()

    matched_keywords = sum(1 for word in words if word in HINGLISH_KEYWORDS)

    if len(words) == 0:
        return False, 0.0

    confidence = matched_keywords / len(words)

    # Consider Hinglish if at least 20% of words match OR at least 1 keyword found
    # in short sentences
    is_hinglish = confidence >= 0.2 or (len(words) <= 5 and matched_keywords >= 1)

    return is_hinglish, min(confidence * 2, 1.0)


def detect_hindi_script(text: str) -> bool:
    """Check if text contains Hindi (Devanagari) script characters."""
    for char in text:
        code_point = ord(char)
        # Devanagari Unicode range: 0x0900 to 0x097F
        if 0x0900 <= code_point <= 0x097F:
            return True
    return False


def detect_tamil_script(text: str) -> bool:
    """Check if text contains Tamil script characters."""
    for char in text:
        code_point = ord(char)
        # Tamil Unicode range: 0x0B80 to 0x0BFF
        if 0x0B80 <= code_point <= 0x0BFF:
            return True
    return False


def detect_kannada_script(text: str) -> bool:
    """Check if text contains Kannada script characters."""
    for char in text:
        code_point = ord(char)
        # Kannada Unicode range: 0x0C80 to 0x0CFF
        if 0x0C80 <= code_point <= 0x0CFF:
            return True
    return False


def detect_language(text: str) -> dict:
    """
    Detect the language of the given text.

    Supports: Hindi (hi), Tamil (ta), Kannada (kn), English (en), Hinglish

    Args:
        text: Input text to detect language for

    Returns:
        Dictionary with keys:
            - language: language code (hi/ta/kn/en/hinglish)
            - language_name: Human-readable language name
            - confidence: Confidence score between 0.0 and 1.0
            - detected_keywords: List of matched Hinglish keywords (if applicable)
    """
    if not text or not text.strip():
        return {
            "language": "en",
            "language_name": "English",
            "confidence": 0.5,
            "detected_keywords": [],
        }

    # Check for Hindi (Devanagari) script first
    if detect_hindi_script(text):
        return {
            "language": "hi",
            "language_name": "Hindi",
            "confidence": 0.95,
            "detected_keywords": [],
        }

    # Check for Tamil script
    if detect_tamil_script(text):
        return {
            "language": "ta",
            "language_name": "Tamil",
            "confidence": 0.95,
            "detected_keywords": [],
        }

    # Check for Kannada script
    if detect_kannada_script(text):
        return {
            "language": "kn",
            "language_name": "Kannada",
            "confidence": 0.95,
            "detected_keywords": [],
        }

    # Check for Hinglish (Roman script Hindi)
    is_hinglish, hinglish_confidence = detect_hinglish(text)
    if is_hinglish:
        text_lower = text.lower()
        words = text_lower.split()
        matched = [word for word in words if word in HINGLISH_KEYWORDS]
        return {
            "language": "hinglish",
            "language_name": "Hinglish",
            "confidence": hinglish_confidence,
            "detected_keywords": matched,
        }

    # Use langdetect library for other languages
    if LANGDETECT_AVAILABLE:
        try:
            langs = detect_langs(text)
            if langs:
                top = langs[0]
                lang_code = top.lang
                confidence = top.prob

                # Map langdetect codes to our supported codes
                if lang_code in ("hi", "ta", "kn", "en"):
                    return {
                        "language": lang_code,
                        "language_name": LANGUAGE_NAMES.get(lang_code, lang_code),
                        "confidence": confidence,
                        "detected_keywords": [],
                    }
        except (LangDetectException, Exception):
            pass

    # Default to English
    return {
        "language": "en",
        "language_name": "English",
        "confidence": 0.7,
        "detected_keywords": [],
    }


def get_hinglish_action(text: str) -> str:
    """
    Extract the action intent from Hinglish text.

    Args:
        text: Hinglish input text

    Returns:
        Action string (create/delete/show/run/start/stop/list/deploy)
    """
    text_lower = text.lower()
    words = text_lower.split()

    action_priority = ["deploy", "create", "delete", "show", "run", "start", "stop", "list"]

    for word in words:
        if word in HINGLISH_KEYWORDS:
            action = HINGLISH_KEYWORDS[word]
            if action in action_priority:
                return action

    return "deploy"  # default action
