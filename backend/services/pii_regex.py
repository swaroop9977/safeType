"""
Regex-based PII detection service.
Identifies common patterns for emails, phones, cards, and identity documents.
"""

import re
from typing import List, Dict, Tuple

class PIIRegexDetector:
    """
    Pattern-based PII detector using regular expressions.
    Optimized for common Indian and international PII formats.
    """
    
    def __init__(self):
        """Initialize regex patterns for various PII types."""
        
        # Email pattern (RFC 5322 simplified)
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone patterns (international and Indian)
        # Matches: +91-9876543210, 9876543210, (987) 654-3210, etc.
        self.phone_pattern = re.compile(
            r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|'
            r'\b\d{10}\b|'
            r'\+\d{1,3}\s?\d{6,14}\b'
        )
        
        # Credit card pattern (basic Luhn algorithm check can be added)
        # Matches: 4111-1111-1111-1111, 4111 1111 1111 1111, 4111111111111111
        self.credit_card_pattern = re.compile(
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        )
        
        # SSN pattern (US Social Security Number)
        # Matches: 123-45-6789, 123456789
        self.ssn_pattern = re.compile(
            r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'
        )
        
        # Aadhaar pattern (Indian UID)
        # Matches: 1234-5678-9012, 1234 5678 9012, 123456789012
        self.aadhaar_pattern = re.compile(
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b(?![-\s]?\d{4})'
        )
        
        # IP Address pattern
        self.ip_pattern = re.compile(
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        )
        
        # Date of birth patterns
        # Matches: 01/01/1990, 1990-01-01, Jan 1, 1990
        self.dob_pattern = re.compile(
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|'
            r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b|'
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',
            re.IGNORECASE
        )
        
        # Passport number patterns
        # Supports broad international formats plus India-specific format.
        self.passport_pattern = re.compile(
            r'\b[A-Z]{1,2}\d{6,9}\b',
            re.IGNORECASE
        )

        # India passport format: one letter followed by 7 digits (e.g. M1234567)
        self.india_passport_pattern = re.compile(
            r'\b[A-PR-WYa-pr-wy][1-9]\d{6}\b'
        )
        
        # Driver's License patterns
        # Includes common formats and India format (SS-RR-NNNNNNNNNNN).
        self.drivers_license_pattern = re.compile(
            r'\b[A-Z]\d{7,8}\b|'                    # Format: A1234567
            r'\b[A-Z]{1,2}\d{5,7}\b|'              # Format: AB12345
            r'\b[A-Z]\d{3}-\d{3}-\d{3}-\d{3}\b',   # Format: A123-456-789-012
            re.IGNORECASE
        )

        self.india_drivers_license_pattern = re.compile(
            r'\b[A-Z]{2}[-\s]?\d{2}[-\s]?\d{11}\b',
            re.IGNORECASE
        )
        
        # Medical ID patterns
        # Medicare: 1AB-CD23-EF45, Medicaid varies by state
        # Health Insurance: various formats
        self.medical_id_pattern = re.compile(
            r'\b\d[A-Z]{2}-[A-Z]{2}\d{2}-[A-Z]{2}\d{2}\b|'  # Medicare format
            r'\bMBI[-\s]?\d{11}\b|'                          # Medicare Beneficiary Identifier
            r'\b(?:MEDICAID|MED)[-\s]?\d{9,13}\b|'          # Medicaid
            r'\b[A-Z]{3}\d{9,11}\b',                         # Insurance member ID
            re.IGNORECASE
        )

        # Indian PAN card number
        # Format: 5 uppercase letters + 4 digits + 1 uppercase letter (e.g. PVPPS3836H)
        self.pan_card_pattern = re.compile(
            r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
            re.IGNORECASE
        )

        # Indian Voter ID (EPIC number)
        # Format: 3 uppercase letters + 7 digits (e.g. ABC1234567)
        self.voter_id_pattern = re.compile(
            r'\b[A-Z]{3}[0-9]{7}\b'
        )
    
    def detect_pii(self, text: str) -> List[Dict]:
        """
        Detect all PII in the given text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected PII entities with metadata:
            [{
                "type": str (email, phone, credit_card, etc.),
                "value": str (matched text),
                "start": int (start position),
                "end": int (end position),
                "confidence": float (0-1)
            }]
        """
        detections = []
        
        # Email detection
        detections.extend(self._detect_pattern(
            text, self.email_pattern, "email", confidence=0.95
        ))
        
        # Phone detection
        phone_matches = self._detect_pattern(
            text, self.phone_pattern, "phone", confidence=0.85
        )
        # Filter out common false positives (like dates, generic numbers)
        phone_matches = [
            m for m in phone_matches
            if self._is_valid_phone(m["value"])
        ]
        detections.extend(phone_matches)
        
        # Credit card detection
        cc_matches = self._detect_pattern(
            text, self.credit_card_pattern, "credit_card", confidence=0.9
        )
        # Validate with Luhn algorithm
        cc_matches = [
            m for m in cc_matches
            if self._luhn_check(m["value"])
        ]
        detections.extend(cc_matches)
        
        # SSN detection
        detections.extend(self._detect_pattern(
            text, self.ssn_pattern, "ssn", confidence=0.85
        ))
        
        # Aadhaar detection
        aadhaar_matches = self._detect_pattern(
            text, self.aadhaar_pattern, "aadhaar", confidence=0.85
        )
        aadhaar_matches = [
            m for m in aadhaar_matches
            if self._is_valid_aadhaar(m["value"])
        ]
        detections.extend(aadhaar_matches)
        
        # IP address detection
        detections.extend(self._detect_pattern(
            text, self.ip_pattern, "ip_address", confidence=0.7
        ))
        
        # Date of birth detection
        detections.extend(self._detect_pattern(
            text, self.dob_pattern, "date_of_birth", confidence=0.6
        ))
        
        # Passport detection
        passport_matches = self._detect_pattern(
            text, self.passport_pattern, "passport", confidence=0.8
        )
        passport_matches.extend(self._detect_pattern(
            text, self.india_passport_pattern, "passport", confidence=0.9
        ))
        # Filter to avoid false positives with phone numbers
        passport_matches = [
            m for m in passport_matches
            if self._is_valid_passport(m["value"])
        ]
        detections.extend(passport_matches)
        
        # Driver's License detection
        dl_matches = self._detect_pattern(
            text, self.drivers_license_pattern, "drivers_license", confidence=0.75
        )
        dl_matches.extend(self._detect_pattern(
            text, self.india_drivers_license_pattern, "drivers_license", confidence=0.9
        ))
        dl_matches = [
            m for m in dl_matches
            if self._is_valid_drivers_license(m["value"])
        ]
        detections.extend(dl_matches)
        
        # Medical ID detection
        detections.extend(self._detect_pattern(
            text, self.medical_id_pattern, "medical_id", confidence=0.85
        ))

        # Indian PAN Card detection
        pan_matches = self._detect_pattern(
            text, self.pan_card_pattern, "pan_card", confidence=0.97
        )
        pan_matches = [m for m in pan_matches if self._is_valid_pan(m["value"])]
        detections.extend(pan_matches)

        # Indian Voter ID detection
        voter_matches = self._detect_pattern(
            text, self.voter_id_pattern, "voter_id", confidence=0.80
        )
        voter_matches = [m for m in voter_matches if self._is_valid_voter_id(m["value"])]
        detections.extend(voter_matches)

        return self._dedupe_detections(detections)
    
    def _detect_pattern(
        self,
        text: str,
        pattern: re.Pattern,
        pii_type: str,
        confidence: float
    ) -> List[Dict]:
        """
        Detect matches for a specific pattern.
        
        Args:
            text: Input text
            pattern: Compiled regex pattern
            pii_type: Type of PII
            confidence: Base confidence score
            
        Returns:
            List of detection dictionaries
        """
        detections = []
        
        for match in pattern.finditer(text):
            detections.append({
                "type": pii_type,
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": confidence
            })
        
        return detections
    
    def _is_valid_phone(self, phone: str) -> bool:
        """
        Validate phone number to reduce false positives.
        
        Args:
            phone: Detected phone string
            
        Returns:
            True if likely a valid phone number
        """
        # Remove non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Must have 10-15 digits
        if len(digits) < 10 or len(digits) > 15:
            return False
        
        # Reject if all digits are the same (e.g., 0000000000)
        if len(set(digits)) == 1:
            return False
        
        # Reject sequential patterns (e.g., 1234567890)
        if self._is_sequential(digits):
            return False
        
        return True
    
    def _is_sequential(self, digits: str) -> bool:
        """Check if digits form a sequential pattern."""
        if len(digits) < 4:
            return False
        
        # Check ascending sequence
        ascending = all(
            int(digits[i]) == int(digits[i-1]) + 1
            for i in range(1, min(len(digits), 8))
        )
        
        # Check descending sequence
        descending = all(
            int(digits[i]) == int(digits[i-1]) - 1
            for i in range(1, min(len(digits), 8))
        )
        
        return ascending or descending
    
    def _is_valid_passport(self, passport: str) -> bool:
        """
        Validate passport number to reduce false positives.
        
        Args:
            passport: Detected passport string
            
        Returns:
            True if likely a valid passport number
        """
        # Remove non-alphanumeric characters
        clean = re.sub(r'[^A-Z0-9]', '', passport.upper())
        
        # Length should be 6-9 characters
        if len(clean) < 6 or len(clean) > 9:
            return False
        
        # Should have at least one letter and one number
        has_letter = any(c.isalpha() for c in clean)
        has_number = any(c.isdigit() for c in clean)
        
        if not (has_letter and has_number):
            return False
        
        return True

    def _is_valid_aadhaar(self, aadhaar: str) -> bool:
        """Validate Aadhaar-like values to reduce false positives."""
        digits = re.sub(r'\D', '', aadhaar)
        if not re.fullmatch(r'\d{12}', digits):
            return False

        # Aadhaar numbers do not start with 0 or 1.
        if digits[0] in {'0', '1'}:
            return False

        if len(set(digits)) == 1:
            return False

        if self._is_sequential(digits):
            return False

        return True

    def _is_valid_pan(self, pan: str) -> bool:
        """Validate PAN format and basic quality constraints."""
        pan_clean = re.sub(r'[^A-Z0-9]', '', pan.upper())
        if not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', pan_clean):
            return False

        if len(set(pan_clean[:5])) == 1:
            return False

        return True

    def _is_valid_voter_id(self, voter_id: str) -> bool:
        """Validate Indian voter ID (EPIC) style values."""
        voter_clean = re.sub(r'[^A-Z0-9]', '', voter_id.upper())
        if not re.fullmatch(r'[A-Z]{3}\d{7}', voter_clean):
            return False

        if len(set(voter_clean[-7:])) == 1:
            return False

        return True

    def _is_valid_drivers_license(self, license_value: str) -> bool:
        """Validate common driver's license formats and India DL pattern."""
        clean = re.sub(r'[^A-Z0-9]', '', license_value.upper())

        patterns = [
            r'[A-Z]\d{7,8}',
            r'[A-Z]{1,2}\d{5,7}',
            r'[A-Z]\d{12}',
            r'[A-Z]{2}\d{13}'  # India DL format after separator removal
        ]
        return any(re.fullmatch(pattern, clean) for pattern in patterns)

    def _dedupe_detections(self, detections: List[Dict]) -> List[Dict]:
        """Remove duplicate detections that can arise from overlapping patterns."""
        seen = set()
        unique = []

        for detection in detections:
            key = (
                detection.get("type"),
                detection.get("start"),
                detection.get("end"),
                detection.get("value")
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(detection)

        return unique
    
    def _luhn_check(self, card_number: str) -> bool:
        """
        Validate credit card number using Luhn algorithm.
        
        Args:
            card_number: Card number string
            
        Returns:
            True if passes Luhn check
        """
        # Remove spaces and dashes
        digits = re.sub(r'\D', '', card_number)
        
        # Must be 13-19 digits
        if len(digits) < 13 or len(digits) > 19:
            return False
        
        # Luhn algorithm
        def luhn_sum(num_str):
            digits_reversed = [int(d) for d in num_str[::-1]]
            checksum = 0
            
            for i, digit in enumerate(digits_reversed):
                if i % 2 == 1:  # Every second digit
                    doubled = digit * 2
                    checksum += doubled if doubled < 10 else doubled - 9
                else:
                    checksum += digit
            
            return checksum % 10 == 0
        
        return luhn_sum(digits)
    
    def redact_pii(
        self,
        text: str,
        detections: List[Dict],
        redaction_char: str = '*'
    ) -> str:
        """
        Redact PII from text for safer display.
        
        Args:
            text: Original text
            detections: List of PII detections
            redaction_char: Character to use for redaction
            
        Returns:
            Redacted text
        """
        if not detections:
            return text
        
        # Sort detections by start position in reverse
        sorted_detections = sorted(
            detections,
            key=lambda x: x["start"],
            reverse=True
        )
        
        result = text
        
        for detection in sorted_detections:
            start = detection["start"]
            end = detection["end"]
            
            # Partial redaction for emails (keep domain visible)
            if detection["type"] == "email":
                redacted = self._redact_email(detection["value"])
            else:
                # Full redaction
                length = end - start
                redacted = redaction_char * length
            
            result = result[:start] + redacted + result[end:]
        
        return result
    
    def _redact_email(self, email: str) -> str:
        """
        Partially redact email (show domain, hide username).
        
        Args:
            email: Email address
            
        Returns:
            Redacted email like: ***@example.com
        """
        parts = email.split('@')
        if len(parts) == 2:
            return f"***@{parts[1]}"
        return "***"
