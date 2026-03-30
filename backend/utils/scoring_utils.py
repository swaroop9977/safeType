"""
Scoring utilities for SafeType+ risk assessment.
Provides modular scoring functions and aggregation logic.
"""

from typing import Dict, List, Tuple
import math

class ScoringUtils:
    """
    Utility class for computing risk scores from detection results.
    Implements weighted scoring with explainable components.
    """
    
    def __init__(self, pii_weight: float = 0.6, nlp_weight: float = 0.4):
        """
        Initialize scoring utils with configurable weights.
        
        Args:
            pii_weight: Weight for PII detection score (default 0.6)
            nlp_weight: Weight for NLP intent score (default 0.4)
        """
        self.pii_weight = pii_weight
        self.nlp_weight = nlp_weight
        
        # Severity multipliers for different PII types
        self.pii_severity = {
            'credit_card': 1.0,
            'ssn': 1.0,
            'aadhaar': 1.0,
            'pan_card': 1.0,
            'passport': 0.95,
            'voter_id': 0.9,
            'drivers_license': 0.9,
            'medical_id': 0.9,
            'date_of_birth': 0.85,
            'email': 0.7,
            'phone': 0.7,
            'person': 0.5,
            'org': 0.3,
            'gpe': 0.2
        }
    
    def compute_pii_score(
        self,
        pii_detections: List[Dict],
        text_length: int
    ) -> Tuple[float, Dict]:
        """
        Compute PII risk score based on detected entities.
        
        Scoring logic:
        - Each PII type has a base severity score
        - Score increases with number of detections
        - Normalized by text length to avoid penalizing longer texts
        
        Args:
            pii_detections: List of detected PII entities
            text_length: Length of analyzed text
            
        Returns:
            Tuple of (score, breakdown_dict)
            - score: Float between 0 and 1
            - breakdown: Dict with per-type contributions
        """
        if not pii_detections or text_length == 0:
            return 0.0, {}
        
        breakdown = {}
        total_severity = 0.0
        
        # Count detections by type
        type_counts = {}
        for detection in pii_detections:
            dtype = detection.get('type', '').lower()
            type_counts[dtype] = type_counts.get(dtype, 0) + 1
        
        # Calculate weighted score
        for dtype, count in type_counts.items():
            severity = self.pii_severity.get(dtype, 0.5)
            
            # Logarithmic scaling for multiple detections (diminishing returns)
            # Prevents overwhelming scores for repetitive PII
            contribution = severity * (1 + 0.2 * math.log(count + 1))
            total_severity += contribution
            breakdown[dtype] = contribution
        
        # Normalize by text length (per 1000 characters)
        # Longer texts naturally have more detections
        normalization_factor = max(1.0, text_length / 1000)
        normalized_score = total_severity / normalization_factor
        
        # Clamp to [0, 1]
        final_score = min(1.0, normalized_score)
        
        return final_score, breakdown
    
    def compute_nlp_score(
        self,
        intent_probabilities: Dict[str, float]
    ) -> Tuple[float, Dict]:
        """
        Compute NLP-based risk score from intent classification.
        
        Intent classes (expected):
        - benign: 0.0 risk
        - suspicious: 0.5 risk
        - phishing: 0.9 risk
        - social_engineering: 0.85 risk
        
        Args:
            intent_probabilities: Dict mapping intent class to probability
            
        Returns:
            Tuple of (score, breakdown_dict)
        """
        if not intent_probabilities:
            return 0.0, {}
        
        # Risk weights for each intent class
        intent_risk_weights = {
            'benign': 0.0,
            'suspicious': 0.5,
            'phishing': 0.9,
            'social_engineering': 0.85,
            'LABEL_0': 0.0,  # DistilBERT negative sentiment
            'LABEL_1': 0.3,  # DistilBERT positive sentiment (can be manipulative)
            'NEGATIVE': 0.0,
            'POSITIVE': 0.3
        }
        
        breakdown = {}
        weighted_score = 0.0
        
        for intent, probability in intent_probabilities.items():
            risk_weight = intent_risk_weights.get(intent, 0.5)
            contribution = probability * risk_weight
            weighted_score += contribution
            breakdown[intent] = contribution
        
        # Clamp to [0, 1]
        final_score = min(1.0, weighted_score)
        
        return final_score, breakdown
    
    def compute_ocr_score(
        self,
        ocr_confidence: float,
        extracted_pii_count: int
    ) -> Tuple[float, Dict]:
        """
        Compute OCR-based risk score.
        
        Combines OCR confidence with PII found in extracted text.
        Higher confidence + more PII = higher risk.
        
        Args:
            ocr_confidence: OCR confidence score (0-100)
            extracted_pii_count: Number of PII entities in extracted text
            
        Returns:
            Tuple of (score, breakdown_dict)
        """
        if ocr_confidence == 0:
            return 0.0, {"ocr_confidence": 0.0, "pii_in_image": 0.0}
        
        # Normalize confidence to 0-1
        confidence_normalized = ocr_confidence / 100.0
        
        # PII count contribution (logarithmic scaling)
        pii_contribution = min(1.0, 0.3 * math.log(extracted_pii_count + 1))
        
        # Combined score: confidence affects how seriously we take the PII
        combined_score = confidence_normalized * (0.3 + 0.7 * pii_contribution)
        
        breakdown = {
            "ocr_confidence": confidence_normalized,
            "pii_in_image": pii_contribution
        }
        
        return combined_score, breakdown
    
    def compute_final_risk_score(
        self,
        pii_score: float,
        nlp_score: float,
        ocr_score: float = 0.0
    ) -> Tuple[float, Dict]:
        """
        Compute final weighted risk score.
        
        Formula:
        - Without OCR: risk = (pii * pii_weight) + (nlp * nlp_weight)
        - With OCR: risk = ((pii + ocr)/2 * pii_weight) + (nlp * nlp_weight)
        
        Args:
            pii_score: PII detection score
            nlp_score: NLP intent score
            ocr_score: Optional OCR score
            
        Returns:
            Tuple of (final_score, module_breakdown)
        """
        # If OCR is present, blend it with PII score
        if ocr_score > 0:
            combined_pii = (pii_score + ocr_score) / 2
        else:
            combined_pii = pii_score
        
        # Weighted combination
        final_score = (combined_pii * self.pii_weight) + (nlp_score * self.nlp_weight)
        
        # Clamp to [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        breakdown = {
            "pii": pii_score,
            "nlp": nlp_score,
            "ocr": ocr_score,
            "weighted_pii_contribution": combined_pii * self.pii_weight,
            "weighted_nlp_contribution": nlp_score * self.nlp_weight
        }
        
        return final_score, breakdown
    
    def generate_reasons(
        self,
        pii_detections: List[Dict],
        nlp_breakdown: Dict,
        ocr_data: Dict = None
    ) -> List[str]:
        """
        Generate human-readable reasons for the risk score.
        
        Args:
            pii_detections: List of detected PII
            nlp_breakdown: NLP score breakdown
            ocr_data: Optional OCR analysis data
            
        Returns:
            List of reason strings
        """
        reasons = []
        
        # PII-based reasons
        pii_counts = {}
        for detection in pii_detections:
            dtype = detection.get('type', 'unknown')
            pii_counts[dtype] = pii_counts.get(dtype, 0) + 1
        
        for dtype, count in pii_counts.items():
            if count == 1:
                reasons.append(f"{dtype.replace('_', ' ').title()} detected")
            else:
                reasons.append(f"Multiple {dtype.replace('_', ' ')}s detected ({count})")
        
        # NLP-based reasons
        for intent, contribution in nlp_breakdown.items():
            if contribution > 0.3:  # Only report significant contributions
                intent_readable = intent.replace('_', ' ').title()
                reasons.append(f"{intent_readable} language patterns detected")
        
        # OCR-based reasons
        if ocr_data and ocr_data.get('confidence', 0) > 0:
            pii_in_image = ocr_data.get('pii_count', 0)
            if pii_in_image > 0:
                reasons.append(f"PII found in image content ({pii_in_image} items)")
        
        # Default reason if nothing specific found
        if not reasons:
            reasons.append("Content analyzed - no specific risks identified")
        
        return reasons
    
    def calculate_confidence_interval(
        self,
        score: float,
        num_detections: int
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for the risk score.
        More detections = higher confidence.
        
        Args:
            score: Computed risk score
            num_detections: Total number of detections
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        # Base uncertainty decreases with more evidence
        base_uncertainty = 0.2
        uncertainty = base_uncertainty / (1 + 0.1 * num_detections)
        
        lower = max(0.0, score - uncertainty)
        upper = min(1.0, score + uncertainty)
        
        return (lower, upper)
