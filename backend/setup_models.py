#!/usr/bin/env python3
"""
SafeType+ Model Setup Script
Downloads and caches AI/ML models locally.

Usage:
    python setup_models.py                  # Download all models
    python setup_models.py --no-multilingual  # Download English-only models
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models_init import ModelInitializer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main setup function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Setup and download SafeType+ AI models'
    )
    parser.add_argument(
        '--no-multilingual',
        action='store_true',
        help='Skip downloading multilingual models (English-only)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("SafeType+ AI Model Setup")
    logger.info("=" * 60)
    
    enable_multilingual = not args.no_multilingual
    
    if enable_multilingual:
        logger.info("Configuration: Full setup (English + Multilingual models)")
    else:
        logger.info("Configuration: English-only setup")
    
    logger.info("")
    
    # Run initialization
    status = ModelInitializer.initialize_all(enable_multilingual=enable_multilingual)
    
    # Print final status
    logger.info("")
    logger.info("=" * 60)
    if status['success']:
        logger.info("✅ Setup completed successfully!")
        logger.info("All AI models are ready for use.")
        return 0
    else:
        logger.error("❌ Setup completed with errors!")
        logger.error("Some models may not be available.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
