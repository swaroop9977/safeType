# SafeType+ Multilingual Support & Edge-Case Testing

## Overview

This document describes the newly added multilingual support and adversarial/edge-case testing capabilities in SafeType+.

---

## Multilingual Support

### Features

1. **Language Detection**
   - Automatic language detection using `langdetect` library
   - Configurable minimum character threshold (default: 20 chars)
   - Fallback to default language (English) for short/ambiguous text
   - Stable detection with seeded random generator

2. **Multilingual NLP Intent Classification**
   - English model: `distilbert-base-uncased-finetuned-sst-2-english`
   - Multilingual model: `cardiffnlp/twitter-xlm-roberta-base-sentiment`
   - Language-aware keyword patterns for phishing detection
   - Supported languages: English (en), Spanish (es), French (fr), German (de), Portuguese (pt), Italian (it)

3. **Multilingual Named Entity Recognition (NER)**
   - English model: `en_core_web_sm` (spaCy)
   - Multilingual model: `xx_ent_wiki_sm` (spaCy)
   - Automatic model selection based on detected language

### Configuration

Add to your `.env` file:

```env
# Enable/disable language detection
ENABLE_LANGUAGE_DETECTION=True

# Default language (ISO 639-1 code)
DEFAULT_LANGUAGE=en

# Minimum characters for reliable detection
MIN_LANGUAGE_DETECT_CHARS=20

# Multilingual models (optional)
MULTILINGUAL_NLP_MODEL=cardiffnlp/twitter-xlm-roberta-base-sentiment
MULTILINGUAL_SPACY_MODEL=xx_ent_wiki_sm
```

### Installation

1. Install language detection library:
```bash
pip install langdetect==1.0.9
```

2. Download multilingual spaCy model:
```bash
python -m spacy download xx_ent_wiki_sm
```

3. (Optional) Pre-download multilingual transformer model:
```python
from transformers import pipeline
pipeline("text-classification", model="cardiffnlp/twitter-xlm-roberta-base-sentiment")
```

### Usage

Language detection runs automatically when enabled. The detected language is included in the API response metadata:

```json
{
  "metadata": {
    "language": {
      "language": "es",
      "confidence": 0.95,
      "reliable": true,
      "reason": "detected"
    }
  }
}
```

### Supported Phishing Keywords by Language

| Language | Code | Urgency | Reward | Authority | Action |
|----------|------|---------|--------|-----------|--------|
| English  | en   | urgent, expire, suspended | winner, prize, free | bank, IRS, police | click here, download |
| Spanish  | es   | urgente, expira, suspendido | ganador, premio, gratis | banco, gobierno | haz clic, descarga |
| French   | fr   | urgent, expire, suspendu | gagner, prix, gratuit | banque, police | cliquez ici, téléchargez |
| German   | de   | dringend, ablauf, gesperrt | gewinner, preis, gratis | bank, polizei | hier klicken, herunterladen |
| Portuguese | pt | urgente, expira, suspenso | ganhador, prêmio, grátis | banco, governo | clique aqui, baixar |
| Italian  | it   | urgente, scade, sospeso | vincitore, premio, gratis | banca, polizia | clicca qui, scarica |

---

## Adversarial & Edge-Case Testing

### Test Categories

#### 1. Obfuscated PII
Tests detection of intentionally disguised PII:
- Email: `user [at] example [dot] com`
- Phone: `five five five one two three four`
- Credit card: `1234-XXXX-XXXX-5678`
- SSN: `XXX-XX-1234`

**Expected Behavior**: Should NOT detect obfuscated patterns (designed to bypass automated detection)

#### 2. Edge-Case Inputs
Tests unusual input formats:
- Empty strings
- Very long text (15,000+ characters)
- Unicode emoji text
- Mixed scripts (Latin + Cyrillic)
- All whitespace
- Numeric-only text

**Expected Behavior**: Should handle gracefully without crashes

#### 3. Sequential & Pattern Data
Tests invalid patterns that match regex but fail validation:
- Sequential phone: `1234567890`
- Repeated digits: `0000000000`
- Invalid Luhn credit card: `1111-1111-1111-1111`
- Valid Luhn test card: `4532-0151-7384-1234`

**Expected Behavior**: Should filter out invalid patterns using validation checks (Luhn algorithm, sequential detection, etc.)

#### 4. Multilingual Phishing
Tests phishing keyword detection across languages:
- Spanish: `Esto es urgente, actualiza tu cuenta ahora.`
- French: `Félicitations, vous avez gagné un prix gratuit!`
- German: `Ihre Bank hat Ihr Konto gesperrt.`
- English baseline: `Your account is suspended. Click here immediately!`

