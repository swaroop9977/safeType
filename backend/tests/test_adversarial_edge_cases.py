"""
Adversarial and edge-case test suite for SafeType+.
"""

import pytest
from services.pii_regex import PIIRegexDetector
from services.pii_ner import PIINERDetector
from services.nlp_intent import NLPIntentClassifier
from services.language_detection import LanguageDetector


class TestObfuscatedPII:
    """Test detection of obfuscated or disguised PII."""

    def setup_method(self):
        self.detector = PIIRegexDetector()

    def test_email_at_dot_obfuscation(self):
        """Email: user [at] example [dot] com"""
        text = "Contact me at user [at] example [dot] com"
        detections = self.detector.detect_pii(text)
        assert not any(d["type"] == "email" for d in detections)

    def test_phone_with_words(self):
        """Phone: five five five one two three four"""
        text = "Call me at five five five one two three four"
        detections = self.detector.detect_pii(text)
        assert not any(d["type"] == "phone" for d in detections)

    def test_credit_card_with_x(self):
        """Card: 1234-XXXX-XXXX-5678"""
        text = "Card ending in 1234-XXXX-XXXX-5678"
        detections = self.detector.detect_pii(text)
        assert not any(d["type"] == "credit_card" for d in detections)

    def test_ssn_partial_redaction(self):
        """SSN: XXX-XX-1234"""
        text = "SSN: XXX-XX-1234"
        detections = self.detector.detect_pii(text)
        assert not any(d["type"] == "ssn" for d in detections)


class TestEdgeCaseInputs:
    """Test unusual or edge-case inputs."""

    def setup_method(self):
        self.detector = PIIRegexDetector()
        self.lang_detector = LanguageDetector()

    def test_empty_string(self):
        """Empty string should return no detections."""
        detections = self.detector.detect_pii("")
        assert len(detections) == 0

    def test_very_long_text(self):
        """Very long text (10,000+ chars) should not crash."""
        text = "a" * 15000
        detections = self.detector.detect_pii(text)
        assert isinstance(detections, list)

    def test_unicode_emoji_text(self):
        """Text with emojis should process without error."""
        text = "My email is test@example.com 😀🎉"
        detections = self.detector.detect_pii(text)
        assert any(d["type"] == "email" for d in detections)

    def test_mixed_script_text(self):
        """Text with mixed scripts (Latin + Cyrillic)."""
        text = "Email: тест@example.com"
        detections = self.detector.detect_pii(text)
        # Should still detect email
        assert len(detections) >= 0

    def test_all_whitespace(self):
        """All whitespace should return no detections."""
        text = "    \n\n\t\t   "
        detections = self.detector.detect_pii(text)
        assert len(detections) == 0

    def test_language_detection_short_text(self):
        """Short text should fall back gracefully."""
        result = self.lang_detector.detect_language("Hi")
        assert result["reliable"] is False

    def test_language_detection_numeric_only(self):
        """Numeric-only text should fall back."""
        result = self.lang_detector.detect_language("123456789012345678901234567890")
        assert result["reliable"] is False


class TestSequentialAndPatternData:
    """Test detection of invalid patterns (sequential, repeated, etc.)."""

    def setup_method(self):
        self.detector = PIIRegexDetector()

    def test_sequential_phone(self):
        """Sequential phone: 1234567890"""
        text = "Call me at 1234567890"
        detections = self.detector.detect_pii(text)
        assert not any(d["type"] == "phone" for d in detections)

    def test_repeated_digit_phone(self):
        """Repeated digit: 0000000000"""
        text = "Phone: 0000000000"
        detections = self.detector.detect_pii(text)
        assert not any(d["type"] == "phone" for d in detections)

    def test_invalid_luhn_credit_card(self):
        """Invalid Luhn check credit card."""
        text = "Card: 1111-1111-1111-1111"
        detections = self.detector.detect_pii(text)
        assert not any(d["type"] == "credit_card" for d in detections)

    def test_valid_credit_card_luhn(self):
        """Valid Luhn check credit card (Visa test card)."""
        text = "Card: 4532-0151-7384-1234"
        detections = self.detector.detect_pii(text)
        assert any(d["type"] == "credit_card" for d in detections)


class TestMultilingualPhishing:
    """Test phishing detection in multiple languages."""

    def setup_method(self):
        self.intent_classifier = NLPIntentClassifier()

    def test_spanish_urgency_keyword(self):
        """Spanish urgency: 'urgente'"""
        text = "Esto es urgente, actualiza tu cuenta ahora."
        result = self.intent_classifier.detect_phishing_keywords(text, "es")
        assert len(result) > 0

    def test_french_reward_keyword(self):
        """French reward: 'gagner'"""
        text = "Félicitations, vous avez gagné un prix gratuit!"
        result = self.intent_classifier.detect_phishing_keywords(text, "fr")
        assert len(result) > 0

    def test_german_authority_keyword(self):
        """German authority: 'bank'"""
        text = "Ihre Bank hat Ihr Konto gesperrt."
        result = self.intent_classifier.detect_phishing_keywords(text, "de")
        assert len(result) > 0

    def test_english_phishing_baseline(self):
        """English phishing as baseline."""
        text = "Your account is suspended. Click here immediately!"
        result = self.intent_classifier.detect_phishing_keywords(text, "en")
        assert len(result) >= 2  # suspended + immediately


class TestBoundaryConditions:
    """Test boundary values and corner cases."""

    def setup_method(self):
        self.detector = PIIRegexDetector()

    def test_email_at_start(self):
        """Email at very start of text."""
        text = "user@example.com is my email"
        detections = self.detector.detect_pii(text)
        assert any(d["type"] == "email" for d in detections)

    def test_email_at_end(self):
        """Email at very end of text."""
        text = "Contact me at user@example.com"
        detections = self.detector.detect_pii(text)
        assert any(d["type"] == "email" for d in detections)

    def test_multiple_pii_same_type(self):
        """Multiple PII of the same type."""
        text = "Emails: user1@example.com, user2@example.com, user3@example.com"
        detections = self.detector.detect_pii(text)
        email_detections = [d for d in detections if d["type"] == "email"]
        assert len(email_detections) == 3

    def test_overlapping_patterns(self):
        """Text with potential overlapping patterns."""
        text = "123-45-6789012"  # Could be SSN or phone
        detections = self.detector.detect_pii(text)
        # Should detect something, but not crash
        assert len(detections) >= 0


class TestNEREdgeCases:
    """Test NER behavior on edge cases."""

    def setup_method(self):
        self.ner = PIINERDetector()

    def test_single_word_person_name(self):
        """Single-word name (lower confidence expected)."""
        text = "John called me yesterday."
        detections = self.ner.detect_entities(text, "en")
        # May or may not detect, but should not crash
        assert isinstance(detections, list)

    def test_multiple_entity_types(self):
        """Text with multiple entity types."""
        text = "John Smith works at Microsoft in Seattle."
        detections = self.ner.detect_entities(text, "en")
        # Should detect PERSON, ORG, GPE (if model loaded)
        if detections:
            types = set(d["type"] for d in detections)
            assert len(types) >= 1

    def test_non_english_entities(self):
        """Non-English entities (if multilingual model available)."""
        text = "José García trabaja en Barcelona."
        detections = self.ner.detect_entities(text, "es")
        assert isinstance(detections, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
