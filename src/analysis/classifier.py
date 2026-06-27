"""Machine learning based classifier"""

import numpy as np
from typing import Dict, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path

from ..utils.logger import get_logger
from ..utils.constants import CLASSES

logger = get_logger(__name__)

class Classifier:
    """
    Classify light curves into categories using features and optional ML.
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.class_weights = {
            'exoplanet': 0.0,
            'binary': 0.0,
            'variable': 0.0,
            'noise': 0.0,
            'insufficient': 0.0,
            'unknown': 0.0
        }
        self.reasoning = []
    
    def classify_from_features(self, features: Dict, metrics: Dict) -> Tuple[Dict[str, float], str]:
        """
        Classify light curve based on extracted features and metrics.
        
        Args:
            features: Detected features
            metrics: Signal metrics
            
        Returns:
            Tuple: (class_probabilities, primary_classification)
        """
        self.reasoning = []
        self.class_weights = {
            'exoplanet': 0.0,
            'binary': 0.0,
            'variable': 0.0,
            'noise': 0.0,
            'insufficient': 0.0,
            'unknown': 0.0
        }
        
        # Check for insufficient data
        if metrics.get('noise_level', 0) > metrics.get('std', 0.01) * 0.5:
            self.class_weights['insufficient'] += 0.4
            self.reasoning.append("High noise relative to signal")
        
        if metrics.get('dip_count', 0) == 0:
            self.class_weights['insufficient'] += 0.3
            self.reasoning.append("No clear transit/eclipse detected")
        
        # Check for noise
        if features.get('noise_dominated', False):
            self.class_weights['noise'] += 0.8
            self.reasoning.append("Signal is noise-dominated")
        
        # Check for eclipsing binary
        if features.get('multiple_dips', 0) >= 2:
            self.class_weights['binary'] += 0.3
            self.reasoning.append(f"Multiple dips detected ({features['multiple_dips']})")
            
            if features.get('periodic_dips', False):
                self.class_weights['binary'] += 0.2
                self.reasoning.append("Periodic dips suggest binary system")
            
            if features.get('v_shaped_eclipse', False):
                self.class_weights['binary'] += 0.4
                self.reasoning.append("V-shaped eclipse characteristic of binary star")
            
            if features.get('secondary_eclipse', False):
                self.class_weights['binary'] += 0.3
                self.reasoning.append("Secondary eclipse detected (binary signature)")
            
            if features.get('odd_even_difference', False):
                self.class_weights['binary'] += 0.2
                self.reasoning.append("Odd-even eclipse depth difference (binary indicator)")
        
        # Check for exoplanet
        if features.get('single_dip', False):
            self.class_weights['exoplanet'] += 0.3
            self.reasoning.append("Single, isolated transit detected")
            
            if features.get('u_shaped_transit', False):
                self.class_weights['exoplanet'] += 0.25
                self.reasoning.append("U-shaped transit with flat bottom")
            
            if features.get('smooth_ingress_egress', False):
                self.class_weights['exoplanet'] += 0.2
                self.reasoning.append("Smooth ingress and egress")
            
            if features.get('symmetric', False):
                self.class_weights['exoplanet'] += 0.15
                self.reasoning.append("Symmetric transit profile")
            
            if not features.get('secondary_eclipse', False):
                self.class_weights['exoplanet'] += 0.1
                self.reasoning.append("No secondary eclipse detected")
        
        # Check for variable star
        if features.get('variable_star_oscillations', False):
            self.class_weights['variable'] += 0.7
            self.reasoning.append("Variable star oscillations detected")
        
        if features.get('multiple_dips', 0) > 3:
            self.class_weights['variable'] += 0.2
            self.reasoning.append("Many dips suggest variable star")
        
        # Check for data quality issues
        if features.get('data_gaps', 0) > 0:
            self.class_weights['unknown'] += 0.15
            self.reasoning.append(f"Data gaps detected ({features['data_gaps']})")
        
        # Measure transit depth
        transit_depth = metrics.get('transit_properties', {}).get('dip_0', {}).get('depth', 0) if isinstance(metrics.get('transit_properties'), dict) else 0
        
        if transit_depth > 0:
            if transit_depth > 0.02:
                self.class_weights['exoplanet'] += 0.05
                self.reasoning.append(f"Deep transit ({transit_depth*100:.1f}%) suggests large planet")
            elif transit_depth < 0.001:
                self.class_weights['noise'] += 0.1
                self.reasoning.append(f"Very shallow dip ({transit_depth*100:.3f}%) might be noise")
        
        # Normalize weights
        total_weight = sum(self.class_weights.values())
        if total_weight > 0:
            for key in self.class_weights:
                self.class_weights[key] /= total_weight
        else:
            self.class_weights['unknown'] = 1.0
        
        # Determine primary classification
        primary = max(self.class_weights, key=self.class_weights.get)
        
        # Convert to probabilities
        probabilities = {
            CLASSES.get(key, key): self.class_weights[key]
            for key in self.class_weights
        }
        
        logger.info(f"Classification: {primary} with confidence {self.class_weights[primary]:.2%}")
        return probabilities, primary
    
    def generate_reasoning(self) -> str:
        """
        Generate human-readable explanation for classification.
        
        Returns:
            str: Reasoning text
        """
        if not self.reasoning:
            return "Classification reasoning unavailable."
        
        reasoning_text = "Classification reasoning:\n\n"
        for i, reason in enumerate(self.reasoning, 1):
            reasoning_text += f"{i}. {reason}\n"
        
        return reasoning_text
    
    def calculate_confidence(self, probabilities: Dict[str, float]) -> Tuple[float, str]:
        """
        Calculate overall confidence level.
        
        Args:
            probabilities: Classification probabilities
            
        Returns:
            Tuple: (confidence_score, confidence_level)
        """
        max_prob = max(probabilities.values())
        
        if max_prob >= 0.75:
            level = "High Confidence"
        elif max_prob >= 0.50:
            level = "Medium Confidence"
        else:
            level = "Low Confidence"
        
        return max_prob, level
    
    def get_recommendation(self, primary_class: str, confidence: float) -> str:
        """
        Generate final recommendation.
        
        Args:
            primary_class: Primary classification
            confidence: Confidence score
            
        Returns:
            str: Recommendation
        """
        if confidence < 0.5:
            return "⚠️ Uncertain – Human Review Recommended"
        
        if 'Exoplanet' in primary_class:
            return "✅ Likely Exoplanet Candidate (worth further inspection)"
        elif 'Binary' in primary_class:
            return "⭐ Likely Eclipsing Binary Star System"
        elif 'Variable' in primary_class:
            return "🌟 Likely Variable Star"
        elif 'Noise' in primary_class:
            return "❌ Likely Noise or Artifact"
        elif 'Insufficient' in primary_class:
            return "❓ Insufficient Data for Classification"
        else:
            return "❓ Unknown Classification"
    
    def get_reasoning_list(self) -> list:
        """
        Get list of reasoning steps.
        
        Returns:
            list: Reasoning steps
        """
        return self.reasoning