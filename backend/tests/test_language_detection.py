from services.language_detection import LanguageDetector


def test_detect_language_english():
    detector = LanguageDetector(default_language="en", min_chars=20)
    text = (
        "This is an English sentence that should be detected correctly. "
        "Here is another English sentence to increase confidence."
    )
    result = detector.detect_language(text)
    assert result["language"] == "en"
    assert result["reliable"] is True
    assert result["confidence"] >= 0.6


def test_short_text_fallback():
    detector = LanguageDetector(default_language="en", min_chars=20)
    result = detector.detect_language("Hi")
    assert result["language"] == "en"
    assert result["reliable"] is False
    assert result["reason"] == "text_too_short"


def test_empty_text_fallback():
    detector = LanguageDetector(default_language="en", min_chars=20)
    result = detector.detect_language("")
    assert result["language"] == "en"
    assert result["reliable"] is False
    assert result["reason"] == "empty_text"
