"""
Named Entity Recognition (NER) based PII detection using spaCy.
Detects person names, organizations, locations, and other entities.
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class PIINERDetector:
    """
    NER-based PII detector using spaCy for entity extraction.
    Complements regex-based detection with ML-powered entity recognition.
    """
    
    def __init__(
        self,
        model_name: str = "en_core_web_sm",
        multilingual_model_name: str = None
    ):
        """
        Initialize spaCy NER model.
        
        Args:
            model_name: spaCy model to use (default: en_core_web_sm)
        """
        self.model_name = model_name
        self.multilingual_model_name = multilingual_model_name
        self.nlp = None
        self.nlp_multi = None
        self._load_models()
    
    def _load_models(self):
        """Load spaCy models lazily."""
        try:
            import spacy
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
        except OSError:
            logger.warning(
                f"spaCy model '{self.model_name}' not found. "
                f"Please run: python -m spacy download {self.model_name}"
            )
            self.nlp = None
        except (TypeError, ValueError) as e:
            # Python 3.14+ compatibility issue with spaCy
            if "REGEX" in str(e) or "unable to infer type" in str(e):
                logger.error(
                    f"spaCy compatibility error (Python 3.14+): {e}\n"
                    "Please use Python 3.11 or 3.12 for full spaCy support.\n"
                    "NER detection will be disabled."
                )
            else:
                logger.error(f"Error loading spaCy model: {e}")
            self.nlp = None
        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
            self.nlp = None

        if not self.multilingual_model_name:
            return

        try:
            import spacy
            self.nlp_multi = spacy.load(self.multilingual_model_name)
            logger.info(f"Loaded spaCy model: {self.multilingual_model_name}")
        except OSError:
            logger.warning(
                f"spaCy model '{self.multilingual_model_name}' not found. "
                f"Please run: python -m spacy download {self.multilingual_model_name}"
            )
            self.nlp_multi = None
        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
            self.nlp_multi = None

    def _select_nlp(self, language: str = "en"):
        if language and language.lower().startswith("en"):
            return self.nlp

        return self.nlp_multi or self.nlp
    
    def detect_entities(self, text: str, language: str = "en") -> List[Dict]:
        """
        Detect named entities in text using spaCy NER.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected entities:
            [{
                "type": str (person, org, gpe, etc.),
                "value": str (entity text),
                "start": int,
                "end": int,
                "confidence": float,
                "label": str (original spaCy label)
            }]
        """
        nlp = self._select_nlp(language)
        if nlp is None:
            logger.warning("spaCy model not available, skipping NER")
            return []
        
        detections = []
        
        try:
            # Process text with spaCy
            doc = nlp(text)
            
            # Extract relevant entities
            for ent in doc.ents:
                entity_type = self._map_entity_type(ent.label_)
                
                # Only include privacy-relevant entities
                if entity_type:
                    detections.append({
                        "type": entity_type,
                        "value": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": self._get_confidence(ent),
                        "label": ent.label_
                    })
        
        except Exception as e:
            logger.error(f"Error during NER detection: {e}")
        
        return detections
    
    def _map_entity_type(self, spacy_label: str) -> str:
        """
        Map spaCy entity labels to our PII categories.
        
        spaCy labels: PERSON, ORG, GPE, DATE, MONEY, etc.
        
        Args:
            spacy_label: Original spaCy label
            
        Returns:
            Mapped type or None if not relevant
        """
        mapping = {
            'PERSON': 'person',
            'ORG': 'org',
            'GPE': 'gpe',  # Geo-Political Entity (countries, cities)
            'LOC': 'location',
            'FAC': 'facility',
            'MONEY': 'financial',
            'DATE': 'date',
            'TIME': 'time',
            'NORP': 'nationality',  # Nationalities, religious groups
            'EVENT': 'event'
        }
        
        return mapping.get(spacy_label, None)
    
    def _get_confidence(self, entity) -> float:
        """
        Estimate confidence score for detected entity.
        
        spaCy doesn't provide direct confidence scores for NER,
        so we use entity length and context as heuristics.
        
        Args:
            entity: spaCy entity object
            
        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence by entity type
        base_confidence = {
            'PERSON': 0.85,
            'ORG': 0.80,
            'GPE': 0.75,
            'MONEY': 0.90,
            'DATE': 0.70
        }
        
        confidence = base_confidence.get(entity.label_, 0.7)
        
        # Adjust based on entity length (longer = more confident)
        # Single-word entities are less reliable
        word_count = len(entity.text.split())
        if word_count == 1:
            confidence *= 0.9
        elif word_count >= 3:
            confidence = min(0.95, confidence * 1.05)
        
        return confidence
    
    def detect_financial_entities(self, text: str, language: str = "en") -> List[Dict]:
        """
        Specialized detection for financial information.
        
        Args:
            text: Input text
            
        Returns:
            List of financial entity detections
        """
        nlp = self._select_nlp(language)
        if nlp is None:
            return []
        
        detections = []
        
        try:
            doc = nlp(text)
            
            # Look for MONEY entities and context
            for ent in doc.ents:
                if ent.label_ == 'MONEY':
                    detections.append({
                        "type": "financial",
                        "value": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.9,
                        "label": "MONEY"
                    })
        
        except Exception as e:
            logger.error(f"Error detecting financial entities: {e}")
        
        return detections
    
    def combine_with_regex(
        self,
        regex_detections: List[Dict],
        ner_detections: List[Dict]
    ) -> List[Dict]:
        """
        Combine regex and NER detections, removing duplicates.
        
        Args:
            regex_detections: Detections from regex patterns
            ner_detections: Detections from NER
            
        Returns:
            Combined and deduplicated list
        """
        combined = []
        
        # Add all regex detections (higher precision)
        combined.extend(regex_detections)
        
        # Add NER detections that don't overlap with regex
        for ner_det in ner_detections:
            ner_start = ner_det["start"]
            ner_end = ner_det["end"]
            
            # Check for overlap with existing detections
            overlaps = False
            for existing in combined:
                ex_start = existing["start"]
                ex_end = existing["end"]
                
                # Check if ranges overlap
                if not (ner_end <= ex_start or ner_start >= ex_end):
                    overlaps = True
                    break
            
            if not overlaps:
                combined.append(ner_det)
        
        # Sort by start position
        combined.sort(key=lambda x: x["start"])
        
        return combined
    
    def get_context_window(
        self,
        text: str,
        entity: Dict,
        window_size: int = 50
    ) -> str:
        """
        Extract context around detected entity for analysis.
        
        Args:
            text: Original text
            entity: Detected entity dict
            window_size: Characters to include before/after
            
        Returns:
            Context string
        """
        start = max(0, entity["start"] - window_size)
        end = min(len(text), entity["end"] + window_size)
        
        context = text[start:end]
        
        # Add ellipsis if truncated
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
