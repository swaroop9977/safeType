"""
NLP Intent Classification Service.
Detects phishing, suspicious, and social engineering patterns in text.
"""

from typing import Dict, List, Tuple
import logging
import re

logger = logging.getLogger(__name__)

class NLPIntentClassifier:
    """
    Transformer-based intent classifier for detecting malicious patterns.
    Uses HuggingFace transformers with fallback to keyword-based detection.
    """
    
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initialize intent classifier.
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.classifier = None
        self._load_model()
        
        # Phishing keyword patterns (fallback and enhancement)
        self.urgency_keywords = [
            r'\burgent\b', r'\bimmediate\b', r'\bact now\b', r'\bexpir(ing|ed)\b',
            r'\bsuspend(ed)?\b', r'\blimited time\b', r'\bverify (now|immediately)\b',
            r'\bconfirm your\b', r'\bupdate your\b', r'\bunusual activity\b'
        ]
        
        self.reward_keywords = [
            r'\bcongratulations\b', r'\bwinner\b', r'\bprize\b', r'\bfree\b',
            r'\bclaim your\b', r'\breward\b', r'\bbonus\b', r'\bgift card\b'
        ]
        
        self.authority_keywords = [
            r'\bbank\b', r'\btax\b', r'\birs\b', r'\bgovernment\b',
            r'\bpolice\b', r'\bcourt\b', r'\blegal action\b', r'\baccount suspended\b'
        ]
        
        self.action_keywords = [
            r'\bclick here\b', r'\bdownload\b', r'\bopen attachment\b',
            r'\bprovide\b', r'\bsend us\b', r'\bshare your\b', r'\benter your\b'
        ]
    
    def _load_model(self):
        """Load HuggingFace transformer model."""
        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "text-classification",
                model=self.model_name,
                device=-1  # CPU
            )
            logger.info(f"Loaded transformer model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not load transformer model: {e}. Using keyword fallback.")
            self.classifier = None
    
    def classify_intent(self, text: str) -> Dict[str, float]:
        """
        Classify text intent with probability scores.
        
        Returns probabilities for:
        - benign: Normal, safe content
        - suspicious: Potentially concerning
        - phishing: High likelihood of phishing attempt
        - social_engineering: Manipulation tactics detected
        
        Args:
            text: Input text to classify
            
        Returns:
            Dict mapping intent classes to probabilities (0-1)
        """
        if not text or len(text.strip()) == 0:
            return {"benign": 1.0}
        
        # Get transformer predictions
        transformer_probs = self._get_transformer_predictions(text)
        
        # Get keyword-based scores
        keyword_scores = self._get_keyword_scores(text)
        
        # Combine both approaches
        combined_scores = self._combine_scores(transformer_probs, keyword_scores)
        
        return combined_scores
    
    def _get_transformer_predictions(self, text: str) -> Dict[str, float]:
        """
        Get predictions from transformer model.
        
        Args:
            text: Input text
            
        Returns:
            Dict of class probabilities
        """
        if self.classifier is None:
            return {}
        
        try:
            # Truncate text if too long (transformer limit ~512 tokens)
            max_length = 500
            truncated_text = text[:max_length] if len(text) > max_length else text
            
            results = self.classifier(truncated_text, top_k=2)
            
            # Convert to our format
            probs = {}
            for result in results:
                label = result['label']
                score = result['score']
                
                # Map sentiment labels to intent
                # Negative sentiment can indicate suspicious content
                # Positive sentiment can indicate manipulation (fake rewards)
                if label in ['NEGATIVE', 'LABEL_0']:
                    probs['suspicious'] = score
                elif label in ['POSITIVE', 'LABEL_1']:
                    probs['benign'] = score
            
            return probs
        
        except Exception as e:
            logger.error(f"Error in transformer prediction: {e}")
            return {}
    
    def _get_keyword_scores(self, text: str) -> Dict[str, float]:
        """
        Compute intent scores based on keyword patterns.
        
        Args:
            text: Input text
            
        Returns:
            Dict of intent scores
        """
        text_lower = text.lower()
        
        # Count matches for each category
        urgency_count = sum(
            1 for pattern in self.urgency_keywords
            if re.search(pattern, text_lower)
        )
        
        reward_count = sum(
            1 for pattern in self.reward_keywords
            if re.search(pattern, text_lower)
        )
        
        authority_count = sum(
            1 for pattern in self.authority_keywords
            if re.search(pattern, text_lower)
        )
        
        action_count = sum(
            1 for pattern in self.action_keywords
            if re.search(pattern, text_lower)
        )
        
        # Compute scores (normalized)
        # Multiple indicators = higher phishing probability
        total_indicators = urgency_count + reward_count + authority_count + action_count
        
        if total_indicators == 0:
            return {"benign": 0.8}
        
        # Scoring logic
        phishing_score = 0.0
        social_engineering_score = 0.0
        suspicious_score = 0.0
        
        # Strong phishing indicators
        if urgency_count >= 2 or (urgency_count >= 1 and action_count >= 1):
            phishing_score = 0.7 + (0.1 * min(total_indicators, 3))
        
        # Social engineering tactics
        if reward_count >= 1 or authority_count >= 1:
            social_engineering_score = 0.6 + (0.1 * min(total_indicators, 3))
        
        # General suspicion
        if total_indicators >= 1:
            suspicious_score = 0.4 + (0.1 * min(total_indicators, 4))
        
        # Take maximum across categories
        max_score = max(phishing_score, social_engineering_score, suspicious_score)
        
        if max_score >= 0.7:
            return {"phishing": phishing_score}
        elif max_score >= 0.6:
            return {"social_engineering": social_engineering_score}
        elif max_score >= 0.4:
            return {"suspicious": suspicious_score}
        else:
            return {"benign": 0.6}
    
    def _combine_scores(
        self,
        transformer_probs: Dict[str, float],
        keyword_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Combine transformer and keyword-based scores.
        
        Args:
            transformer_probs: Probabilities from transformer
            keyword_scores: Scores from keyword matching
            
        Returns:
            Combined probability distribution
        """
        # Initialize with default benign
        combined = {
            "benign": 0.0,
            "suspicious": 0.0,
            "phishing": 0.0,
            "social_engineering": 0.0
        }
        
        # Weight transformer and keywords (60-40 split)
        transformer_weight = 0.4 if transformer_probs else 0.0
        keyword_weight = 0.6 if keyword_scores else 1.0
        
        # Combine scores
        for intent in combined.keys():
            transformer_score = transformer_probs.get(intent, 0.0)
            keyword_score = keyword_scores.get(intent, 0.0)
            
            combined[intent] = (
                transformer_score * transformer_weight +
                keyword_score * keyword_weight
            )
        
        # Normalize to sum to 1.0
        total = sum(combined.values())
        if total > 0:
            combined = {k: v / total for k, v in combined.items()}
        else:
            combined["benign"] = 1.0
        
        return combined
    
    def detect_phishing_keywords(self, text: str) -> List[Dict]:
        """
        Detect specific phishing keywords and their positions.
        
        Args:
            text: Input text
            
        Returns:
            List of detected keyword spans
        """
        detections = []
        text_lower = text.lower()
        
        all_patterns = (
            self.urgency_keywords +
            self.reward_keywords +
            self.authority_keywords +
            self.action_keywords
        )
        
        for pattern in all_patterns:
            for match in re.finditer(pattern, text_lower):
                detections.append({
                    "type": "phishing_keyword",
                    "value": text[match.start():match.end()],  # Preserve original case
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.8
                })
        
        return detections
    
    def analyze_sentiment_manipulation(self, text: str) -> Dict:
        """
        Analyze text for emotional manipulation tactics.
        
        Args:
            text: Input text
            
        Returns:
            Dict with manipulation analysis
        """
        analysis = {
            "uses_urgency": False,
            "uses_fear": False,
            "uses_greed": False,
            "uses_authority": False,
            "manipulation_score": 0.0
        }
        
        text_lower = text.lower()
        
        # Check for manipulation tactics
        if any(re.search(p, text_lower) for p in self.urgency_keywords):
            analysis["uses_urgency"] = True
            analysis["manipulation_score"] += 0.3
        
        if any(re.search(p, text_lower) for p in self.authority_keywords):
            analysis["uses_authority"] = True
            analysis["uses_fear"] = True
            analysis["manipulation_score"] += 0.35
        
        if any(re.search(p, text_lower) for p in self.reward_keywords):
            analysis["uses_greed"] = True
            analysis["manipulation_score"] += 0.25
        
        # Cap at 1.0
        analysis["manipulation_score"] = min(1.0, analysis["manipulation_score"])
        
        return analysis
