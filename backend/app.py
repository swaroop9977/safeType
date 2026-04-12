"""
SafeType+ Backend API
Main Flask application entry point for privacy and phishing detection system.

Author: SafeType+ Team
Date: January 2026
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging
from routes.scan_text import text_bp
from routes.scan_image import image_bp
from config import Config
from middleware.limiter import limiter
from models_init import initialize_models_on_startup

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})
limiter.init_app(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize AI/ML models on startup
logger.info("Initializing AI models at startup...")
try:
    model_status = initialize_models_on_startup(app)
    if not model_status['success']:
        logger.warning("⚠️  Some AI models failed to load. Using fallback detection methods.")
except Exception as e:
    logger.warning(f"⚠️  Model initialization failed: {e}")
    logger.warning("System will use fallback detection (regex/keywords only)")

# Register blueprints
app.register_blueprint(text_bp, url_prefix='/api/scan')
app.register_blueprint(image_bp, url_prefix='/api/scan')

@app.route('/')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "SafeType+ API",
        "version": "1.0.0"
    }), 200

@app.route('/api/status')
def status():
    """Detailed status endpoint."""
    # Check if AI models are loaded
    ai_status = "operational"
    if not model_status.get('success'):
        ai_status = "degraded (using fallback detection)"
    
    return jsonify({
        "status": "operational",
        "ai_models": ai_status,
        "modules": {
            "pii_detection": "ready",
            "ner": "ready" if model_status['models'].get('spacy_en', {}).get('status') == 'loaded' else "fallback",
            "nlp_intent": "ready" if model_status['models'].get('transformers_en', {}).get('status') == 'loaded' else "fallback",
            "ocr": "ready",
            "risk_engine": "ready",
            "suggestion_engine": "ready"
        },
        "models_loaded": {k: v.get('status') for k, v in model_status['models'].items()}
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit errors."""
    return jsonify({"error": "Rate limit exceeded. Please slow down."}), 429

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting SafeType+ Backend API...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
