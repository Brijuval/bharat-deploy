"""
Tests for Language Detector module
"""

import pytest
from src.lang_detector import (
    detect_language,
    detect_hinglish,
    detect_hindi_script,
    detect_tamil_script,
    detect_kannada_script,
    get_hinglish_action,
    HINGLISH_KEYWORDS,
)


class TestDetectHindiScript:
    def test_hindi_devanagari_text(self):
        assert detect_hindi_script("नमस्ते") is True

    def test_hindi_mixed_with_english(self):
        assert detect_hindi_script("Hello नमस्ते") is True

    def test_english_only(self):
        assert detect_hindi_script("Hello World") is False

    def test_empty_string(self):
        assert detect_hindi_script("") is False

    def test_hindi_keywords(self):
        assert detect_hindi_script("सर्वर बनाओ") is True


class TestDetectTamilScript:
    def test_tamil_text(self):
        assert detect_tamil_script("வணக்கம்") is True

    def test_english_only(self):
        assert detect_tamil_script("Hello World") is False

    def test_empty_string(self):
        assert detect_tamil_script("") is False


class TestDetectKannadaScript:
    def test_kannada_text(self):
        assert detect_kannada_script("ನಮಸ್ಕಾರ") is True

    def test_english_only(self):
        assert detect_kannada_script("Hello World") is False

    def test_empty_string(self):
        assert detect_kannada_script("") is False


class TestDetectHinglish:
    def test_hinglish_with_banao(self):
        is_hinglish, confidence = detect_hinglish("flask app banao")
        assert is_hinglish is True
        assert confidence > 0

    def test_hinglish_with_karo(self):
        is_hinglish, confidence = detect_hinglish("deploy karo")
        assert is_hinglish is True

    def test_hinglish_with_hatao(self):
        is_hinglish, confidence = detect_hinglish("server hatao")
        assert is_hinglish is True

    def test_hinglish_with_dikhao(self):
        is_hinglish, confidence = detect_hinglish("EC2 instances dikhao")
        assert is_hinglish is True

    def test_pure_english(self):
        is_hinglish, confidence = detect_hinglish("create a new EC2 instance")
        assert is_hinglish is False

    def test_empty_string(self):
        is_hinglish, confidence = detect_hinglish("")
        assert is_hinglish is False
        assert confidence == 0.0

    def test_single_hinglish_word(self):
        is_hinglish, confidence = detect_hinglish("banao")
        assert is_hinglish is True

    def test_multiple_hinglish_keywords(self):
        is_hinglish, confidence = detect_hinglish("mera naya server banao")
        assert is_hinglish is True
        assert confidence > 0.5


class TestDetectLanguage:
    def test_hindi_devanagari(self):
        result = detect_language("सर्वर बनाओ")
        assert result["language"] == "hi"
        assert result["confidence"] >= 0.9
        assert result["language_name"] == "Hindi"

    def test_hinglish_banao(self):
        result = detect_language("flask app banao")
        assert result["language"] == "hinglish"
        assert "banao" in result["detected_keywords"]

    def test_hinglish_karo(self):
        result = detect_language("deploy karo")
        assert result["language"] == "hinglish"

    def test_hinglish_hatao(self):
        result = detect_language("server hatao")
        assert result["language"] == "hinglish"

    def test_tamil_script(self):
        result = detect_language("வணக்கம்")
        assert result["language"] == "ta"
        assert result["confidence"] >= 0.9

    def test_kannada_script(self):
        result = detect_language("ನಮಸ್ಕಾರ")
        assert result["language"] == "kn"
        assert result["confidence"] >= 0.9

    def test_empty_string(self):
        result = detect_language("")
        assert result["language"] == "en"

    def test_whitespace_only(self):
        result = detect_language("   ")
        assert result["language"] == "en"

    def test_english_deploy_command(self):
        result = detect_language("create a new EC2 instance in Mumbai region")
        assert result["language"] in ("en", "hinglish")

    def test_mixed_hinglish_commands(self):
        result = detect_language("mera purana server hatao")
        assert result["language"] == "hinglish"

    def test_confidence_score_range(self):
        result = detect_language("hello world")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_result_has_required_keys(self):
        result = detect_language("deploy app")
        assert "language" in result
        assert "language_name" in result
        assert "confidence" in result
        assert "detected_keywords" in result


class TestHinglishKeywords:
    def test_keywords_are_lowercase(self):
        for keyword in HINGLISH_KEYWORDS:
            assert keyword == keyword.lower(), f"Keyword should be lowercase: {keyword}"

    def test_known_keywords_exist(self):
        expected = ["banao", "karo", "hatao", "dikhao", "chalao"]
        for kw in expected:
            assert kw in HINGLISH_KEYWORDS, f"Expected keyword missing: {kw}"

    def test_keywords_have_string_values(self):
        for k, v in HINGLISH_KEYWORDS.items():
            assert isinstance(v, str), f"Value should be string for key: {k}"


class TestGetHinglishAction:
    def test_banao_maps_to_create(self):
        action = get_hinglish_action("server banao")
        assert action == "create"

    def test_hatao_maps_to_delete(self):
        action = get_hinglish_action("server hatao")
        assert action == "delete"

    def test_dikhao_maps_to_show(self):
        action = get_hinglish_action("list dikhao")
        assert action == "show"

    def test_deploy_keyword(self):
        action = get_hinglish_action("app deploy karo")
        assert action == "deploy"

    def test_default_action(self):
        action = get_hinglish_action("something without a keyword")
        assert action == "deploy"  # default

    def test_chalao_maps_to_run(self):
        action = get_hinglish_action("script chalao")
        assert action == "run"
