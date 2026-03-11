"""
OCR Service for extracting text from images.
Uses PyTesseract and OpenCV for preprocessing.
"""

from typing import Dict, Tuple
import logging
import io

logger = logging.getLogger(__name__)

class OCRService:
    """
    OCR service for extracting text from images.
    Includes preprocessing for better accuracy.
    """
    
    def __init__(self, tesseract_path: str = None):
        """
        Initialize OCR service.
        
        Args:
            tesseract_path: Optional path to tesseract executable
        """
        self.tesseract_path = tesseract_path
        self._setup_tesseract()
    
    def _setup_tesseract(self):
        """Configure tesseract path if provided."""
        if self.tesseract_path:
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
                logger.info(f"Tesseract path set to: {self.tesseract_path}")
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
            from PIL import Image
            import cv2
            import numpy as np
            
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Upscale small images — improves OCR accuracy significantly
            opencv_image = self._upscale_image(opencv_image)

            # Preprocess if requested
            if preprocess:
                opencv_image = self._preprocess_multi_strategy(opencv_image)

            # Use LSTM engine + single-block page segmentation
            tess_config = '--oem 3 --psm 6'

            # Try multilingual (eng+hin) first, fall back to English-only
            data = None
            for lang in ('eng+hin', 'eng'):
                try:
                    data = pytesseract.image_to_data(
                        opencv_image,
                        lang=lang,
                        config=tess_config,
                        output_type=pytesseract.Output.DICT
                    )
                    break
                except Exception as e:
                    logger.debug(f"Tesseract lang={lang} failed: {e}")
                    continue

            if data is None:
                raise RuntimeError("Tesseract failed for all language configurations")

            # Get text and calculate average confidence
            extracted_text = " ".join([
                word for word in data['text'] if word.strip()
            ])
            
            # Calculate average confidence (ignore -1 values)
            confidences = [
                conf for conf in data['conf']
                if conf != -1
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            logger.info(f"OCR extracted {len(extracted_text)} characters with {avg_confidence:.1f}% confidence")
            
            return {
                "text": extracted_text,
                "confidence": avg_confidence,
                "metadata": {
                    "word_count": len([w for w in data['text'] if w.strip()]),
                    "low_confidence_words": len([c for c in confidences if c < 60])
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
                best_count = 0
                for name, img in candidates.items():
                    text = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
                    count = len([w for w in text.split() if len(w) > 1])
                    logger.debug(f"Preprocessing strategy '{name}': {count} words")
                    if count > best_count:
                        best_count = count
                        best_img = img
                return best_img
            except Exception:
                return next(iter(candidates.values()))

        except Exception as e:
            logger.warning(f"Error in preprocessing, using original: {e}")
            return image
    
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
