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
            
            # Preprocess if requested
            if preprocess:
                opencv_image = self._preprocess_image(opencv_image)
            
            # Extract text with confidence data
            data = pytesseract.image_to_data(
                opencv_image,
                output_type=pytesseract.Output.DICT
            )
            
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
    
    def _preprocess_image(self, image):
        """
        Preprocess image for better OCR accuracy.
        
        Steps:
        1. Convert to grayscale
        2. Apply thresholding
        3. Noise reduction
        4. Deskewing (optional)
        
        Args:
            image: OpenCV image
            
        Returns:
            Preprocessed image
        """
        try:
            import cv2
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise while preserving edges
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Apply adaptive thresholding
            # This works better than simple thresholding for varying lighting
            thresh = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Optional: Deskew
            # Uncomment if dealing with rotated images
            # thresh = self._deskew(thresh)
            
            return thresh
        
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
