"""Image processing and graph detection"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image

from ..utils.logger import get_logger
from ..utils.constants import SUPPORTED_FORMATS, MAX_IMAGE_SIZE, MIN_IMAGE_SIZE

logger = get_logger(__name__)

class ImageProcessor:
    """
    Handle image loading, preprocessing, and graph detection.
    """
    
    def __init__(self):
        self.original_image = None
        self.processed_image = None
        self.graph_region = None
    
    def load_image(self, image_path: str) -> bool:
        """
        Load image from file path.
        
        Args:
            image_path: Path to image file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            path = Path(image_path)
            
            # Check file extension
            if path.suffix.lower() not in SUPPORTED_FORMATS:
                logger.error(f"Unsupported format: {path.suffix}")
                return False
            
            # Load image
            self.original_image = cv2.imread(str(path))
            if self.original_image is None:
                logger.error(f"Failed to load image: {image_path}")
                return False
            
            # Validate size
            h, w = self.original_image.shape[:2]
            if not (MIN_IMAGE_SIZE[0] <= w <= MAX_IMAGE_SIZE[0] and 
                    MIN_IMAGE_SIZE[1] <= h <= MAX_IMAGE_SIZE[1]):
                logger.warning(f"Image size {w}x{h} may be too large or small")
            
            logger.info(f"Successfully loaded image: {image_path} ({w}x{h})")
            self.processed_image = self.original_image.copy()
            return True
        
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return False
    
    def load_from_pil(self, pil_image: Image.Image) -> bool:
        """
        Load image from PIL Image object.
        
        Args:
            pil_image: PIL Image object
            
        Returns:
            bool: True if successful
        """
        try:
            # Convert PIL to OpenCV format
            pil_image_rgb = pil_image.convert('RGB')
            self.original_image = cv2.cvtColor(np.array(pil_image_rgb), cv2.COLOR_RGB2BGR)
            self.processed_image = self.original_image.copy()
            logger.info(f"Loaded image from PIL object")
            return True
        except Exception as e:
            logger.error(f"Error loading PIL image: {str(e)}")
            return False
    
    def remove_white_borders(self) -> np.ndarray:
        """
        Remove white/light borders from image.
        
        Returns:
            np.ndarray: Image with borders removed
        """
        if self.processed_image is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
        
        # Threshold for white regions (>200)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours and bounding rectangle
        contours, _ = cv2.findContours(cv2.bitwise_not(thresh), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return self.processed_image
        
        # Get bounding box of all contours
        x, y, w, h = cv2.boundingRect(np.concatenate(contours))
        cropped = self.processed_image[y:y+h, x:x+w]
        
        self.processed_image = cropped
        logger.info(f"Removed white borders, new size: {w}x{h}")
        return self.processed_image
    
    def detect_graph_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the graph/plot region in the image.
        
        Returns:
            Tuple: (x, y, width, height) of graph region, or None
        """
        if self.processed_image is None:
            return None
        
        gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate to connect edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            logger.warning("No graph region detected")
            return None
        
        # Find largest contour (likely the graph)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Verify it's a reasonably sized region
        if w < 100 or h < 100:
            logger.warning("Detected region too small")
            return None
        
        self.graph_region = (x, y, w, h)
        logger.info(f"Detected graph region: x={x}, y={y}, w={w}, h={h}")
        return self.graph_region
    
    def improve_contrast(self, clip_limit: float = 2.0, tile_size: int = 8) -> np.ndarray:
        """
        Improve image contrast using CLAHE.
        
        Args:
            clip_limit: Clip limit for CLAHE
            tile_size: Tile grid size
            
        Returns:
            np.ndarray: Contrast-enhanced image
        """
        if self.processed_image is None:
            return None
        
        # Convert to LAB color space
        lab = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
        l_enhanced = clahe.apply(l_channel)
        
        # Merge channels back
        lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
        enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        
        self.processed_image = enhanced
        logger.info("Contrast improved")
        return self.processed_image
    
    def remove_artifacts(self) -> np.ndarray:
        """
        Remove compression artifacts using bilateral filtering.
        
        Returns:
            np.ndarray: Filtered image
        """
        if self.processed_image is None:
            return None
        
        # Bilateral filter preserves edges while smoothing
        filtered = cv2.bilateralFilter(self.processed_image, 9, 75, 75)
        self.processed_image = filtered
        logger.info("Artifacts removed")
        return self.processed_image
    
    def detect_axes(self) -> dict:
        """
        Detect axes in the graph.
        
        Returns:
            dict: Axis information (x_min, x_max, y_min, y_max, orientation)
        """
        if self.processed_image is None:
            return None
        
        gray = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
        
        # Detect lines using Hough transform
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)
        
        if lines is None:
            logger.warning("No axes detected")
            return None
        
        # Separate horizontal and vertical lines
        horizontal_lines = []
        vertical_lines = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.abs(np.arctan2(y2-y1, x2-x1))
            
            # Lines close to 0 or pi are horizontal
            if angle < np.pi/6 or angle > 5*np.pi/6:
                horizontal_lines.append((y1 + y2) / 2)  # Average y position
            # Lines close to pi/2 are vertical
            elif np.pi/3 < angle < 2*np.pi/3:
                vertical_lines.append((x1 + x2) / 2)  # Average x position
        
        axes_info = {
            'horizontal_lines': horizontal_lines,
            'vertical_lines': vertical_lines,
            'has_axes': len(horizontal_lines) > 0 and len(vertical_lines) > 0
        }
        
        logger.info(f"Detected axes: {axes_info}")
        return axes_info
    
    def get_processed_image(self) -> Optional[np.ndarray]:
        """
        Get the current processed image.
        
        Returns:
            np.ndarray: Processed image
        """
        return self.processed_image
    
    def get_original_image(self) -> Optional[np.ndarray]:
        """
        Get the original image.
        
        Returns:
            np.ndarray: Original image
        """
        return self.original_image
    
    def preprocess_pipeline(self) -> bool:
        """
        Run complete preprocessing pipeline.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Starting preprocessing pipeline")
            
            self.remove_white_borders()
            self.remove_artifacts()
            self.improve_contrast()
            
            logger.info("Preprocessing pipeline completed")
            return True
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {str(e)}")
            return False