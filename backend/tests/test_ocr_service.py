from services.ocr_service import OCRService


def test_normalize_ocr_text_compacts_whitespace_and_removes_empty_lines():
    service = OCRService()
    raw = "  Name:  Alice   \n\n  Aadhaar   1234 5678 9012   \n   "

    normalized = service._normalize_ocr_text(raw)

    assert normalized == "Name: Alice\nAadhaar 1234 5678 9012"


def test_ocr_quality_score_prefers_readable_text():
    service = OCRService()

    noisy = service._score_ocr_text("@@@ ### $$$", avg_confidence=10)
    readable = service._score_ocr_text(
        "Government of India Aadhaar 1234 5678 9012",
        avg_confidence=80,
    )

    assert readable > noisy


def test_invalid_ocr_mode_falls_back_to_accurate():
    service = OCRService()

    result = service.extract_text_from_image(b"invalid-bytes", ocr_mode="turbo")

    # Invalid image bytes should fail gracefully and return default structure.
    assert "text" in result
    assert "confidence" in result
    assert "metadata" in result
