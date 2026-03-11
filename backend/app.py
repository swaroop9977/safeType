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
    return jsonify({
        "status": "operational",
        "modules": {
            "pii_detection": "ready",
            "ner": "ready",
            "nlp_intent": "ready",
            "ocr": "ready",
            "risk_engine": "ready",
            "suggestion_engine": "ready"
        }
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
