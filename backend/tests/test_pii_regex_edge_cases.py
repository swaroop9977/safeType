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


def test_valid_pan_detected():
    detector = PIIRegexDetector()
    text = "My PAN is PVPPS3836H for tax records."
    detections = detector.detect_pii(text)
    assert any(d["type"] == "pan_card" and d["value"].upper() == "PVPPS3836H" for d in detections)


def test_valid_aadhaar_detected():
    detector = PIIRegexDetector()
    text = "Aadhaar: 2345 7698 1234"
    detections = detector.detect_pii(text)
    assert any(d["type"] == "aadhaar" for d in detections)


def test_invalid_aadhaar_start_not_detected():
    detector = PIIRegexDetector()
    text = "Aadhaar: 1234 5678 9012"
    detections = detector.detect_pii(text)
    assert not any(d["type"] == "aadhaar" for d in detections)


def test_valid_voter_and_india_dl_detected():
    detector = PIIRegexDetector()
    text = "Voter ID ABC1234567 and DL KA01 20231234567"
    detections = detector.detect_pii(text)
    assert any(d["type"] == "voter_id" for d in detections)
    assert any(d["type"] == "drivers_license" for d in detections)


def test_valid_india_passport_detected():
    detector = PIIRegexDetector()
    text = "Passport number: M1234567"
    detections = detector.detect_pii(text)
    assert any(d["type"] == "passport" and d["value"].upper() == "M1234567" for d in detections)
