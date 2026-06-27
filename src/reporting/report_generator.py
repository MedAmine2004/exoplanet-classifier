"""Generate comprehensive analysis reports"""

from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
import json

from ..utils.logger import get_logger
from ..utils.constants import OUTPUT_DIR, CLASSES

logger = get_logger(__name__)

class ReportGenerator:
    """
    Generate comprehensive analysis reports.
    """
    
    def __init__(self):
        self.report_data = {}
        self.timestamp = datetime.now()
    
    def create_report(self, image_path: str, analysis_results: Dict, 
                     classification: Dict, confidence: float, reasoning: list) -> Dict:
        """
        Create comprehensive report from analysis results.
        
        Args:
            image_path: Path to original image
            analysis_results: Signal analysis metrics
            classification: Classification probabilities
            confidence: Confidence score
            reasoning: Reasoning steps
            
        Returns:
            dict: Report data
        """
        self.report_data = {
            'timestamp': self.timestamp.isoformat(),
            'image_path': str(image_path),
            'analysis': {
                'basic_stats': analysis_results.get('basic_stats', {}),
                'noise_level': analysis_results.get('noise_level', None),
                'snr_db': analysis_results.get('snr_db', None),
                'dip_count': analysis_results.get('dip_count', 0),
                'baseline_stability': analysis_results.get('baseline_stability', None),
                'transit_properties': analysis_results.get('transit_properties', {}),
                'period': analysis_results.get('period', None),
                'outlier_count': analysis_results.get('outlier_count', 0),
                'saturated_count': analysis_results.get('saturated_count', 0),
            },
            'classification': classification,
            'confidence': confidence,
            'reasoning': reasoning,
        }
        
        logger.info(f"Report created at {self.timestamp}")
        return self.report_data
    
    def get_summary(self) -> str:
        """
        Generate text summary of report.
        
        Returns:
            str: Summary text
        """
        if not self.report_data:
            return "No report data available."
        
        summary = f"""Exoplanet Light Curve Classification Report
{'='*60}

Generated: {self.report_data['timestamp']}
Image: {self.report_data['image_path']}

ANALYSIS SUMMARY
{'-'*60}

Basic Statistics:
  Mean Flux: {self.report_data['analysis']['basic_stats'].get('mean', 'N/A')}
  Median Flux: {self.report_data['analysis']['basic_stats'].get('median', 'N/A')}
  Std Dev: {self.report_data['analysis']['basic_stats'].get('std', 'N/A')}

Signal Quality:
  Noise Level: {self.report_data['analysis']['noise_level']}
  SNR (dB): {self.report_data['analysis']['snr_db']}
  Baseline Stability: {self.report_data['analysis']['baseline_stability']}

Features Detected:
  Dips/Transits: {self.report_data['analysis']['dip_count']}
  Outliers: {self.report_data['analysis']['outlier_count']}
  Saturated Points: {self.report_data['analysis']['saturated_count']}

CLASSIFICATION
{'-'*60}

Class Probabilities:
"""
        
        for class_name, probability in self.report_data['classification'].items():
            summary += f"  {class_name}: {probability*100:.1f}%\n"
        
        summary += f"\nOverall Confidence: {self.report_data['confidence']*100:.1f}%\n"
        
        summary += f"\nREASONING\n{'-'*60}\n"
        for i, reason in enumerate(self.report_data['reasoning'], 1):
            summary += f"{i}. {reason}\n"
        
        return summary
    
    def export_json(self, filename: Optional[str] = None) -> Optional[Path]:
        """
        Export report as JSON.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to exported file or None
        """
        try:
            if not self.report_data:
                logger.warning("No report data to export")
                return None
            
            if filename is None:
                filename = f"report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, 'w') as f:
                json.dump(self.report_data, f, indent=2)
            
            logger.info(f"Report exported to {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error exporting JSON report: {str(e)}")
            return None
    
    def get_report_data(self) -> Dict:
        """
        Get raw report data.
        
        Returns:
            dict: Report data
        """
        return self.report_data