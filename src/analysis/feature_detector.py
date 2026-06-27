"""Feature detection for classification"""

import numpy as np
from typing import Dict, List
from scipy.signal import find_peaks

from ..utils.logger import get_logger

logger = get_logger(__name__)

class FeatureDetector:
    """
    Detect characteristic features for exoplanet, binary, and variable star classification.
    """
    
    def __init__(self, y_data: np.ndarray, x_data: np.ndarray = None):
        self.y = y_data
        self.x = x_data if x_data is not None else np.arange(len(y_data))
        self.features = {}
    
    def detect_single_dip(self) -> bool:
        """
        Detect if there's a single, isolated dip.
        
        Returns:
            bool: True if single dip detected
        """
        baseline = np.quantile(self.y, 0.9)
        below_baseline = self.y < baseline * 0.95
        
        # Count connected components
        dips = np.diff(below_baseline.astype(int))
        num_dips = np.sum(np.abs(dips)) // 2
        
        feature = num_dips == 1
        self.features['single_dip'] = feature
        logger.info(f"Single dip detected: {feature}")
        return feature
    
    def detect_multiple_dips(self) -> int:
        """
        Detect and count multiple dips.
        
        Returns:
            int: Number of dips detected
        """
        baseline = np.quantile(self.y, 0.9)
        below_baseline = self.y < baseline * 0.95
        
        dips = np.diff(below_baseline.astype(int))
        num_dips = np.sum(np.abs(dips)) // 2
        
        self.features['multiple_dips'] = num_dips
        logger.info(f"Multiple dips detected: {num_dips}")
        return num_dips
    
    def detect_periodic_dips(self) -> bool:
        """
        Detect if dips are periodic.
        
        Returns:
            bool: True if periodic pattern detected
        """
        baseline = np.quantile(self.y, 0.9)
        inverted = baseline - self.y
        
        peaks, _ = find_peaks(inverted, height=0.005)
        
        if len(peaks) < 2:
            self.features['periodic_dips'] = False
            return False
        
        spacings = np.diff(peaks)
        if len(spacings) > 1:
            spacing_std = np.std(spacings)
            spacing_mean = np.mean(spacings)
            periodicity = 1.0 - (spacing_std / spacing_mean if spacing_mean > 0 else 1.0)
            periodic = periodicity > 0.7
        else:
            periodic = False
        
        self.features['periodic_dips'] = periodic
        logger.info(f"Periodic dips detected: {periodic}")
        return periodic
    
    def detect_eclipsing_binary_signature(self) -> bool:
        """
        Detect V-shaped eclipse signature (characteristic of eclipsing binaries).
        
        Returns:
            bool: True if V-shaped signature detected
        """
        baseline = np.quantile(self.y, 0.9)
        dip_points = np.where(self.y < baseline * 0.95)[0]
        
        if len(dip_points) < 5:
            self.features['v_shaped_eclipse'] = False
            return False
        
        # Find dip region
        dip_data = self.y[dip_points]
        
        # Calculate if it's V-shaped (sharp bottom) vs U-shaped (flat bottom)
        center_idx = len(dip_points) // 2
        bottom_std = np.std(dip_data[max(0, center_idx-2):min(len(dip_data), center_idx+3)])
        
        v_shaped = bottom_std > np.std(dip_data) * 0.1
        
        self.features['v_shaped_eclipse'] = v_shaped
        logger.info(f"V-shaped eclipse detected: {v_shaped}")
        return v_shaped
    
    def detect_secondary_eclipse(self) -> bool:
        """
        Detect secondary eclipse (characteristic of eclipsing binaries).
        
        Returns:
            bool: True if secondary eclipse likely
        """
        baseline = np.quantile(self.y, 0.9)
        inverted = baseline - self.y
        
        peaks, properties = find_peaks(inverted, height=0.001, distance=20)
        
        if len(peaks) >= 2:
            # Check if two peaks have similar heights (characteristic of equal eclipses)
            heights = properties.get('peak_heights', [])
            if len(heights) >= 2:
                primary_depth = np.max(heights)
                secondary_depth = np.sort(heights)[-2] if len(heights) > 1 else 0
                
                secondary = (secondary_depth / primary_depth) > 0.3  # At least 30% of primary
                self.features['secondary_eclipse'] = secondary
                logger.info(f"Secondary eclipse detected: {secondary}")
                return secondary
        
        self.features['secondary_eclipse'] = False
        return False
    
    def detect_odd_even_difference(self) -> bool:
        """
        Detect differences between odd and even eclipses (eclipsing binary signature).
        
        Returns:
            bool: True if significant odd-even differences
        """
        baseline = np.quantile(self.y, 0.9)
        inverted = baseline - self.y
        
        peaks, properties = find_peaks(inverted, height=0.005, distance=20)
        
        if len(peaks) < 3:
            self.features['odd_even_difference'] = False
            return False
        
        heights = properties.get('peak_heights', [])
        if len(heights) < 2:
            return False
        
        odd_heights = heights[::2]
        even_heights = heights[1::2]
        
        if len(odd_heights) > 0 and len(even_heights) > 0:
            odd_mean = np.mean(odd_heights)
            even_mean = np.mean(even_heights)
            difference = abs(odd_mean - even_mean) / max(odd_mean, even_mean)
            
            has_diff = difference > 0.15
            self.features['odd_even_difference'] = has_diff
            logger.info(f"Odd-even difference detected: {has_diff} (diff={difference:.3f})")
            return has_diff
        
        self.features['odd_even_difference'] = False
        return False
    
    def detect_variable_star_oscillations(self) -> bool:
        """
        Detect periodic oscillations characteristic of variable stars.
        
        Returns:
            bool: True if oscillations detected
        """
        # Look for small-amplitude rapid oscillations
        baseline = np.median(self.y)
        detrended = self.y - baseline
        
        # Find local extrema
        maxima = find_peaks(detrended, distance=2)[0]
        minima = find_peaks(-detrended, distance=2)[0]
        
        extrema_count = len(maxima) + len(minima)
        total_points = len(self.y)
        
        # If many extrema relative to length, likely oscillations
        oscillations = (extrema_count / total_points) > 0.15
        
        self.features['variable_star_oscillations'] = oscillations
        logger.info(f"Variable star oscillations detected: {oscillations}")
        return oscillations
    
    def detect_noise(self, noise_level: float) -> bool:
        """
        Detect if signal is primarily noise.
        
        Args:
            noise_level: Estimated noise level
            
        Returns:
            bool: True if noise-dominated
        """
        signal_power = np.std(self.y)
        noise_ratio = noise_level / signal_power if signal_power > 0 else 1.0
        
        is_noise = noise_ratio > 0.5
        
        self.features['noise_dominated'] = is_noise
        logger.info(f"Noise dominated signal: {is_noise}")
        return is_noise
    
    def detect_data_gaps(self) -> int:
        """
        Detect gaps or missing data regions.
        
        Returns:
            int: Number of data gaps detected
        """
        # Look for large jumps in x-coordinates
        if len(self.x) < 2:
            return 0
        
        x_diffs = np.diff(self.x)
        median_diff = np.median(x_diffs)
        gaps = np.sum(x_diffs > median_diff * 3)
        
        self.features['data_gaps'] = gaps
        logger.info(f"Data gaps detected: {gaps}")
        return gaps
    
    def detect_transit_characteristics(self) -> Dict[str, bool]:
        """
        Detect characteristics of planetary transits.
        
        Returns:
            dict: Transit characteristic flags
        """
        characteristics = {}
        
        baseline = np.quantile(self.y, 0.9)
        dip_indices = np.where(self.y < baseline * 0.95)[0]
        
        if len(dip_indices) > 0:
            dip_data = self.y[dip_indices]
            min_idx = np.argmin(dip_data)
            
            # U-shaped (flat bottom)
            bottom_std = np.std(dip_data[max(0, min_idx-2):min(len(dip_data), min_idx+3)])
            characteristics['u_shaped_transit'] = bottom_std < np.std(dip_data) * 0.1
            
            # Check for smooth ingress/egress
            left_side = dip_data[:min_idx]
            right_side = dip_data[min_idx:]
            
            left_smooth = np.mean(np.diff(left_side) ** 2) < 0.0001
            right_smooth = np.mean(np.diff(right_side) ** 2) < 0.0001
            characteristics['smooth_ingress_egress'] = left_smooth and right_smooth
            
            # Check symmetry
            if len(left_side) > 0 and len(right_side) > 0:
                left_slope = (dip_data[min_idx] - dip_data[0]) / (len(left_side) + 1)
                right_slope = (dip_data[-1] - dip_data[min_idx]) / (len(right_side) + 1)
                symmetry = 1.0 - abs(left_slope - right_slope) / max(abs(left_slope), abs(right_slope), 0.001)
                characteristics['symmetric'] = symmetry > 0.8
            
            characteristics['isolated_event'] = self.detect_single_dip()
        
        self.features.update(characteristics)
        return characteristics
    
    def get_all_features(self) -> Dict:
        """
        Get all detected features.
        
        Returns:
            dict: All features
        """
        return self.features