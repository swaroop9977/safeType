from services.document_heuristics import DocumentHeuristicsDetector


def test_detects_aadhaar_from_keywords_and_number():
    detector = DocumentHeuristicsDetector()
    text = """
    Government of India
    Unique Identification Authority of India
    Aadhaar
    Name: RAMESH KUMAR
    DOB: 1992
    Male
    2345 6789 1234
    """

    result = detector.assess_document(b"not-an-image", text)

    assert result["document_type"] == "aadhaar"
    assert result["confidence"] >= 0.55
    assert result["fields"]["aadhaar_number"] == "2345 6789 1234"


def test_does_not_flag_generic_text_as_aadhaar():
    detector = DocumentHeuristicsDetector()
    text = "Meeting agenda for quarterly engineering review."

    result = detector.assess_document(b"not-an-image", text)

    assert result["document_type"] == "unknown"
    assert result["confidence"] < 0.55


def test_detects_kannada_signal_with_aadhaar_context():
    detector = DocumentHeuristicsDetector()
    text = "ಆಧಾರ್ Government of India UIDAI 3456 7890 1234"

    result = detector.assess_document(b"not-an-image", text)

    assert result["fields"]["has_kannada_script"] is True
    assert result["document_type"] == "aadhaar"
