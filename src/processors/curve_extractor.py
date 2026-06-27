"""Curve extraction from graph images"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

from ..utils.logger import get_logger
from ..utils.constants import SMOOTHING_WINDOW

logger = get_logger(__name__)

class CurveExtractor:
    """
    Extract light curve data from graph images.
    """
    
    def __init__(self):
        self.curve_points = None
        self.x_data = None
        self.y_data = None
        self.smoothed_data = None
        self.axes_bounds = None
    
    def extract_curve(self, image: np.ndarray, tolerance: int = 30) -> bool:
        """
        Extract the plotted curve from image.
        
        Args:
            image: Input image
            tolerance: Color tolerance for curve detection
            
        Returns:
            bool: True if successful
        """
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Look for blue/dark colored curves (typical scientific plots)
            # Adjust these ranges based on actual curve colors
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # Also detect white/light curves
            lower_white = np.array([0, 0, 200])
            upper_white = np.array([180, 30, 255])
            white_mask = cv2.inRange(hsv, lower_white, upper_white)
            
            # Combine masks
            mask = cv2.bitwise_or(mask, white_mask)
            
            # Apply morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                logger.warning("No curve detected in image")
                return False
            
            # Get the largest contour (the curve)
            curve_contour = max(contours, key=cv2.contourArea)
            
            # Extract points from contour
            points = curve_contour.reshape(-1, 2).astype(float)
            
            # Sort points by x coordinate
            points = points[points[:, 0].argsort()]
            
            self.curve_points = points
            logger.info(f"Extracted curve with {len(points)} points")
            return True
        
        except Exception as e:
            logger.error(f"Error extracting curve: {str(e)}")
            return False
    
    def detect_curve_color(self, image: np.ndarray) -> Tuple[int, int, int]:
        """
        Detect the primary curve color in image.
        
        Args:
            image: Input image
            
        Returns:
            Tuple: (B, G, R) color value
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Find non-white, non-black pixels
        lower = np.array([0, 30, 30])
        upper = np.array([180, 255, 200])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Find most common color
        if mask.sum() > 0:
            dominant_color = cv2.mean(image, mask=mask)[:3]
            return tuple(int(x) for x in dominant_color)
        
        return (0, 0, 255)  # Default to red
    
    def calibrate_axes(self, image: np.ndarray, x_range: Tuple[float, float], 
                      y_range: Tuple[float, float]) -> bool:
        """
        Calibrate pixel coordinates to data coordinates.
        
        Args:
            image: Input image
            x_range: (x_min, x_max) data range
            y_range: (y_min, y_max) data range
            
        Returns:
            bool: True if successful
        """
        try:
            h, w = image.shape[:2]
            
            # Assume axes are at image borders
            # Left axis (y-axis) at x=0, right at x=w
            # Bottom axis (x-axis) at y=h, top at y=0
            
            self.axes_bounds = {
                'x_pixel_range': (0, w),
                'y_pixel_range': (0, h),
                'x_data_range': x_range,
                'y_data_range': y_range
            }
            
            logger.info(f"Axes calibrated: X({x_range[0]}-{x_range[1]}), Y({y_range[0]}-{y_range[1]})")
            return True
        
        except Exception as e:
            logger.error(f"Error calibrating axes: {str(e)}")
            return False
    
    def pixel_to_data(self, pixel_x: float, pixel_y: float) -> Tuple[float, float]:
        """
        Convert pixel coordinates to data coordinates.
        
        Args:
            pixel_x: X coordinate in pixels
            pixel_y: Y coordinate in pixels
            
        Returns:
            Tuple: (data_x, data_y)
        """
        if self.axes_bounds is None:
            logger.warning("Axes not calibrated, returning pixel coordinates")
            return (pixel_x, pixel_y)
        
        # Linear interpolation
        x_pixel_min, x_pixel_max = self.axes_bounds['x_pixel_range']
        y_pixel_min, y_pixel_max = self.axes_bounds['y_pixel_range']
        x_data_min, x_data_max = self.axes_bounds['x_data_range']
        y_data_min, y_data_max = self.axes_bounds['y_data_range']
        
        # Note: Y axis is inverted in images (0 at top)
        data_x = x_data_min + (pixel_x - x_pixel_min) / (x_pixel_max - x_pixel_min) * (x_data_max - x_data_min)
        data_y = y_data_max - (pixel_y - y_pixel_min) / (y_pixel_max - y_pixel_min) * (y_data_max - y_data_min)
        
        return (data_x, data_y)
    
    def reconstruct_light_curve(self, calibrate: bool = True) -> bool:
        """
        Reconstruct numerical light curve from extracted points.
        
        Args:
            calibrate: Whether to calibrate to data coordinates
            
        Returns:
            bool: True if successful
        """
        try:
            if self.curve_points is None or len(self.curve_points) < 3:
                logger.error("Not enough points to reconstruct curve")
                return False
            
            if calibrate and self.axes_bounds:
                # Convert pixel to data coordinates
                x_data = []
                y_data = []
                for px, py in self.curve_points:
                    dx, dy = self.pixel_to_data(px, py)
                    x_data.append(dx)
                    y_data.append(dy)
                self.x_data = np.array(x_data)
                self.y_data = np.array(y_data)
            else:
                # Use pixel coordinates directly
                self.x_data = self.curve_points[:, 0]
                self.y_data = self.curve_points[:, 1]
            
            logger.info(f"Reconstructed light curve: {len(self.x_data)} points")
            return True
        
        except Exception as e:
            logger.error(f"Error reconstructing light curve: {str(e)}")
            return False
    
    def smooth_curve(self, window_length: int = SMOOTHING_WINDOW, polyorder: int = 2) -> bool:
        """
        Smooth the light curve while preserving transit features.
        
        Args:
            window_length: Savitzky-Golay window length
            polyorder: Polynomial order
            
        Returns:
            bool: True if successful
        """
        try:
            if self.y_data is None or len(self.y_data) < window_length:
                logger.warning("Not enough data points for smoothing")
                return False
            
            # Ensure odd window length
            if window_length % 2 == 0:
                window_length += 1
            
            # Apply Savitzky-Golay filter
            self.smoothed_data = savgol_filter(self.y_data, window_length, polyorder)
            
            logger.info(f"Smoothed curve with window={window_length}, polyorder={polyorder}")
            return True
        
        except Exception as e:
            logger.error(f"Error smoothing curve: {str(e)}")
            return False
    
    def get_raw_curve(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get raw extracted curve data.
        
        Returns:
            Tuple: (x_data, y_data)
        """
        return (self.x_data, self.y_data)
    
    def get_smoothed_curve(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get smoothed curve data.
        
        Returns:
            Tuple: (x_data, y_smoothed)
        """
        return (self.x_data, self.smoothed_data)
    
    def get_curve_points(self) -> np.ndarray:
        """
        Get extracted pixel coordinates.
        
        Returns:
            np.ndarray: Curve points
        """
        return self.curve_points