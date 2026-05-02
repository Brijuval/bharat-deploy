"""
Tests for src/lang_detector.py
"""

import pytest
from src.lang_detector import LangDetector, detect_language


class TestLangDetector:
    """Unit tests for LangDetector."""

    def setup_method(self):
        self.detector = LangDetector()

    # ------------------------------------------------------------------
    # Devanagari / Hindi
    # ------------------------------------------------------------------

    def test_detects_devanagari_as_hindi(self):
        result = self.detector.detect("नमस्ते, एक EC2 instance बनाओ")
        assert result["language"] == "hi"
        assert result["confidence"] >= 0.95
        assert result["is_hinglish"] is False

    def test_pure_hindi_devanagari(self):
        result = self.detector.detect("मुझे S3 बकेट चाहिए")
        assert result["language"] == "hi"

    # ------------------------------------------------------------------
    # Hinglish (Roman-script Hindi)
    # ------------------------------------------------------------------

    def test_detects_hinglish_banao(self):
        result = self.detector.detect("ek EC2 instance banao")
        assert result["language"] == "hinglish"
        assert result["is_hinglish"] is True

    def test_detects_hinglish_karo(self):
        result = self.detector.detect("yeh server start karo please")
        assert result["language"] == "hinglish"
        assert result["is_hinglish"] is True

    def test_detects_hinglish_dikhao(self):
        result = self.detector.detect("meri saari EC2 instances dikhao")
        assert result["language"] == "hinglish"
        assert result["is_hinglish"] is True

    def test_hinglish_confidence_range(self):
        result = self.detector.detect("banao yeh server karo")
        assert 0.0 < result["confidence"] <= 1.0

    # ------------------------------------------------------------------
    # English
    # ------------------------------------------------------------------

    def test_english_text(self):
        result = self.detector.detect("create an EC2 instance")
        # Should not flag as Hinglish (no Hinglish keywords)
        assert result["is_hinglish"] is False

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_empty_string(self):
        result = self.detector.detect("")
        assert result["language"] == "unknown"
        assert result["confidence"] == 0.0
        assert result["is_hinglish"] is False

    def test_whitespace_only(self):
        result = self.detector.detect("   ")
        assert result["language"] == "unknown"

    def test_none_like_empty(self):
        result = self.detector.detect("")
        assert result["language"] == "unknown"

    def test_result_has_required_keys(self):
        result = self.detector.detect("hello world")
        assert "language" in result
        assert "confidence" in result
        assert "is_hinglish" in result

    def test_confidence_is_float(self):
        result = self.detector.detect("banao karo")
        assert isinstance(result["confidence"], float)

    # ------------------------------------------------------------------
    # Module-level convenience function
    # ------------------------------------------------------------------

    def test_module_level_detect_language(self):
        result = detect_language("EC2 instance banao")
        assert result["is_hinglish"] is True

    def test_module_level_returns_dict(self):
        result = detect_language("hello world")
        assert isinstance(result, dict)
