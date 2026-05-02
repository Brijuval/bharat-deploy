import pytest
from unittest.mock import patch

from src.lang_detector import LanguageDetector


@pytest.fixture
def detector():
    return LanguageDetector()


def test_detect_hinglish(detector):
    result = detector.detect_language("banao ek instance please")
    assert result["is_hinglish"] is True
    assert result["language"] == "hi"


def test_detect_hinglish_karo(detector):
    result = detector.detect_language("deploy karo mera app")
    assert result["is_hinglish"] is True


def test_detect_hinglish_hatao(detector):
    result = detector.detect_language("hatao yeh server")
    assert result["is_hinglish"] is True


def test_detect_hinglish_dikhao(detector):
    result = detector.detect_language("dikhao mujhe resources")
    assert result["is_hinglish"] is True


def test_detect_hindi(detector):
    with patch('src.lang_detector.detect', return_value='hi'):
        result = detector.detect_language("नमस्ते, मुझे एक instance बनाना है")
    assert result["language"] == "hi"
    assert result["confidence"] == 0.95


def test_detect_english(detector):
    with patch('src.lang_detector.detect', return_value='en'):
        result = detector.detect_language("create a new EC2 instance")
    assert result["language"] == "en"
    assert result["is_hinglish"] is False


def test_detect_fallback_on_exception(detector):
    with patch('src.lang_detector.detect', side_effect=Exception("langdetect error")):
        result = detector.detect_language("xyz")
    assert result["language"] == "en"
    assert result["confidence"] == 0.7


def test_hinglish_confidence_is_high(detector):
    result = detector.detect_language("banao ek new instance")
    assert result["confidence"] >= 0.9


def test_returns_dict_with_required_keys(detector):
    with patch('src.lang_detector.detect', return_value='en'):
        result = detector.detect_language("hello")
    assert "language" in result
    assert "confidence" in result
    assert "is_hinglish" in result
