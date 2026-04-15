"""
Text scanning API route for SafeType+.
Analyzes text for PII, phishing patterns, and risk assessment.
"""

from flask import Blueprint, request, jsonify
import logging
from services.pii_regex import PIIRegexDetector
from services.pii_ner import PIINERDetector
from services.nlp_intent import NLPIntentClassifier
from services.language_detection import LanguageDetector
from services.risk_engine import RiskEngine
from services.suggestion_engine import SuggestionEngine
from utils.highlighter import TextHighlighter
from middleware.auth import require_api_key
from middleware.limiter import limiter
from config import Config

logger = logging.getLogger(__name__)

# Create Blueprint
text_bp = Blueprint('text_scan', __name__)

# Initialize services (lazy loading handled in classes)
pii_regex = PIIRegexDetector()

# Try to initialize NER, but don't fail if it doesn't work
try:
    pii_ner = PIINERDetector(
        Config.SPACY_MODEL,
        Config.MULTILINGUAL_SPACY_MODEL
    )
except Exception as e:
    logger.warning(f"Could not initialize spaCy NER: {e}. Using regex-only PII detection.")
    pii_ner = None

nlp_intent = NLPIntentClassifier(
    Config.NLP_MODEL,
    Config.MULTILINGUAL_NLP_MODEL
)
language_detector = LanguageDetector(
    default_language=Config.DEFAULT_LANGUAGE,
    min_chars=Config.MIN_LANGUAGE_DETECT_CHARS
)
risk_engine = RiskEngine(Config())
suggestion_engine = SuggestionEngine()
highlighter = TextHighlighter()

@text_bp.route('/text', methods=['POST'])
@require_api_key
@limiter.limit(lambda: f"{Config.RATE_LIMIT} per minute")
def scan_text():
    """
    Scan text for PII, phishing patterns, and compute risk score.
    
    Request JSON:
    {
        "text": str (required),
        "include_suggestions": bool (optional, default True),
        "include_highlights": bool (optional, default True)
    }
    
    Response JSON:
    {
        "risk_score": float,
        "risk_level": str,
        "module_breakdown": dict,
        "reasons": list,
        "detected_pii": list,
        "intent_analysis": dict,
        "highlighted_text": str (optional),
        "highlights": list (optional),
        "safer_suggestions": list (optional),
        "metadata": dict
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        
        # Extract text
        text = data.get('text', '').strip()
        if not text:
            return jsonify({"error": "Text field is required and cannot be empty"}), 400
        
        # Check text length limits
        if len(text) > 10000:
            return jsonify({"error": "Text exceeds maximum length of 10,000 characters"}), 400
        
        # Options
        include_suggestions = data.get('include_suggestions', True)
        include_highlights = data.get('include_highlights', True)
        
        logger.info(f"Scanning text ({len(text)} characters)")
        
        # Step 1: Language Detection
        language_info = {
            "language": Config.DEFAULT_LANGUAGE,
            "confidence": 0.0,
            "reliable": False,
            "reason": "disabled"
        }
        if Config.ENABLE_LANGUAGE_DETECTION:
            language_info = language_detector.detect_language(text)
        detected_language = language_info["language"]

        # Step 2: PII Detection (Regex)
        regex_detections = pii_regex.detect_pii(text)
        logger.debug(f"Regex detected {len(regex_detections)} PII items")
        
        # Step 3: PII Detection (NER) - Optional
        ner_detections = []
        if pii_ner is not None:
            ner_detections = pii_ner.detect_entities(text, detected_language)
            logger.debug(f"NER detected {len(ner_detections)} entities")
        else:
            logger.debug("NER skipped (spaCy not available)")
        
        # Step 4: Combine PII detections
        if pii_ner is not None:
            all_pii = pii_ner.combine_with_regex(regex_detections, ner_detections)
        else:
            all_pii = regex_detections
        logger.debug(f"Combined total: {len(all_pii)} PII items")
        
        # Step 5: NLP Intent Classification
        intent_probs = nlp_intent.classify_intent(text, detected_language)
        logger.debug(f"Intent classification: {intent_probs}")
        
        # Step 6: Detect phishing keywords
        phishing_keywords = nlp_intent.detect_phishing_keywords(text, detected_language)
        
        # Add phishing keywords to detections for highlighting
        all_detections = all_pii + phishing_keywords
        
        # Step 7: Compute Risk Score
        risk_assessment = risk_engine.compute_risk(
            pii_detections=all_pii,
            intent_probabilities=intent_probs,
            text_length=len(text)
        )
        
        # Step 8: Generate Highlights
        highlights = []
        highlighted_text = ""
        if include_highlights:
            highlights = highlighter.highlight_text(text, all_detections)
            highlighted_text = highlighter.create_marked_text(text, highlights)
        
        # Step 9: Generate Suggestions
        suggestions = []
        if include_suggestions and risk_assessment['risk_level'] in ['Medium', 'High']:
            suggestions = suggestion_engine.generate_suggestions(
                text=text,
                pii_detections=all_pii,
                risk_level=risk_assessment['risk_level'],
                reasons=risk_assessment['reasons']
            )
        
        # Step 10: Build response
        response = {
            "risk_score": risk_assessment['risk_score'],
            "risk_level": risk_assessment['risk_level'],
            "confidence_interval": risk_assessment['confidence_interval'],
            "module_breakdown": risk_assessment['module_breakdown'],
            "reasons": risk_assessment['reasons'],
            "detected_pii": [
                {
                    "type": d['type'],
                    "value": d['value'][:50] + "..." if len(d['value']) > 50 else d['value'],
                    "start": d['start'],
                    "end": d['end'],
                    "confidence": d.get('confidence', 0.0)
                }
                for d in all_pii
            ],
            "intent_analysis": {
                "probabilities": intent_probs,
                "manipulation_detected": nlp_intent.analyze_sentiment_manipulation(
                    text,
                    detected_language
                )
            },
            "detection_summary": risk_assessment['detection_summary'],
            "metadata": {
                "text_length": len(text),
                "total_detections": len(all_detections),
                "pii_count": len(all_pii),
                "phishing_keywords_count": len(phishing_keywords),
                "language": language_info,
                "processing_timestamp": _get_timestamp()
            }
        }
        
        # Add optional fields
        if include_highlights:
            response['highlights'] = highlights
            response['highlighted_text'] = highlighted_text
            response['explanation_tokens'] = highlighter.get_explanation_tokens(
                text,
                highlights
            )
        
        if suggestions:
            response['safer_suggestions'] = suggestions
        
        logger.info(
            f"Scan complete: risk={risk_assessment['risk_level']}, "
            f"score={risk_assessment['risk_score']:.3f}"
        )
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error scanning text: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error during text analysis",
            "details": str(e) if Config.DEBUG else None
        }), 500

def _get_timestamp():
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat() + 'Z'
