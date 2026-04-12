"""
Model initialization module for SafeType+ backend.
Handles downloading and caching of AI/ML models on first run.

Author: SafeType+ Team
Date: April 2026
"""

import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelInitializer:
    """Manages initialization and downloading of AI/ML models."""
    
    # Model definitions
    MODELS = {
        'transformers_en': {
            'name': 'distilbert-base-uncased-finetuned-sst-2-english',
            'library': 'transformers',
            'type': 'intent_classifier'
        },
        'transformers_multi': {
            'name': 'cardiffnlp/twitter-xlm-roberta-base-sentiment',
            'library': 'transformers',
            'type': 'intent_classifier_multi'
        },
        'spacy_en': {
            'name': 'en_core_web_sm',
            'library': 'spacy',
            'type': 'ner'
        },
        'spacy_multi': {
            'name': 'xx_ent_wiki_sm',
            'library': 'spacy',
            'type': 'ner_multi'
        }
    }
    
    @staticmethod
    def initialize_all(enable_multilingual: bool = True) -> dict:
        """
        Initialize all AI/ML models.
        
        Args:
            enable_multilingual: Whether to download multilingual models
            
        Returns:
            Dictionary with initialization status for each model
        """
        logger.info("=" * 60)
        logger.info("SafeType+ Model Initialization")
        logger.info("=" * 60)
        
        status = {
            'success': True,
            'models': {},
            'errors': [],
            'warnings': []
        }
        
        # Initialize HuggingFace transformers
        logger.info("\n[1/2] Initializing HuggingFace Transformers...")
        ModelInitializer._init_transformers(status, enable_multilingual)
        
        # Skip spaCy if on incompatible Python version
        import sys
        if sys.version_info.major >= 3 and sys.version_info.minor >= 14:
            logger.warning("\n[2/2] Skipping spaCy NLP (Python 3.14+ incompatible)")
            logger.warning("    Using regex-only PII detection")
            status['warnings'].append("Skipped spaCy (Python 3.14+ incompatible)")
        else:
            # Initialize spaCy NER
            logger.info("\n[2/2] Initializing spaCy NLP...")
            ModelInitializer._init_spacy(status, enable_multilingual)
        
        # Print summary
        logger.info("\n[3/2] Initialization Summary")
        logger.info("-" * 60)
        ModelInitializer._print_summary(status)
        logger.info("=" * 60)
        
        if not status['success'] and len(status['errors']) > 0:
            logger.warning("\n⚠️  Some models failed to initialize. System will use fallback detection.")
        else:
            logger.info("\n✅ Core models ready! System is operational.")
        
        return status
    
    @staticmethod
    def _init_transformers(status: dict, enable_multilingual: bool):
        """Initialize HuggingFace transformer models."""
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            
            # English model
            try:
                model_name = ModelInitializer.MODELS['transformers_en']['name']
                logger.info(f"  • Downloading {model_name}...")
                
                # This triggers the download
                pipeline(
                    "text-classification",
                    model=model_name,
                    device=-1  # CPU
                )
                
                status['models']['transformers_en'] = {
                    'status': 'loaded',
                    'model': model_name
                }
                logger.info(f"    ✓ English transformer model ready")
                
            except Exception as e:
                msg = f"Failed to load English transformer: {e}"
                logger.error(f"    ✗ {msg}")
                status['errors'].append(msg)
                status['models']['transformers_en'] = {'status': 'failed'}
            
            # Multilingual model (optional)
            if enable_multilingual:
                try:
                    model_name = ModelInitializer.MODELS['transformers_multi']['name']
                    logger.info(f"  • Downloading {model_name}...")
                    
                    pipeline(
                        "text-classification",
                        model=model_name,
                        device=-1
                    )
                    
                    status['models']['transformers_multi'] = {
                        'status': 'loaded',
                        'model': model_name
                    }
                    logger.info(f"    ✓ Multilingual transformer model ready")
                    
                except Exception as e:
                    msg = f"Failed to load multilingual transformer: {e}"
                    logger.warning(f"    ⚠ {msg}")
                    status['warnings'].append(msg)
                    status['models']['transformers_multi'] = {'status': 'failed'}
        
        except ImportError as e:
            msg = f"transformers library not installed: {e}"
            logger.error(f"  ✗ {msg}")
            status['errors'].append(msg)
            status['success'] = False
    
    @staticmethod
    def _init_spacy(status: dict, enable_multilingual: bool):
        """Initialize spaCy NER models."""
        try:
            import spacy
            from spacy.cli import download
            
            # English model
            try:
                model_name = ModelInitializer.MODELS['spacy_en']['name']
                logger.info(f"  • Downloading {model_name}...")
                
                try:
                    spacy.load(model_name)
                except OSError:
                    logger.info(f"    Downloading model (first time)...")
                    download(model_name)
                    spacy.load(model_name)
                
                status['models']['spacy_en'] = {
                    'status': 'loaded',
                    'model': model_name
                }
                logger.info(f"    ✓ English spaCy model ready (NER)")
                
            except Exception as e:
                msg = f"Failed to load English spaCy model: {e}"
                logger.error(f"    ✗ {msg}")
                status['errors'].append(msg)
                status['models']['spacy_en'] = {'status': 'failed'}
            
            # Multilingual model (optional)
            if enable_multilingual:
                try:
                    model_name = ModelInitializer.MODELS['spacy_multi']['name']
                    logger.info(f"  • Downloading {model_name}...")
                    
                    try:
                        spacy.load(model_name)
                    except OSError:
                        logger.info(f"    Downloading model (first time)...")
                        download(model_name)
                        spacy.load(model_name)
                    
                    status['models']['spacy_multi'] = {
                        'status': 'loaded',
                        'model': model_name
                    }
                    logger.info(f"    ✓ Multilingual spaCy model ready (NER)")
                    
                except Exception as e:
                    msg = f"Failed to load multilingual spaCy model: {e}"
                    logger.warning(f"    ⚠ {msg}")
                    status['warnings'].append(msg)
                    status['models']['spacy_multi'] = {'status': 'failed'}
        
        except ImportError as e:
            msg = f"spacy library not installed or incompatible: {e}"
            logger.warning(f"  ⚠ {msg}")
            logger.warning("    NER-based entity detection will be disabled")
            status['warnings'].append(msg)
            # Don't mark as fatal error - system will work with regex only
    
    @staticmethod
    def _verify_models(status: dict):
        """Verify that models are available."""
        try:
            from transformers import pipeline
            import spacy
            
            for model_key, model_info in status['models'].items():
                if model_info.get('status') == 'loaded':
                    logger.info(f"  ✓ {model_key}: {model_info['model']}")
                else:
                    logger.warning(f"  ✗ {model_key}: Failed")
        
        except Exception as e:
            logger.warning(f"  Could not verify models: {e}")
    
    @staticmethod
    def _print_summary(status: dict):
        """Print initialization summary."""
        loaded = sum(1 for m in status['models'].values() if m.get('status') == 'loaded')
        total = len(status['models'])
        
        logger.info(f"\nModels loaded: {loaded}/{total}")
        
        if status['errors']:
            logger.error(f"Errors ({len(status['errors'])}): ")
            for err in status['errors']:
                logger.error(f"  - {err}")
        
        if status['warnings']:
            logger.warning(f"Warnings ({len(status['warnings'])}): ")
            for warn in status['warnings']:
                logger.warning(f"  - {warn}")
        
        if status['success']:
            logger.info("\n✅ All models initialized successfully!")
            logger.info("AI detection is FULLY ENABLED")
        else:
            logger.warning("\n⚠️  Some models unavailable - fallback detection active")


def initialize_models_on_startup(app=None):
    """
    Flask app initialization function.
    Call this in your Flask app before running.
    
    Args:
        app: Flask application instance (optional)
    """
    from config import Config
    
    logger.info("Initializing SafeType+ AI models...")
    status = ModelInitializer.initialize_all(
        enable_multilingual=Config.ENABLE_MULTILINGUAL
    )
    
    return status


if __name__ == '__main__':
    # Allow standalone execution for model download
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    enable_multi = '--no-multilingual' not in sys.argv
    status = ModelInitializer.initialize_all(enable_multilingual=enable_multi)
    sys.exit(0 if status['success'] else 1)
