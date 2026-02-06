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
    SPACY_MODEL = os.getenv('SPACY_MODEL', 'en_core_web_sm')
    
    # OCR configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', None)
    
    # Risk scoring weights and thresholds
    PII_WEIGHT = float(os.getenv('PII_WEIGHT', '0.6'))
    NLP_WEIGHT = float(os.getenv('NLP_WEIGHT', '0.4'))
    LOW_RISK_THRESHOLD = float(os.getenv('LOW_RISK_THRESHOLD', '0.3'))
    HIGH_RISK_THRESHOLD = float(os.getenv('HIGH_RISK_THRESHOLD', '0.6'))
    
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
