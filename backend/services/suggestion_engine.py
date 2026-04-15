"""
Suggestion Engine - Generates safer alternative text for risky content.
Key differentiator for SafeType+.
"""

from typing import List, Dict
import re
import logging

logger = logging.getLogger(__name__)

class SuggestionEngine:
    """
    Generates safer alternatives for text containing PII or risky patterns.
    Uses rule-based rewriting with context awareness.
    """
    
    def __init__(self):
        """Initialize suggestion engine with rewriting rules."""
        
        # Replacement templates for different PII types
        self.redaction_templates = {
            'email': '[Email address removed]',
            'phone': '[Phone number removed]',
            'credit_card': '[Payment details removed]',
            'ssn': '[SSN removed]',
            'aadhaar': '[Aadhaar removed]',
            'pan_card': '[PAN removed]',
            'passport': '[Passport details removed]',
            'voter_id': '[Voter ID removed]',
            'drivers_license': '[Driving license removed]',
            'medical_id': '[Medical ID removed]',
            'person': '[Name removed]',
            'ip_address': '[IP address removed]',
            'date_of_birth': '[Date removed]'
        }
        
        # Contextual suggestion templates
        self.context_suggestions = {
            'contact': "You can contact me privately for details.",
            'payment': "Payment information can be shared through secure channels.",
            'identity': "Identity verification can be done through official channels.",
            'personal': "This information is better shared privately."
        }
    
    def generate_suggestions(
        self,
        text: str,
        pii_detections: List[Dict],
        risk_level: str,
        reasons: List[str]
    ) -> List[Dict]:
        """
        Generate safer alternative text suggestions.
        
        Args:
            text: Original text
            pii_detections: List of detected PII
            risk_level: Computed risk level
            reasons: Risk reasons
            
        Returns:
            List of suggestion dicts:
            [{
                "type": str ("redacted", "rewritten", "guidance"),
                "text": str (suggested alternative),
                "explanation": str,
                "confidence": float
            }]
        """
        suggestions = []
        
        # Only generate for Medium and High risk
        if risk_level not in ["Medium", "High"]:
            return suggestions
        
        # 1. Redacted version (always include for High risk)
        if pii_detections:
            redacted = self._create_redacted_version(text, pii_detections)
            suggestions.append({
                "type": "redacted",
                "text": redacted,
                "explanation": "PII has been redacted for privacy protection.",
                "confidence": 0.95
            })
        
        # 2. Rewritten version (context-aware)
        if len(text) < 500:  # Only for shorter texts
            rewritten = self._create_rewritten_version(
                text,
                pii_detections,
                reasons
            )
            if rewritten and rewritten != text:
                suggestions.append({
                    "type": "rewritten",
                    "text": rewritten,
                    "explanation": "Rephrased to maintain intent while removing PII.",
                    "confidence": 0.75
                })
        
        # 3. Guidance suggestions (actionable alternatives)
        guidance = self._generate_guidance(pii_detections, reasons)
        if guidance:
            suggestions.append({
                "type": "guidance",
                "text": guidance,
                "explanation": "Alternative approach to sharing this information.",
                "confidence": 0.85
            })
        
        # 4. Template-based suggestion for common scenarios
        template_suggestion = self._generate_template_suggestion(
            pii_detections,
            reasons
        )
        if template_suggestion:
            suggestions.append(template_suggestion)
        
        return suggestions
    
    def _create_redacted_version(
        self,
        text: str,
        pii_detections: List[Dict]
    ) -> str:
        """
        Create redacted version of text.
        
        Args:
            text: Original text
            pii_detections: PII detections
            
        Returns:
            Redacted text
        """
        # Sort detections by start position (reverse to avoid offset issues)
        sorted_detections = sorted(
            pii_detections,
            key=lambda x: x["start"],
            reverse=True
        )
        
        result = text
        
        for detection in sorted_detections:
            start = detection["start"]
            end = detection["end"]
            dtype = detection["type"]
            
            # Get appropriate replacement
            replacement = self.redaction_templates.get(
                dtype,
                "[Information removed]"
            )
            
            result = result[:start] + replacement + result[end:]
        
        return result
    
    def _create_rewritten_version(
        self,
        text: str,
        pii_detections: List[Dict],
        reasons: List[str]
    ) -> str:
        """
        Create context-aware rewritten version.
        
        Args:
            text: Original text
            pii_detections: PII detections
            reasons: Risk reasons
            
        Returns:
            Rewritten text
        """
        # Detect context/intent
        text_lower = text.lower()
        
        # Contact information sharing
        if any(dtype['type'] in ['email', 'phone'] for dtype in pii_detections):
            if any(word in text_lower for word in ['contact', 'reach', 'call', 'email']):
                return self.context_suggestions['contact']
        
        # Payment information
        if any(dtype['type'] in ['credit_card', 'financial'] for dtype in pii_detections):
            return self.context_suggestions['payment']
        
        # Identity information
        if any(dtype['type'] in ['ssn', 'aadhaar', 'pan_card', 'passport', 'voter_id', 'drivers_license', 'medical_id', 'date_of_birth'] for dtype in pii_detections):
            return self.context_suggestions['identity']
        
        # Personal information
        if any(dtype['type'] == 'person' for dtype in pii_detections):
            return self.context_suggestions['personal']
        
        # Fallback: redacted version
        return self._create_redacted_version(text, pii_detections)
    
    def _generate_guidance(
        self,
        pii_detections: List[Dict],
        reasons: List[str]
    ) -> str:
        """
        Generate guidance text for safer alternatives.
        
        Args:
            pii_detections: PII detections
            reasons: Risk reasons
            
        Returns:
            Guidance string
        """
        guidance_parts = []
        
        # Detect what types of PII are present
        pii_types = set(d['type'] for d in pii_detections)
        
        if 'email' in pii_types or 'phone' in pii_types:
            guidance_parts.append(
                "Consider sharing contact details through direct messages or private channels"
            )
        
        if any(t in pii_types for t in ['credit_card', 'ssn', 'aadhaar', 'pan_card', 'passport', 'voter_id', 'drivers_license', 'medical_id']):
            guidance_parts.append(
                "Never share sensitive identity or payment information in public messages"
            )
        
        if 'person' in pii_types:
            guidance_parts.append(
                "Use initials or general references instead of full names when possible"
            )
        
        # Check for phishing indicators
        if any('phishing' in r.lower() for r in reasons):
            guidance_parts.append(
                "This message shows signs of phishing. Verify sender identity before responding"
            )
        
        if guidance_parts:
            return ". ".join(guidance_parts) + "."
        
        return ""
    
    def _generate_template_suggestion(
        self,
        pii_detections: List[Dict],
        reasons: List[str]
    ) -> Dict:
        """
        Generate template-based suggestion for common scenarios.
        
        Args:
            pii_detections: PII detections
            reasons: Risk reasons
            
        Returns:
            Suggestion dict or None
        """
        pii_types = set(d['type'] for d in pii_detections)
        
        # Contact information template
        if 'email' in pii_types and 'phone' in pii_types:
            return {
                "type": "template",
                "text": "For contact information, please visit my profile or send me a direct message.",
                "explanation": "Template for safely indicating contact availability.",
                "confidence": 0.8
            }
        
        # Verification template
        if any(t in pii_types for t in ['ssn', 'aadhaar', 'pan_card', 'passport', 'voter_id', 'drivers_license', 'medical_id', 'credit_card']):
            return {
                "type": "template",
                "text": "Identity verification can be completed through our secure verification system.",
                "explanation": "Template for identity verification scenarios.",
                "confidence": 0.85
            }
        
        return None
    
    def suggest_privacy_level(
        self,
        pii_detections: List[Dict],
        platform_context: str = "public"
    ) -> Dict:
        """
        Suggest appropriate privacy level for the content.
        
        Args:
            pii_detections: PII detections
            platform_context: "public", "private", "direct"
            
        Returns:
            Privacy recommendation dict
        """
        pii_types = set(d['type'] for d in pii_detections)
        
        # Determine required privacy level
        if any(t in pii_types for t in ['credit_card', 'ssn', 'aadhaar', 'pan_card', 'passport', 'voter_id', 'drivers_license', 'medical_id']):
            recommended = "encrypted_direct"
            reason = "Contains highly sensitive identity/payment information"
        elif any(t in pii_types for t in ['email', 'phone', 'person']):
            recommended = "private"
            reason = "Contains personal contact information"
        elif pii_types:
            recommended = "limited"
            reason = "Contains some personal information"
        else:
            recommended = "public"
            reason = "No sensitive information detected"
        
        return {
            "current_context": platform_context,
            "recommended_privacy": recommended,
            "reason": reason,
            "risk_mismatch": (
                platform_context == "public" and
                recommended in ["private", "encrypted_direct"]
            )
        }
    
    def generate_safe_placeholder(self, pii_type: str) -> str:
        """
        Generate context-appropriate placeholder for PII type.
        
        Args:
            pii_type: Type of PII
            
        Returns:
            Safe placeholder string
        """
        placeholders = {
            'email': 'my email address',
            'phone': 'my phone number',
            'credit_card': 'my payment method',
            'ssn': 'my SSN',
            'aadhaar': 'my Aadhaar',
            'pan_card': 'my PAN',
            'passport': 'my passport number',
            'voter_id': 'my voter ID',
            'drivers_license': 'my driving license',
            'medical_id': 'my medical ID',
            'person': 'the individual',
            'org': 'the organization',
            'ip_address': 'the IP address'
        }
        
        return placeholders.get(pii_type, 'this information')
