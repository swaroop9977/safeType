from utils.highlighter import TextHighlighter


def test_highlighter_empty_detections_returns_text():
    highlighter = TextHighlighter()
    text = "Nothing to highlight here."
    assert highlighter.create_marked_text(text, []) == text


def test_highlighter_overlapping_merge():
    highlighter = TextHighlighter()
    highlights = [
        {
            "start": 5,
            "end": 10,
            "text": "alpha",
            "type": "email",
            "category": "pii",
            "severity": "high"
        },
        {
            "start": 8,
            "end": 14,
            "text": "beta",
            "type": "phone",
            "category": "pii",
            "severity": "high"
        }
    ]
    merged = highlighter.merge_overlapping_highlights(highlights)
    assert len(merged) == 1
    assert merged[0]["start"] == 5
    assert merged[0]["end"] == 14