**Expected Behavior**: Should detect phishing keywords in all supported languages

#### 5. Boundary Conditions
Tests edge positions and multiple occurrences:
- Email at start of text
- Email at end of text
- Multiple PII of same type
- Overlapping patterns

**Expected Behavior**: Should detect all valid occurrences regardless of position

#### 6. NER Edge Cases
Tests NER behavior on unusual entity patterns:
- Single-word names (lower confidence)
- Multiple entity types in one sentence
- Non-English entities

**Expected Behavior**: Should handle gracefully with or without model loaded

### Running Tests

```bash
# Run all adversarial tests
pytest backend/tests/test_adversarial_edge_cases.py -v

# Run specific test class
pytest backend/tests/test_adversarial_edge_cases.py::TestObfuscatedPII -v

# Run with coverage
pytest backend/tests/test_adversarial_edge_cases.py --cov=services --cov-report=html
```

### Test Results Interpretation

| Result | Meaning |
|--------|---------|
| ✅ PASS | System correctly handled the edge case |
| ❌ FAIL | Unexpected behavior or crash |
| ⚠️ SKIP | Test skipped (e.g., model not available) |

### Adding New Tests

To add new adversarial tests, follow this pattern:

```python
class TestYourCategory:
    """Description of test category."""

    def setup_method(self):
        self.detector = PIIRegexDetector()

    def test_your_edge_case(self):
        """Description of specific test."""
        text = "Your test input"
        detections = self.detector.detect_pii(text)
        assert len(detections) == expected_count
```

---

## Implementation Details

### Language Detection Flow

1. **Input Validation**
   - Check text length (minimum 20 chars by default)
   - Check alpha character ratio (minimum 20%)

2. **Detection**
   - Use `langdetect.detect_langs()` with seeded randomness
   - Return top language with confidence score

3. **Reliability Assessment**
   - Confidence >= 0.6 → reliable
   - Confidence < 0.6 → unreliable, use default

4. **Fallback**
   - Short text → default language
   - Low alpha ratio → default language
   - Detection error → default language

### Model Selection Logic

```python
def _select_nlp(self, language: str = "en"):
    if language.startswith("en"):
        return self.nlp  # English model
    return self.nlp_multi or self.nlp  # Multilingual or fallback
```

### Keyword Pattern Matching

```python
def _get_language_patterns(self, language: str):
    lang = normalize_language(language)  # "en-US" → "en"
    if lang in self.keyword_patterns:
        return self.keyword_patterns[lang]
    return self.keyword_patterns["en"]  # Fallback
```

---

## Performance Considerations

1. **Model Loading**
   - Models are loaded lazily on first use
   - English models loaded by default
   - Multilingual models only if configured

2. **Language Detection Overhead**
   - ~10-50ms for typical text (100-1000 chars)
   - Disable if performance is critical and language is known

3. **Memory Usage**
   - Each transformer model: ~200-500 MB
   - Each spaCy model: ~100-200 MB
   - Consider disabling multilingual models for resource-constrained environments

---

## Known Limitations

1. **Language Detection**
   - Requires minimum 20 characters for reliability
   - Mixed-language text may produce inconsistent results
   - Code-switched text (multiple languages in one sentence) defaults to dominant language

2. **Multilingual NER**
   - `xx_ent_wiki_sm` has lower accuracy than language-specific models
   - Consider downloading language-specific models for production use

3. **Phishing Keywords**
   - Keyword patterns are manually curated
   - May not cover all phishing variations
   - Consider adding domain-specific patterns

4. **Obfuscation**
   - Deliberately obfuscated PII (e.g., `user [at] example [dot] com`) is NOT detected by design
   - Users can bypass detection with creative obfuscation

---

## Future Enhancements

1. **Language-Specific Models**
   - Add support for language-specific spaCy models (e.g., `es_core_news_sm`)

2. **Additional Languages**
   - Add keyword patterns for more languages (Arabic, Chinese, Japanese, etc.)

3. **Advanced Obfuscation Detection**
   - Pattern learning for common obfuscation techniques
   - Context-aware deobfuscation

4. **Model Fine-Tuning**
   - Fine-tune multilingual models on privacy/phishing datasets
   - Improve accuracy for domain-specific text

5. **A/B Testing**
   - Compare accuracy of English vs multilingual models
   - Benchmark performance impact

---

## References

- **langdetect**: https://github.com/Mimino666/langdetect
- **spaCy Multilingual**: https://spacy.io/models/xx
- **Transformers Multilingual**: https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment
- **Luhn Algorithm**: https://en.wikipedia.org/wiki/Luhn_algorithm

---

## Questions?

For issues or suggestions, open an issue in the repository or contact the SafeType+ team.
