"""
OCR Service for extracting text from images.
Uses PyTesseract and OpenCV for preprocessing.
"""

from typing import Dict, Tuple
import logging
import io
import os
import shutil

logger = logging.getLogger(__name__)

class OCRService:
    """
    OCR service for extracting text from images.
    Includes preprocessing for better accuracy.
    """
    
    def __init__(
        self,
        tesseract_path: str = None,
        tessdata_path: str = None,
        language_priority: list = None
    ):
        """
        Initialize OCR service.

        Args:
            tesseract_path: Optional path to tesseract executable
            tessdata_path: Optional path to tessdata language files directory
            language_priority: Preferred OCR language combinations in order
        """
        self.tesseract_path = tesseract_path
        self.tessdata_path = tessdata_path
        self.language_priority = language_priority or ['eng+kan', 'eng']
        self._setup_tesseract()
    
    def _setup_tesseract(self):
        """Configure tesseract path from config, PATH, or common install locations."""
        try:
            import pytesseract

            if self.tessdata_path and os.path.isdir(self.tessdata_path):
                os.environ['TESSDATA_PREFIX'] = self.tessdata_path
                logger.info(f"TESSDATA_PREFIX set to: {self.tessdata_path}")

            configured = (self.tesseract_path or '').strip().strip('"')
            normalized_configured = configured.replace('\\\\', '\\') if configured else ''

            candidates = [
                configured,
                normalized_configured,
                shutil.which('tesseract') or '',
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]

            resolved = next((path for path in candidates if path and os.path.exists(path)), None)

            if resolved:
                pytesseract.pytesseract.tesseract_cmd = resolved
                self.tesseract_path = resolved
                logger.info(f"Tesseract path set to: {resolved}")
            else:
                logger.warning(
                    "Tesseract executable not found. Checked configured path, PATH, and common install paths."
                )

        except Exception as e:
            logger.warning(f"Could not set tesseract path: {e}")
    
    def extract_text_from_image(
        self,
        image_data: bytes,
        preprocess: bool = True
    ) -> Dict:
        """
        Extract text from image with OCR.
        
        Args:
            image_data: Image bytes
            preprocess: Whether to apply preprocessing
            
        Returns:
            Dict with:
            - text: Extracted text
            - confidence: Average OCR confidence (0-100)
            - metadata: Additional OCR metadata
        """
        try:
            import pytesseract
            from pytesseract.pytesseract import TesseractNotFoundError
            from PIL import Image
            import cv2
            import numpy as np
            
            # Load image
            image = Image.open(io.BytesIO(image_data))
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Upscale small images — improves OCR accuracy significantly
            opencv_image = self._upscale_image(opencv_image)

            # Preprocess if requested
            if preprocess:
                opencv_image = self._preprocess_multi_strategy(opencv_image)

            # Try multiple OCR language/config combinations and keep the best readable output.
            available_languages = set(pytesseract.get_languages(config=''))

            language_candidates = []

            for candidate in self.language_priority:
                parts = [part.strip() for part in candidate.split('+') if part.strip()]
                if parts and all(part in available_languages for part in parts):
                    language_candidates.append('+'.join(parts))

            # Conservative fallbacks if configured options are unavailable.
            if {'eng', 'kan'}.issubset(available_languages):
                language_candidates.append('eng+kan')
            if 'eng' in available_languages:
                language_candidates.append('eng')

            # Remove duplicates while preserving order.
            language_candidates = list(dict.fromkeys(language_candidates))
            config_candidates = ['--oem 3 --psm 6', '--oem 3 --psm 4', '--oem 3 --psm 11']

            best_result = None
            errors = []

            for lang in language_candidates:
                for tess_config in config_candidates:
                    try:
                        data = pytesseract.image_to_data(
                            opencv_image,
                            lang=lang,
                            config=tess_config,
                            output_type=pytesseract.Output.DICT
                        )
                        text = pytesseract.image_to_string(
                            opencv_image,
                            lang=lang,
                            config=tess_config
                        )

                        confidences = self._extract_confidences(data)
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                        quality_score = self._score_ocr_text(text, avg_confidence)

                        candidate = {
                            'text': text,
                            'data': data,
                            'avg_confidence': avg_confidence,
                            'quality_score': quality_score,
                            'lang': lang,
                            'tess_config': tess_config,
                            'confidences': confidences,
                        }

                        if best_result is None or candidate['quality_score'] > best_result['quality_score']:
                            best_result = candidate

                    except TesseractNotFoundError:
                        raise RuntimeError(
                            "Tesseract executable not found. Install Tesseract OCR and set TESSERACT_PATH in backend/.env"
                        )
                    except Exception as e:
                        errors.append(f"{lang} {tess_config}: {e}")
                        logger.debug(f"Tesseract lang={lang}, cfg={tess_config} failed: {e}")
                        continue

            if best_result is None:
                if errors:
                    raise RuntimeError(
                        "Tesseract failed for all language/config combinations. " + " | ".join(errors)
                    )
                raise RuntimeError("Tesseract failed for all language/config combinations")

            extracted_text = self._normalize_ocr_text(best_result['text'])
            avg_confidence = best_result['avg_confidence']
            confidences = best_result['confidences']
            
            logger.info(f"OCR extracted {len(extracted_text)} characters with {avg_confidence:.1f}% confidence")
            
            return {
                "text": extracted_text,
                "confidence": avg_confidence,
                "metadata": {
                    "word_count": len([w for w in best_result['data']['text'] if str(w).strip()]),
                    "low_confidence_words": len([c for c in confidences if c < 60]),
                    "selected_language": best_result['lang'],
                    "selected_config": best_result['tess_config']
                }
            }
        
        except ImportError as e:
            logger.error(f"Required library not installed: {e}")
            return {
                "text": "",
                "confidence": 0,
                "metadata": {"error": "OCR libraries not available"}
            }
        
        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return {
                "text": "",
                "confidence": 0,
                "metadata": {"error": str(e)}
            }
    
    def _upscale_image(self, image, target_min_dim: int = 1400):
        """
        Scale up images whose shorter side is below target_min_dim pixels.
        Upscaling markedly improves Tesseract accuracy on small or
        medium-resolution scans (e.g. phone photos of ID cards).
        """
        try:
            import cv2
            h, w = image.shape[:2]
            min_dim = min(h, w)
            if min_dim < target_min_dim:
                scale = target_min_dim / min_dim
                new_w, new_h = int(w * scale), int(h * scale)
                image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
                logger.debug(f"Upscaled image {w}x{h} -> {new_w}x{new_h}")
        except Exception as e:
            logger.warning(f"Could not upscale image: {e}")
        return image

    def _preprocess_multi_strategy(self, image):
        """
        Try multiple preprocessing strategies and return the one that yields
        the most readable text.  This handles colored and complex backgrounds
        such as those found on Indian government ID cards (PAN, Aadhaar, etc).

        Strategies:
        1. CLAHE + Otsu global threshold  — general purpose
        2. Blue-channel negative + Otsu   — blue-tinted ID cards
        3. Adaptive threshold             — original fallback
        """
        try:
            import cv2

            candidates = {}

            # Strategy 1: CLAHE on grayscale + Otsu
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(gray)
                _, thresh = cv2.threshold(
                    enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
                candidates['clahe_otsu'] = thresh
            except Exception:
                pass

            # Strategy 2: Blue channel inversion (works for blue-background ID cards)
            try:
                b_channel = image[:, :, 0]  # OpenCV BGR: index 0 == Blue
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                b_enhanced = clahe.apply(b_channel)
                _, thresh = cv2.threshold(
                    b_enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
                )
                candidates['blue_inv'] = thresh
            except Exception:
                pass

            # Strategy 3: Adaptive threshold (original approach)
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                denoised = cv2.bilateralFilter(gray, 9, 75, 75)
                thresh = cv2.adaptiveThreshold(
                    denoised, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                    11, 2
                )
                candidates['adaptive'] = thresh
            except Exception:
                pass

            if not candidates:
                return image

            # Pick the strategy that yields the most words
            try:
                import pytesseract
                best_img = next(iter(candidates.values()))
                best_score = -1
                for name, img in candidates.items():
                    text = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
                    score = self._score_ocr_text(text, 0.0)
                    logger.debug(f"Preprocessing strategy '{name}': score={score:.2f}")
                    if score > best_score:
                        best_score = score
                        best_img = img
                return best_img
            except Exception:
                return next(iter(candidates.values()))

        except Exception as e:
            logger.warning(f"Error in preprocessing, using original: {e}")
            return image

    def _extract_confidences(self, data) -> list:
        """Extract usable OCR confidence values from pytesseract output."""
        confidences = []
        for conf in data.get('conf', []):
            try:
                parsed = float(conf)
                if parsed >= 0:
                    confidences.append(parsed)
            except (TypeError, ValueError):
                continue
        return confidences

    def _score_ocr_text(self, text: str, avg_confidence: float) -> float:
        """Heuristic quality score to prefer readable OCR output for identity documents."""
        if not text:
            return 0.0

        text = text.strip()
        if not text:
            return 0.0

        total_chars = len(text)
        alnum_chars = sum(1 for c in text if c.isalnum() or c.isspace())
        readable_ratio = alnum_chars / max(1, total_chars)
        token_count = len([t for t in text.split() if len(t) > 1])

        keyword_boost = 0.0
        lowered = text.lower()
        for keyword in ('aadhaar', 'government', 'india', 'enrolment', 'uidai', 'dob'):
            if keyword in lowered:
                keyword_boost += 0.2

        return (readable_ratio * 2.0) + min(2.0, token_count / 35.0) + (avg_confidence / 100.0) + keyword_boost

    def _normalize_ocr_text(self, text: str) -> str:
        """Normalize OCR text while preserving useful line boundaries."""
        if not text:
            return ""

        normalized_lines = []
        for line in text.splitlines():
            compact = " ".join(line.split())
            if compact:
                normalized_lines.append(compact)
        return "\n".join(normalized_lines)
    
    def _deskew(self, image):
        """
        Deskew image by detecting and correcting rotation.
        
        Args:
            image: Grayscale image
            
        Returns:
            Deskewed image
        """
        try:
            import cv2
            import numpy as np
            
            # Calculate skew angle
            coords = np.column_stack(np.where(image > 0))
            angle = cv2.minAreaRect(coords)[-1]
            
            # Correct angle
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Rotate image
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            
            return rotated
        
        except Exception as e:
            logger.warning(f"Could not deskew image: {e}")
            return image
    
    def detect_image_type(self, image_data: bytes) -> str:
        """
        Detect type of content in image (screenshot, photo, document, etc.).
        
        Args:
            image_data: Image bytes
            
        Returns:
            Image type string
        """
        try:
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_data))
            
            # Simple heuristics based on dimensions and format
            width, height = image.size
            aspect_ratio = width / height
            
            # Screenshot detection (common resolutions)
            if aspect_ratio in [16/9, 16/10, 4/3] and width >= 1024:
                return "screenshot"
            
            # Document scan (portrait, high contrast)
            if aspect_ratio < 1.0 and width < 1024:
                return "document"
            
            # Photo
            if image.format in ['JPEG', 'JPG']:
                return "photo"
            
            return "unknown"
        
        except Exception as e:
            logger.error(f"Error detecting image type: {e}")
            return "unknown"
    
    def validate_image(self, image_data: bytes) -> Tuple[bool, str]:
        """
        Validate image data before processing.
        
        Args:
            image_data: Image bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            from PIL import Image
            import io
            
            # Try to open image
            image = Image.open(io.BytesIO(image_data))
            
            # Check format
            if image.format not in ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP']:
                return False, "Unsupported image format"
            
            # Check size (max 10MB)
            if len(image_data) > 10 * 1024 * 1024:
                return False, "Image too large (max 10MB)"
            
            # Check dimensions
            width, height = image.size
            if width < 100 or height < 100:
                return False, "Image too small (min 100x100)"
            
            if width > 4096 or height > 4096:
                return False, "Image dimensions too large (max 4096x4096)"
            
            return True, ""
        
        except Exception as e:
            return False, f"Invalid image: {str(e)}"
