"""
Risk Engine - Computes explainable risk scores from multiple detection modules.
Core scoring logic for SafeType+.
"""

from typing import Dict, List, Tuple
import logging
from utils.scoring_utils import ScoringUtils
from config import Config

logger = logging.getLogger(__name__)

class RiskEngine:
    """
    Aggregates detection results and computes explainable risk scores.
    Provides transparency through module-level breakdowns.
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize risk engine with configuration.
        
        Args:
            config: Configuration object (uses defaults if None)
        """
        self.config = config or Config()
        self.scorer = ScoringUtils(
            pii_weight=self.config.PII_WEIGHT,
            nlp_weight=self.config.NLP_WEIGHT
        )
    
    def compute_risk(
        self,
        pii_detections: List[Dict],
        intent_probabilities: Dict[str, float],
        text_length: int,
        ocr_data: Dict = None
    ) -> Dict:
        """
        Compute comprehensive risk assessment.
        
        Args:
            pii_detections: List of detected PII entities
            intent_probabilities: NLP intent classification results
            text_length: Length of analyzed text
            ocr_data: Optional OCR analysis data
            
        Returns:
            Risk assessment dict:
            {
                "risk_score": float (0-1),
                "risk_level": str ("Low", "Medium", "High"),
                "confidence_interval": (float, float),
                "module_breakdown": {
                    "pii": float,
                    "nlp": float,
                    "ocr": float
                },
                "component_details": {
                    "pii_breakdown": dict,
                    "nlp_breakdown": dict,
                    "ocr_breakdown": dict
                },
                "reasons": list[str],
                "detection_summary": dict
            }
        """
        # Compute individual module scores
        pii_score, pii_breakdown = self.scorer.compute_pii_score(
            pii_detections,
            text_length
        )
        
        nlp_score, nlp_breakdown = self.scorer.compute_nlp_score(
            intent_probabilities
        )
        
        ocr_score, ocr_breakdown = 0.0, {}
        if ocr_data:
            ocr_score, ocr_breakdown = self.scorer.compute_ocr_score(
                ocr_data.get('confidence', 0),
                ocr_data.get('pii_count', 0)
            )
        
        # Compute final weighted score
        final_score, module_breakdown = self.scorer.compute_final_risk_score(
            pii_score,
            nlp_score,
            ocr_score
        )
        
        # Determine risk level
        risk_level = self.config.get_risk_level(final_score)
        
        # Calculate confidence interval
        total_detections = len(pii_detections)
        confidence_interval = self.scorer.calculate_confidence_interval(
            final_score,
            total_detections
        )
        
        # Generate human-readable reasons
        reasons = self.scorer.generate_reasons(
            pii_detections,
            nlp_breakdown,
            ocr_data
        )
        
        # Create detection summary
        detection_summary = self._create_detection_summary(
            pii_detections,
            intent_probabilities,
            ocr_data
        )
        
        return {
            "risk_score": round(final_score, 3),
            "risk_level": risk_level,
            "confidence_interval": {
                "lower": round(confidence_interval[0], 3),
                "upper": round(confidence_interval[1], 3)
            },
            "module_breakdown": {
                "pii": round(pii_score, 3),
                "nlp": round(nlp_score, 3),
                "ocr": round(ocr_score, 3)
            },
            "component_details": {
                "pii_breakdown": pii_breakdown,
                "nlp_breakdown": nlp_breakdown,
                "ocr_breakdown": ocr_breakdown
            },
            "reasons": reasons,
            "detection_summary": detection_summary
        }
    
    def _create_detection_summary(
        self,
        pii_detections: List[Dict],
        intent_probabilities: Dict[str, float],
        ocr_data: Dict = None
    ) -> Dict:
        """
        Create summary of all detections for transparency.
        
        Args:
            pii_detections: PII detections
            intent_probabilities: Intent classification
            ocr_data: OCR data
            
        Returns:
            Summary dict
        """
        # Count PII by type
        pii_counts = {}
        for detection in pii_detections:
            dtype = detection.get('type', 'unknown')
            pii_counts[dtype] = pii_counts.get(dtype, 0) + 1
        
        # Get dominant intent
        dominant_intent = max(
            intent_probabilities.items(),
            key=lambda x: x[1]
        ) if intent_probabilities else ("unknown", 0.0)
        
        summary = {
            "total_pii_detections": len(pii_detections),
            "pii_by_type": pii_counts,
            "dominant_intent": {
                "class": dominant_intent[0],
                "probability": round(dominant_intent[1], 3)
            },
            "has_ocr_data": ocr_data is not None
        }
        
        if ocr_data:
            summary["ocr_confidence"] = ocr_data.get('confidence', 0)
            summary["ocr_text_length"] = len(ocr_data.get('text', ''))
        
        return summary
    
    def assess_urgency_level(
        self,
        risk_level: str,
        reasons: List[str]
    ) -> str:
        """
        Assess urgency of addressing the detected risks.
        
        Args:
            risk_level: Computed risk level
            reasons: List of risk reasons
            
        Returns:
            Urgency level: "immediate", "soon", "consider", "none"
        """
        # Check for critical PII
        critical_keywords = [
            'credit_card',
            'ssn',
            'aadhaar',
            'pan card',
            'passport',
            'voter id',
            'drivers license',
            'medical id',
            'financial'
        ]
        has_critical = any(
            keyword in reason.lower()
            for reason in reasons
            for keyword in critical_keywords
        )
        
        if risk_level == "High":
            return "immediate" if has_critical else "soon"
        elif risk_level == "Medium":
            return "soon" if has_critical else "consider"
        else:
            return "none"
    
    def compare_with_baseline(
        self,
        current_score: float,
        baseline_score: float = 0.2
    ) -> Dict:
        """
        Compare current risk score with baseline.
        
        Args:
            current_score: Current risk score
            baseline_score: Baseline acceptable risk
            
        Returns:
            Comparison analysis
        """
        delta = current_score - baseline_score
        delta_percent = (delta / baseline_score * 100) if baseline_score > 0 else 0
        
        return {
            "current_score": current_score,
            "baseline_score": baseline_score,
            "delta": round(delta, 3),
            "delta_percent": round(delta_percent, 1),
            "exceeds_baseline": current_score > baseline_score
        }
