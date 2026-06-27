"""Signal analysis and feature measurement"""

import numpy as np
from typing import Dict, Tuple, Optional
from scipy.signal import find_peaks, argrelextrema
from scipy.stats import skew, kurtosis

from ..utils.logger import get_logger
from ..utils.constants import NOISE_THRESHOLD, TRANSIT_DEPTH_THRESHOLD

logger = get_logger(__name__)

class SignalAnalyzer:
    """
    Analyze light curve signals and extract features.
    """
    
    def __init__(self, x_data: np.ndarray, y_data: np.ndarray):
        self.x = x_data
        self.y = y_data
        self.metrics = {}
        self.baseline = None
        self.residuals = None
    
    def compute_basic_stats(self) -> Dict[str, float]:
        """
        Compute basic statistical measures.
        
        Returns:
            dict: Statistics
        """
        stats = {
            'mean': np.mean(self.y),
            'median': np.median(self.y),
            'std': np.std(self.y),
            'min': np.min(self.y),
            'max': np.max(self.y),
            'range': np.max(self.y) - np.min(self.y),
            'var': np.var(self.y),
            'skewness': float(skew(self.y)),
            'kurtosis': float(kurtosis(self.y)),
        }
        
        self.metrics.update(stats)
        logger.info(f"Basic stats computed: mean={stats['mean']:.4f}, std={stats['std']:.4f}")
        return stats
    
    def estimate_noise_level(self) -> float:
        """
        Estimate noise level in the signal.
        
        Returns:
            float: Estimated noise standard deviation
        """
        # Use median absolute deviation (MAD) for robust noise estimation
        med = np.median(self.y)
        mad = np.median(np.abs(self.y - med))
        noise = 1.4826 * mad  # Conversion factor for normal distribution
        
        self.metrics['noise_level'] = noise
        logger.info(f"Estimated noise level: {noise:.6f}")
        return noise
    
    def calculate_snr(self) -> float:
        """
        Calculate signal-to-noise ratio.
        
        Returns:
            float: SNR in dB
        """
        noise = self.estimate_noise_level()
        signal_power = np.var(self.y)
        
        if noise > 0:
            snr_linear = signal_power / (noise ** 2)
            snr_db = 10 * np.log10(snr_linear)
        else:
            snr_db = np.inf
        
        self.metrics['snr_db'] = snr_db
        logger.info(f"SNR: {snr_db:.2f} dB")
        return snr_db
    
    def detect_baseline(self, method: str = 'quantile') -> np.ndarray:
        """
        Estimate the baseline (out-of-transit) level.
        
        Args:
            method: 'quantile' or 'percentile'
            
        Returns:
            np.ndarray: Baseline curve
        """
        if method == 'quantile':
            # Use high quantile (out-of-transit data)
            baseline_value = np.quantile(self.y, 0.9)
            self.baseline = np.ones_like(self.y) * baseline_value
        else:
            # Use percentile method
            self.baseline = np.percentile(self.y, 95)
            self.baseline = np.ones_like(self.y) * self.baseline
        
        logger.info(f"Baseline detected: {np.mean(self.baseline):.6f}")
        return self.baseline
    
    def detect_dips(self, height_threshold: float = 0.01, 
                    min_width: int = 3, max_width: int = 100) -> Dict:
        """
        Detect dips (transits/eclipses) in the light curve.
        
        Args:
            height_threshold: Minimum dip depth
            min_width: Minimum dip width (in points)
            max_width: Maximum dip width
            
        Returns:
            dict: Dip properties
        """
        # Invert signal for peak finding (find dips as peaks)
        inverted = self.detect_baseline() - self.y
        
        # Find peaks in inverted signal
        peaks, properties = find_peaks(
            inverted,
            height=height_threshold,
            width=(min_width, max_width),
            prominence=0.005
        )
        
        dips = {
            'count': len(peaks),
            'indices': peaks,
            'depths': properties.get('peak_heights', []),
            'widths': properties.get('widths', []),
            'prominences': properties.get('prominences', [])
        }
        
        self.metrics['dip_count'] = len(peaks)
        logger.info(f"Detected {len(peaks)} dips")
        return dips
    
    def measure_transit_properties(self, dip_indices: np.ndarray) -> Dict:
        """
        Measure properties of detected transits.
        
        Args:
            dip_indices: Indices of dip centers
            
        Returns:
            dict: Transit properties
        """
        properties = {}
        
        for i, idx in enumerate(dip_indices):
            dip_dict = {}
            
            # Find dip boundaries (where curve returns to baseline)
            baseline = np.quantile(self.y, 0.9)
            depth = baseline - self.y[idx]
            dip_dict['depth'] = depth
            
            # Find ingress and egress
            left_idx = idx
            while left_idx > 0 and self.y[left_idx] < baseline * 0.95:
                left_idx -= 1
            
            right_idx = idx
            while right_idx < len(self.y) - 1 and self.y[right_idx] < baseline * 0.95:
                right_idx += 1
            
            duration = right_idx - left_idx
            dip_dict['duration'] = duration
            dip_dict['ingress_idx'] = left_idx
            dip_dict['egress_idx'] = right_idx
            
            # Calculate slopes
            if left_idx < idx:
                ingress_slope = depth / (idx - left_idx)
                dip_dict['ingress_slope'] = ingress_slope
            
            if right_idx > idx:
                egress_slope = depth / (right_idx - idx)
                dip_dict['egress_slope'] = egress_slope
            
            # Measure symmetry
            if 'ingress_slope' in dip_dict and 'egress_slope' in dip_dict:
                symmetry = 1.0 - abs(dip_dict['ingress_slope'] - dip_dict['egress_slope']) / max(dip_dict['ingress_slope'], dip_dict['egress_slope'])
                dip_dict['symmetry'] = symmetry
            
            # Check for flat bottom
            dip_bottom = self.y[left_idx:right_idx]
            flat_bottom_score = np.std(dip_bottom) / np.std(self.y)
            dip_dict['flat_bottom_score'] = flat_bottom_score
            
            properties[f'dip_{i}'] = dip_dict
        
        self.metrics['transit_properties'] = properties
        logger.info(f"Measured properties for {len(dip_indices)} transits")
        return properties
    
    def check_baseline_stability(self) -> float:
        """
        Check stability of the baseline (out-of-transit regions).
        
        Returns:
            float: Baseline stability score (0-1, higher is more stable)
        """
        baseline = np.quantile(self.y, 0.95)
        out_of_transit = self.y[self.y > baseline * 0.90]
        
        stability = 1.0 / (1.0 + np.std(out_of_transit) / baseline)
        
        self.metrics['baseline_stability'] = stability
        logger.info(f"Baseline stability: {stability:.4f}")
        return stability
    
    def detect_periodic_spacing(self) -> Optional[float]:
        """
        Detect periodic spacing between transits (if multiple).
        
        Returns:
            float: Period in time units, or None
        """
        dips = self.detect_dips()
        if dips['count'] < 2:
            return None
        
        indices = dips['indices']
        spacings = np.diff(indices)
        
        if len(spacings) > 0:
            period = np.mean(spacings)
            period_std = np.std(spacings)
            
            self.metrics['period'] = period
            self.metrics['period_uncertainty'] = period_std
            logger.info(f"Detected period: {period:.2f} ± {period_std:.2f}")
            return period
        
        return None
    
    def detect_outliers(self, threshold: float = 3.0) -> np.ndarray:
        """
        Detect outliers using z-score method.
        
        Args:
            threshold: Z-score threshold
            
        Returns:
            np.ndarray: Boolean mask of outliers
        """
        z_scores = np.abs((self.y - np.mean(self.y)) / np.std(self.y))
        outliers = z_scores > threshold
        
        self.metrics['outlier_count'] = np.sum(outliers)
        logger.info(f"Detected {np.sum(outliers)} outliers")
        return outliers
    
    def check_saturated_regions(self, threshold_percentile: float = 99) -> np.ndarray:
        """
        Detect saturated (clipped) regions.
        
        Returns:
            np.ndarray: Boolean mask of saturated points
        """
        threshold = np.percentile(self.y, threshold_percentile)
        saturated = self.y > threshold
        
        self.metrics['saturated_count'] = np.sum(saturated)
        logger.info(f"Detected {np.sum(saturated)} saturated points")
        return saturated
    
    def get_all_metrics(self) -> Dict:
        """
        Get all computed metrics.
        
        Returns:
            dict: All metrics
        """
        return self.metrics