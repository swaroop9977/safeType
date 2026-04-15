"""
Configuration module for SafeType+ backend.
Loads environment variables and provides centralized configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Model paths and names
    NLP_MODEL = os.getenv('NLP_MODEL', 'distilbert-base-uncased-finetuned-sst-2-english')
    MULTILINGUAL_NLP_MODEL = os.getenv(
        'MULTILINGUAL_NLP_MODEL',
        'cardiffnlp/twitter-xlm-roberta-base-sentiment'
    )
    SPACY_MODEL = os.getenv('SPACY_MODEL', 'en_core_web_sm')
    MULTILINGUAL_SPACY_MODEL = os.getenv('MULTILINGUAL_SPACY_MODEL', 'xx_ent_wiki_sm')

    # Language detection
    ENABLE_LANGUAGE_DETECTION = os.getenv('ENABLE_LANGUAGE_DETECTION', 'True').lower() == 'true'
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
    MIN_LANGUAGE_DETECT_CHARS = int(os.getenv('MIN_LANGUAGE_DETECT_CHARS', '20'))
    
    # Multilingual support (can be disabled to avoid large model downloads)
    ENABLE_MULTILINGUAL = os.getenv('ENABLE_MULTILINGUAL', 'False').lower() == 'true'
    MULTILINGUAL_NLP_MODEL = os.getenv(
        'MULTILINGUAL_NLP_MODEL',
        'cardiffnlp/twitter-xlm-roberta-base-sentiment'
    ) if ENABLE_MULTILINGUAL else None
    MULTILINGUAL_SPACY_MODEL = os.getenv('MULTILINGUAL_SPACY_MODEL', 'xx_ent_wiki_sm') if ENABLE_MULTILINGUAL else None
    
    # OCR configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', None)
    TESSDATA_PATH = os.getenv(
        'TESSDATA_PATH',
        os.path.join(os.path.dirname(__file__), 'tessdata')
    )
    OCR_LANGUAGE_PRIORITY = [
        lang.strip() for lang in os.getenv('OCR_LANGUAGE_PRIORITY', 'eng+kan,eng').split(',')
        if lang.strip()
    ]
    OCR_DEFAULT_MODE = os.getenv('OCR_DEFAULT_MODE', 'accurate').strip().lower()
    
    # Risk scoring weights and thresholds
    PII_WEIGHT = float(os.getenv('PII_WEIGHT', '0.6'))
    NLP_WEIGHT = float(os.getenv('NLP_WEIGHT', '0.4'))
    LOW_RISK_THRESHOLD = float(os.getenv('LOW_RISK_THRESHOLD', '0.3'))
    HIGH_RISK_THRESHOLD = float(os.getenv('HIGH_RISK_THRESHOLD', '0.6'))
        # CORS allowed origins
    # Comma-separated list.  Defaults to the React dev server.
    # In production set e.g.: CORS_ORIGINS=https://yourapp.com
    CORS_ORIGINS = [
        o.strip() for o in
        os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
        if o.strip()
    ]
    # API key authentication
    # Set API_KEY_ENABLED=True and a strong API_KEY value in production.
    # Defaults to disabled so local dev and the evaluation script keep working.
    API_KEY_ENABLED = os.getenv('API_KEY_ENABLED', 'False').lower() == 'true'
    API_KEY = os.getenv('API_KEY', None)

    # Privacy settings
    ENABLE_LOGGING = os.getenv('ENABLE_LOGGING', 'False').lower() == 'true'
    STORE_DATA = os.getenv('STORE_DATA', 'False').lower() == 'true'
    
    # Rate limiting
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', '100'))
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    
    @staticmethod
    def get_risk_level(score: float) -> str:
        """
        Map risk score to risk level.
        
        Args:
            score: Risk score between 0 and 1
            
        Returns:
            Risk level: "Low", "Medium", or "High"
        """
        if score < Config.LOW_RISK_THRESHOLD:
            return "Low"
        elif score < Config.HIGH_RISK_THRESHOLD:
            return "Medium"
        else:
            return "High"
