"""
Rule-based document detection heuristics for OCR image scans.
Currently focuses on identifying Aadhaar cards from OCR text and layout cues.
"""

from typing import Dict, Optional
import io
import re


class DocumentHeuristicsDetector:
    """Detect probable identity document types from OCR text and image layout."""

    def assess_document(self, image_data: bytes, extracted_text: str) -> Dict:
        """Return document detection assessment with confidence and supporting signals."""
        text = extracted_text or ""
        normalized = self._normalize_text(text)

        aadhaar_number = self._extract_aadhaar_number(text)
        enrolment_number = self._extract_enrolment_number(normalized)
        has_kannada_script = bool(re.search(r"[\u0C80-\u0CFF]", text))

        keyword_score = 0.0
        signals = []

        keyword_patterns = {
            "aadhaar_keyword": r"\baadhaar\b|\badhar\b|\buidai\b",
            "govt_of_india": r"government\s+of\s+india|bharat\s+sarkar",
            "unique_id_authority": r"unique\s+identification\s+authority",
            "enrolment_label": r"enrol(l)?ment\s*no",
            "dob_gender_terms": r"\bdob\b|\byear\s+of\s+birth\b|\bgender\b|\bmale\b|\bfemale\b"
        }

        for signal_name, pattern in keyword_patterns.items():
            if re.search(pattern, normalized):
                keyword_score += 0.12
                signals.append(signal_name)

        if aadhaar_number:
            keyword_score += 0.30
            signals.append("aadhaar_number_pattern")

        if enrolment_number:
            keyword_score += 0.12
            signals.append("enrolment_number_pattern")

        if has_kannada_script:
            keyword_score += 0.05
            signals.append("kannada_script_detected")

        layout = self._layout_signals(image_data)
        if layout["qr_like_region"]:
            keyword_score += 0.10
            signals.append("qr_like_region")
        if layout["portrait_document_ratio"]:
            keyword_score += 0.05
            signals.append("portrait_document_ratio")

        confidence = min(1.0, keyword_score)
        is_aadhaar = confidence >= 0.55

        return {
            "document_type": "aadhaar" if is_aadhaar else "unknown",
            "confidence": round(confidence, 3),
            "signals": signals,
            "fields": {
                "aadhaar_number": aadhaar_number,
                "enrolment_number": enrolment_number,
                "has_kannada_script": has_kannada_script
            },
            "layout": layout
        }

    def _normalize_text(self, text: str) -> str:
        lowered = text.lower()
        return re.sub(r"\s+", " ", lowered)

    def _extract_aadhaar_number(self, text: str) -> Optional[str]:
        for match in re.finditer(r"\b([2-9]\d{3})[-\s]?(\d{4})[-\s]?(\d{4})\b", text):
            groups = match.groups()
            candidate = "".join(groups)
            if len(set(candidate)) <= 2:
                continue
            return f"{groups[0]} {groups[1]} {groups[2]}"
        return None

    def _extract_enrolment_number(self, normalized_text: str) -> Optional[str]:
        match = re.search(r"enrol(l)?ment\s*no\s*[:\-]?\s*(\d{4}/\d{5}/\d{5})", normalized_text)
        if match:
            return match.group(2)
        return None

    def _layout_signals(self, image_data: bytes) -> Dict:
        """Detect rough layout cues that are common in Aadhaar scans."""
        try:
            from PIL import Image

            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            width, height = image.size
            portrait_ratio = (width / max(1, height)) < 0.85

            # Simple QR-like heuristic: look for a high-contrast square patch
            # in the lower part of the document where Aadhaar QR often appears.
            gray = image.convert("L")
            min_side = min(width, height)
            patch = max(40, int(min_side * 0.20))
            step_x = max(20, patch // 2)
            step_y = max(20, patch // 2)
            qr_like = False

            y_start = int(height * 0.30)
            y_end = max(y_start + 1, height - patch)
            x_end = max(1, width - patch)

            for y in range(y_start, y_end + 1, step_y):
                for x in range(0, x_end + 1, step_x):
                    tile = gray.crop((x, y, x + patch, y + patch))
                    pixels = list(tile.getdata())
                    if not pixels:
                        continue

                    total = len(pixels)
                    dark = sum(1 for p in pixels if p < 80) / total
                    bright = sum(1 for p in pixels if p > 200) / total
                    mid = 1.0 - dark - bright

                    # QR-like patches tend to have strong black/white mix.
                    if 0.20 <= dark <= 0.75 and bright >= 0.20 and mid <= 0.55:
                        qr_like = True
                        break
                if qr_like:
                    break

            return {
                "portrait_document_ratio": portrait_ratio,
                "qr_like_region": qr_like
            }

        except Exception:
            return {
                "portrait_document_ratio": False,
                "qr_like_region": False
            }
