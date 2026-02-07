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
    
    def __init__(
        self,
        model_name: str = "distilbert-base-uncased-finetuned-sst-2-english",
        multilingual_model_name: str = None
    ):
        """
        Initialize intent classifier.
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.multilingual_model_name = multilingual_model_name
        self.classifier_en = None
        self.classifier_multi = None
        self._load_models()

        # Phishing keyword patterns by language (fallback and enhancement)
        self.keyword_patterns = {
            "en": {
                "urgency": [
                    r"\burgent\b", r"\bimmediate\b", r"\bact now\b",
                    r"\bexpir(ing|ed)\b", r"\bsuspend(ed)?\b",
                    r"\blimited time\b", r"\bverify (now|immediately)\b",
                    r"\bconfirm your\b", r"\bupdate your\b", r"\bunusual activity\b"
                ],
                "reward": [
                    r"\bcongratulations\b", r"\bwinner\b", r"\bprize\b",
                    r"\bfree\b", r"\bclaim your\b", r"\breward\b",
                    r"\bbonus\b", r"\bgift card\b"
                ],
                "authority": [
                    r"\bbank\b", r"\btax\b", r"\birs\b", r"\bgovernment\b",
                    r"\bpolice\b", r"\bcourt\b", r"\blegal action\b",
                    r"\baccount suspended\b"
                ],
                "action": [
                    r"\bclick here\b", r"\bdownload\b", r"\bopen attachment\b",
                    r"\bprovide\b", r"\bsend us\b", r"\bshare your\b",
                    r"\benter your\b"
                ]
            },
            "es": {
                "urgency": [
                    r"\burgente\b", r"\binmediato\b", r"\bactua ahora\b",
                    r"\bexpira\b", r"\bsuspendid[ao]\b", r"\bverifica\b",
                    r"\bactualiza\b"
                ],
                "reward": [
                    r"\bganador\b", r"\bpremio\b", r"\bgratis\b",
                    r"\bbono\b", r"\bregalo\b"
                ],
                "authority": [
                    r"\bbanco\b", r"\bgobierno\b", r"\bpolicia\b",
                    r"\bimpuestos\b", r"\bcuenta suspendida\b"
                ],
                "action": [
                    r"\bhaz clic\b", r"\bdescarga\b", r"\babre el adjunto\b",
                    r"\bproporciona\b", r"\bcomparte\b", r"\bingresa\b"
                ]
            },
            "fr": {
                "urgency": [
                    r"\burgent\b", r"\bimmediat\w*\b", r"\bagissez maintenant\b",
                    r"\bexpire\b", r"\bsuspendu\b", r"\bverifiez\b",
                    r"\bconfirmez\b", r"\bmettez a jour\b"
                ],
                "reward": [
                    r"\bfelicitations\b", r"\bgagnant\b", r"\bprix\b",
                    r"\bgratuit\b", r"\brecompense\b", r"\bcadeau\b"
                ],
                "authority": [
                    r"\bbanque\b", r"\bimpots\b", r"\bgouvernement\b",
                    r"\bpolice\b", r"\bcompte suspendu\b"
                ],
                "action": [
                    r"\bcliquez ici\b", r"\btelechargez\b",
                    r"\bouvrez la piece jointe\b", r"\bfournissez\b",
                    r"\bpartagez\b", r"\bsaisissez\b"
                ]
            },
            "de": {
                "urgency": [
                    r"\bdringend\b", r"\bsofort\b", r"\bjetzt handeln\b",
                    r"\bablauf\b", r"\bgesperrt\b", r"\bbestaetigen\b",
                    r"\baktualisieren\b"
                ],
                "reward": [
                    r"\bglueckwunsch\b", r"\bgewinner\b", r"\bpreis\b",
                    r"\bgratis\b", r"\bbonus\b", r"\bgutschein\b"
                ],
                "authority": [
                    r"\bbank\b", r"\bfinanzamt\b", r"\bregierung\b",
                    r"\bpolizei\b", r"\bkonto gesperrt\b"
                ],
                "action": [
                    r"\bhier klicken\b", r"\bherunterladen\b",
                    r"\banhang oeffnen\b", r"\bgeben sie\b",
                    r"\bteilen sie\b", r"\beingeben\b"
                ]
            },
            "pt": {
                "urgency": [
                    r"\burgente\b", r"\bimediato\b", r"\baja agora\b",
                    r"\bexpira\b", r"\bsuspenso\b", r"\bverifique\b",
                    r"\batualize\b"
                ],
                "reward": [
                    r"\bparabens\b", r"\bganhador\b", r"\bpremio\b",
                    r"\bgratis\b", r"\bbonus\b", r"\bcartao presente\b"
                ],
                "authority": [
                    r"\bbanco\b", r"\bimposto\b", r"\bgoverno\b",
                    r"\bpolicia\b", r"\bconta suspensa\b"
                ],
                "action": [
                    r"\bclique aqui\b", r"\bbaixar\b",
                    r"\babra o anexo\b", r"\bforneca\b",
                    r"\bcompartilhe\b", r"\bdigite\b"
                ]
            },
            "it": {
                "urgency": [
                    r"\burgente\b", r"\bimmediato\b", r"\bagisci ora\b",
                    r"\bscade\b", r"\bsospeso\b", r"\bverifica\b",
                    r"\baggiorna\b"
                ],
                "reward": [
                    r"\bcongratulazioni\b", r"\bvincitore\b", r"\bpremio\b",
                    r"\bgratis\b", r"\bbonus\b", r"\bbuono regalo\b"
                ],
                "authority": [
                    r"\bbanca\b", r"\btasse\b", r"\bgoverno\b",
                    r"\bpolizia\b", r"\baccount sospeso\b"
                ],
                "action": [
                    r"\bclicca qui\b", r"\bscarica\b",
                    r"\bapri allegato\b", r"\bfornisci\b",
                    r"\bcondividi\b", r"\binserisci\b"
                ]
            }
        }
    
    def _load_models(self):
        """Load HuggingFace transformer models."""
        try:
            from transformers import pipeline
            self.classifier_en = pipeline(
                "text-classification",
                model=self.model_name,
                device=-1  # CPU
            )
            logger.info(f"Loaded transformer model: {self.model_name}")
        except Exception as e:
            logger.warning(
                f"Could not load transformer model: {e}. Using keyword fallback."
            )
            self.classifier_en = None

        if not self.multilingual_model_name:
            return

        try:
            from transformers import pipeline
            self.classifier_multi = pipeline(
                "text-classification",
                model=self.multilingual_model_name,
                device=-1  # CPU
            )
            logger.info(f"Loaded transformer model: {self.multilingual_model_name}")
        except Exception as e:
            logger.warning(
                f"Could not load multilingual model: {e}. Using English model."
            )
            self.classifier_multi = None

    def _normalize_language(self, language: str) -> str:
        if not language:
            return "en"

        return language.strip().lower().split("-")[0]

    def _get_classifier(self, language: str):
        lang = self._normalize_language(language)
        if lang == "en":
            return self.classifier_en

        return self.classifier_multi or self.classifier_en
    
    def classify_intent(self, text: str, language: str = "en") -> Dict[str, float]:
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
        transformer_probs = self._get_transformer_predictions(text, language)
        
        # Get keyword-based scores
        keyword_scores = self._get_keyword_scores(text, language)
        
        # Combine both approaches
        combined_scores = self._combine_scores(transformer_probs, keyword_scores)
        
        return combined_scores
    
    def _get_transformer_predictions(self, text: str, language: str) -> Dict[str, float]:
        """
        Get predictions from transformer model.
        
        Args:
            text: Input text
            
        Returns:
            Dict of class probabilities
        """
        classifier = self._get_classifier(language)
        if classifier is None:
            return {}
        
        try:
            # Truncate text if too long (transformer limit ~512 tokens)
            max_length = 500
            truncated_text = text[:max_length] if len(text) > max_length else text
            
            results = classifier(truncated_text, top_k=3)
            
            # Convert to our format
            probs = {}
            for result in results:
                intent = self._map_transformer_label(result.get('label'))
                score = result.get('score', 0.0)
                if intent:
                    probs[intent] = max(probs.get(intent, 0.0), score)
            
            return probs
        
        except Exception as e:
            logger.error(f"Error in transformer prediction: {e}")
            return {}
    
    def _get_keyword_scores(self, text: str, language: str) -> Dict[str, float]:
        """
        Compute intent scores based on keyword patterns.
        
        Args:
            text: Input text
            
        Returns:
            Dict of intent scores
        """
        text_lower = text.lower()
        
        patterns = self._get_language_patterns(language)

        # Count matches for each category
        urgency_count = sum(
            1 for pattern in patterns["urgency"]
            if re.search(pattern, text_lower)
        )

        reward_count = sum(
            1 for pattern in patterns["reward"]
            if re.search(pattern, text_lower)
        )

        authority_count = sum(
            1 for pattern in patterns["authority"]
            if re.search(pattern, text_lower)
        )

        action_count = sum(
            1 for pattern in patterns["action"]
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
    
    def detect_phishing_keywords(self, text: str, language: str = "en") -> List[Dict]:
        """
        Detect specific phishing keywords and their positions.
        
        Args:
            text: Input text
            
        Returns:
            List of detected keyword spans
        """
        detections = []
        text_lower = text.lower()
        
        patterns = self._get_language_patterns(language)
        all_patterns = (
            patterns["urgency"] +
            patterns["reward"] +
            patterns["authority"] +
            patterns["action"]
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
    
    def analyze_sentiment_manipulation(self, text: str, language: str = "en") -> Dict:
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
        
        patterns = self._get_language_patterns(language)

        # Check for manipulation tactics
        if any(re.search(p, text_lower) for p in patterns["urgency"]):
            analysis["uses_urgency"] = True
            analysis["manipulation_score"] += 0.3

        if any(re.search(p, text_lower) for p in patterns["authority"]):
            analysis["uses_authority"] = True
            analysis["uses_fear"] = True
            analysis["manipulation_score"] += 0.35

        if any(re.search(p, text_lower) for p in patterns["reward"]):
            analysis["uses_greed"] = True
            analysis["manipulation_score"] += 0.25
        
        # Cap at 1.0
        analysis["manipulation_score"] = min(1.0, analysis["manipulation_score"])
        
        return analysis

    def _map_transformer_label(self, label: str) -> str:
        if not label:
            return ""

        label_upper = str(label).upper()
        if label_upper in ["NEGATIVE", "LABEL_0"]:
            return "suspicious"
        if label_upper in ["POSITIVE", "LABEL_1"]:
            return "benign"
        if label_upper in ["NEUTRAL", "LABEL_2"]:
            return "benign"

        return ""

    def _get_language_patterns(self, language: str) -> Dict[str, List[str]]:
        lang = self._normalize_language(language)
        if lang in self.keyword_patterns:
            return self.keyword_patterns[lang]

        return self.keyword_patterns["en"]
