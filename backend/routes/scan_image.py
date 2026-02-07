"""
Image scanning API route for SafeType+.
Extracts text via OCR and analyzes for PII and phishing patterns.
"""

from flask import Blueprint, request, jsonify
import logging
from services.ocr_service import OCRService
from services.pii_regex import PIIRegexDetector
from services.pii_ner import PIINERDetector
from services.nlp_intent import NLPIntentClassifier
from services.language_detection import LanguageDetector
from services.risk_engine import RiskEngine
from services.suggestion_engine import SuggestionEngine
from utils.highlighter import TextHighlighter
from config import Config

logger = logging.getLogger(__name__)

# Create Blueprint
image_bp = Blueprint('image_scan', __name__)

# Initialize services
ocr_service = OCRService(Config.TESSERACT_PATH)
pii_regex = PIIRegexDetector()
pii_ner = PIINERDetector(
    Config.SPACY_MODEL,
    Config.MULTILINGUAL_SPACY_MODEL
)
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

@image_bp.route('/image', methods=['POST'])
def scan_image():
    """
    Scan image for text content, then analyze for PII and phishing.
    
    Request:
    - Content-Type: multipart/form-data
    - Field: image (file)
    - Optional field: preprocess (boolean, default true)
    
    Response JSON:
    {
        "risk_score": float,
        "risk_level": str,
        "module_breakdown": dict,
        "reasons": list,
        "ocr_data": {
            "extracted_text": str,
            "confidence": float,
            "metadata": dict
        },
        "detected_pii": list,
        "intent_analysis": dict,
        "safer_suggestions": list (optional),
        "metadata": dict
    }
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        # Check file extension
        allowed_extensions = Config.ALLOWED_EXTENSIONS
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                "error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            }), 400
        
        # Read image data
        image_data = file.read()
        
        # Validate image
        is_valid, error_msg = ocr_service.validate_image(image_data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        logger.info(f"Processing image: {file.filename} ({len(image_data)} bytes)")
        
        # Get preprocessing option
        preprocess = request.form.get('preprocess', 'true').lower() == 'true'
        
        # Step 1: OCR - Extract text from image
        ocr_result = ocr_service.extract_text_from_image(image_data, preprocess)
        extracted_text = ocr_result['text']
        ocr_confidence = ocr_result['confidence']
        
        logger.info(
            f"OCR extracted {len(extracted_text)} characters "
            f"(confidence: {ocr_confidence:.1f}%)"
        )
        
        # If no text extracted, return early
        if not extracted_text.strip():
            return jsonify({
                "risk_score": 0.0,
                "risk_level": "Low",
                "module_breakdown": {"pii": 0.0, "nlp": 0.0, "ocr": 0.0},
                "reasons": ["No text detected in image"],
                "ocr_data": {
                    "extracted_text": "",
                    "confidence": ocr_confidence,
                    "metadata": ocr_result['metadata']
                },
                "detected_pii": [],
                "metadata": {
                    "image_size": len(image_data),
                    "image_type": ocr_service.detect_image_type(image_data),
                    "processing_timestamp": _get_timestamp()
                }
            }), 200
        
        # Step 2: Language Detection
        language_info = {
            "language": Config.DEFAULT_LANGUAGE,
            "confidence": 0.0,
            "reliable": False,
            "reason": "disabled"
        }
        if Config.ENABLE_LANGUAGE_DETECTION:
            language_info = language_detector.detect_language(extracted_text)
        detected_language = language_info["language"]

        # Step 3: PII Detection on extracted text
        regex_detections = pii_regex.detect_pii(extracted_text)
        ner_detections = pii_ner.detect_entities(extracted_text, detected_language)
        all_pii = pii_ner.combine_with_regex(regex_detections, ner_detections)
        
        logger.debug(f"Detected {len(all_pii)} PII items in image text")
        
        # Step 4: NLP Intent Classification
        intent_probs = nlp_intent.classify_intent(extracted_text, detected_language)
        phishing_keywords = nlp_intent.detect_phishing_keywords(
            extracted_text,
            detected_language
        )
        
        # Step 5: Compute Risk Score (with OCR component)
        ocr_data_for_risk = {
            'confidence': ocr_confidence,
            'pii_count': len(all_pii),
            'text': extracted_text
        }
        
        risk_assessment = risk_engine.compute_risk(
            pii_detections=all_pii,
            intent_probabilities=intent_probs,
            text_length=len(extracted_text),
            ocr_data=ocr_data_for_risk
        )
        
        # Step 6: Generate Highlights for extracted text
        all_detections = all_pii + phishing_keywords
        highlights = highlighter.highlight_text(extracted_text, all_detections)
        highlighted_text = highlighter.create_marked_text(extracted_text, highlights)
        
        # Step 7: Generate Suggestions
        suggestions = []
        if risk_assessment['risk_level'] in ['Medium', 'High']:
            suggestions = suggestion_engine.generate_suggestions(
                text=extracted_text,
                pii_detections=all_pii,
                risk_level=risk_assessment['risk_level'],
                reasons=risk_assessment['reasons']
            )
        
        # Step 8: Build response
        response = {
            "risk_score": risk_assessment['risk_score'],
            "risk_level": risk_assessment['risk_level'],
            "confidence_interval": risk_assessment['confidence_interval'],
            "module_breakdown": risk_assessment['module_breakdown'],
            "reasons": risk_assessment['reasons'],
            "ocr_data": {
                "extracted_text": extracted_text,
                "confidence": ocr_confidence,
                "metadata": ocr_result['metadata'],
                "highlighted_text": highlighted_text
            },
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
                    extracted_text,
                    detected_language
                )
            },
            "highlights": highlights,
            "detection_summary": risk_assessment['detection_summary'],
            "metadata": {
                "image_size": len(image_data),
                "image_type": ocr_service.detect_image_type(image_data),
                "extracted_text_length": len(extracted_text),
                "total_detections": len(all_detections),
                "language": language_info,
                "processing_timestamp": _get_timestamp()
            }
        }
        
        # Add suggestions if generated
        if suggestions:
            response['safer_suggestions'] = suggestions
        
        logger.info(
            f"Image scan complete: risk={risk_assessment['risk_level']}, "
            f"score={risk_assessment['risk_score']:.3f}"
        )
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error scanning image: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error during image analysis",
            "details": str(e) if Config.DEBUG else None
        }), 500

def _get_timestamp():
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.utcnow().isoformat() + 'Z'
