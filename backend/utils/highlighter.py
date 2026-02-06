"""
Text highlighting utility for SafeType+.
Identifies and marks risky text spans with contextual information.
"""

from typing import List, Dict, Tuple
import re

class TextHighlighter:
    """
    Highlights risky text spans with metadata for frontend visualization.
    Supports multiple highlight types: PII, phishing keywords, suspicious patterns.
    """
    
    def __init__(self):
        """Initialize highlighter with category mappings."""
        self.highlight_categories = {
            'email': 'pii',
            'phone': 'pii',
            'ssn': 'pii',
            'aadhaar': 'pii',
            'credit_card': 'pii',
            'person': 'ner',
            'org': 'ner',
            'gpe': 'ner',
            'urgency': 'phishing',
            'suspicious': 'phishing'
        }
    
    def highlight_text(
        self,
        text: str,
        detections: List[Dict]
    ) -> List[Dict]:
        """
        Create highlighted spans from detected entities.
        
        Args:
            text: Original text content
            detections: List of detected entities with start, end, type, and value
            
        Returns:
            List of highlight spans with metadata:
            [{
                "start": int,
                "end": int,
                "text": str,
                "type": str,
                "category": str,
                "severity": str
            }]
        """
        highlights = []
        
        for detection in detections:
            highlight = {
                "start": detection.get("start", 0),
                "end": detection.get("end", 0),
                "text": detection.get("value", ""),
                "type": detection.get("type", "unknown"),
                "category": self._get_category(detection.get("type", "")),
                "severity": self._get_severity(detection.get("type", ""))
            }
            highlights.append(highlight)
        
        # Sort by start position for proper rendering
        highlights.sort(key=lambda x: x["start"])
        
        return highlights
    
    def _get_category(self, detection_type: str) -> str:
        """
        Map detection type to category.
        
        Args:
            detection_type: Type of detection (email, phone, etc.)
            
        Returns:
            Category name
        """
        return self.highlight_categories.get(
            detection_type.lower(),
            'other'
        )
    
    def _get_severity(self, detection_type: str) -> str:
        """
        Determine severity level based on detection type.
        
        Args:
            detection_type: Type of detection
            
        Returns:
            Severity level: "critical", "high", "medium", or "low"
        """
        critical_types = ['credit_card', 'ssn', 'aadhaar']
        high_types = ['email', 'phone', 'person']
        medium_types = ['org', 'gpe', 'urgency']
        
        dtype = detection_type.lower()
        
        if dtype in critical_types:
            return 'critical'
        elif dtype in high_types:
            return 'high'
        elif dtype in medium_types:
            return 'medium'
        else:
            return 'low'
    
    def create_marked_text(
        self,
        text: str,
        highlights: List[Dict]
    ) -> str:
        """
        Create a marked version of text with HTML-like tags.
        Useful for display in terminals or simple UIs.
        
        Args:
            text: Original text
            highlights: List of highlight spans
            
        Returns:
            Text with markers like: "My email is <MARK type='email'>user@example.com</MARK>"
        """
        if not highlights:
            return text
        
        # Sort highlights by start position in reverse to avoid offset issues
        sorted_highlights = sorted(highlights, key=lambda x: x["start"], reverse=True)
        
        result = text
        for highlight in sorted_highlights:
            start = highlight["start"]
            end = highlight["end"]
            h_type = highlight["type"]
            h_severity = highlight["severity"]
            
            original = result[start:end]
            marked = f'<MARK type="{h_type}" severity="{h_severity}">{original}</MARK>'
            result = result[:start] + marked + result[end:]
        
        return result
    
    def get_explanation_tokens(
        self,
        text: str,
        highlights: List[Dict]
    ) -> List[str]:
        """
        Extract tokens that influenced risk assessment for explainability.
        
        Args:
            text: Original text
            highlights: List of highlight spans
            
        Returns:
            List of unique tokens that triggered detections
        """
        tokens = set()
        
        for highlight in highlights:
            # Add the detected text
            tokens.add(highlight["text"])
            
            # For phishing keywords, extract individual words
            if highlight["category"] == "phishing":
                words = re.findall(r'\b\w+\b', highlight["text"])
                tokens.update(words)
        
        return sorted(list(tokens))
    
    def merge_overlapping_highlights(
        self,
        highlights: List[Dict]
    ) -> List[Dict]:
        """
        Merge overlapping or adjacent highlights to avoid visual clutter.
        
        Args:
            highlights: List of highlight spans
            
        Returns:
            Merged list with no overlaps
        """
        if not highlights:
            return []
        
        # Sort by start position
        sorted_highlights = sorted(highlights, key=lambda x: x["start"])
        
        merged = [sorted_highlights[0]]
        
        for current in sorted_highlights[1:]:
            last = merged[-1]
            
            # Check for overlap or adjacency
            if current["start"] <= last["end"] + 1:
                # Merge: extend the end and combine metadata
                merged[-1] = {
                    "start": last["start"],
                    "end": max(last["end"], current["end"]),
                    "text": "",  # Will need to recompute from text
                    "type": f"{last['type']},{current['type']}",
                    "category": last["category"],  # Keep first category
                    "severity": max(last["severity"], current["severity"])
                }
            else:
                merged.append(current)
        
        return merged
