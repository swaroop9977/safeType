from services.pii_regex import PIIRegexDetector


def test_obfuscated_email_not_detected():
    detector = PIIRegexDetector()
    text = "Contact me at user [at] example [dot] com for details."
    detections = detector.detect_pii(text)
    assert not any(d["type"] == "email" for d in detections)


def test_sequential_phone_not_detected():
    detector = PIIRegexDetector()
    text = "Call me at 1234567890 tomorrow."
    detections = detector.detect_pii(text)
    assert not any(d["type"] == "phone" for d in detections)


def test_invalid_credit_card_not_detected():
    detector = PIIRegexDetector()
    text = "Card: 1111-1111-1111-1111"
    detections = detector.detect_pii(text)
    assert not any(d["type"] == "credit_card" for d in detections)


def test_valid_email_detected():
    detector = PIIRegexDetector()
    text = "Reach me at user@example.com for details."
    detections = detector.detect_pii(text)
    assert any(d["type"] == "email" for d in detections)
