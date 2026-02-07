"""
Language detection utility for SafeType+.
Provides a lightweight way to pick language-aware models.
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

class LanguageDetector:
    """
    Detect language for input text with a safe fallback.
    """

    def __init__(
        self,
        default_language: str = "en",
        min_chars: int = 20,
        min_alpha_ratio: float = 0.2
    ):
        self.default_language = default_language
        self.min_chars = min_chars
        self.min_alpha_ratio = min_alpha_ratio

    def detect_language(self, text: str) -> Dict:
        """
        Detect language of the text.

        Returns:
            {
                "language": "en",
                "confidence": 0.0-1.0,
                "reliable": bool,
                "reason": str
            }
        """
        cleaned = (text or "").strip()

        if not cleaned:
            return self._fallback("empty_text")

        if len(cleaned) < self.min_chars:
            return self._fallback("text_too_short")

        alpha_chars = sum(1 for c in cleaned if c.isalpha())
        alpha_ratio = alpha_chars / max(1, len(cleaned))
        if alpha_ratio < self.min_alpha_ratio:
            return self._fallback("low_alpha_ratio")

        try:
            from langdetect import detect_langs, DetectorFactory
            DetectorFactory.seed = 0
            langs = detect_langs(cleaned)
            if not langs:
                return self._fallback("no_language_detected")

            top = langs[0]
            lang = (top.lang or self.default_language).lower()
            confidence = float(top.prob)
            reliable = confidence >= 0.6

            return {
                "language": lang,
                "confidence": round(confidence, 3),
                "reliable": reliable,
                "reason": "detected"
            }

        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return self._fallback("detection_error")

    def _fallback(self, reason: str) -> Dict:
        return {
            "language": self.default_language,
            "confidence": 0.0,
            "reliable": False,
            "reason": reason
        }
