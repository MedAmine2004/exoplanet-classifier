"""Export reports in various formats"""

import csv
import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

from ..utils.logger import get_logger
from ..utils.constants import OUTPUT_DIR

logger = get_logger(__name__)

class BaseExporter:
    """
    Base class for exporters.
    """
    
    def __init__(self):
        self.timestamp = datetime.now()
    
    def get_default_filename(self, extension: str) -> str:
        """
        Generate default filename with timestamp.
        
        Args:
            extension: File extension
            
        Returns:
            str: Filename
        """
        return f"report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.{extension}"

class JSONExporter(BaseExporter):
    """
    Export reports as JSON.
    """
    
    def export(self, report_data: Dict, filename: Optional[str] = None) -> Optional[Path]:
        """
        Export report as JSON.
        
        Args:
            report_data: Report data dictionary
            filename: Output filename
            
        Returns:
            Path to exported file or None
        """
        try:
            if filename is None:
                filename = self.get_default_filename('json')
            
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            logger.info(f"JSON report exported to {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error exporting JSON: {str(e)}")
            return None

class CSVExporter(BaseExporter):
    """
    Export numerical data as CSV.
    """
    
    def export(self, x_data: list, y_data: list, smoothed_data: list = None,
               filename: Optional[str] = None) -> Optional[Path]:
        """
        Export light curve data as CSV.
        
        Args:
            x_data: X coordinates
            y_data: Y coordinates (raw)
            smoothed_data: Y coordinates (smoothed)
            filename: Output filename
            
        Returns:
            Path to exported file or None
        """
        try:
            if filename is None:
                filename = self.get_default_filename('csv')
            
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                if smoothed_data is not None:
                    writer.writerow(['X', 'Y_Raw', 'Y_Smoothed'])
                    for x, y, ys in zip(x_data, y_data, smoothed_data):
                        writer.writerow([x, y, ys])
                else:
                    writer.writerow(['X', 'Y'])
                    for x, y in zip(x_data, y_data):
                        writer.writerow([x, y])
            
            logger.info(f"CSV data exported to {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error exporting CSV: {str(e)}")
            return None

class TXTExporter(BaseExporter):
    """
    Export reports as plain text.
    """
    
    def export(self, report_summary: str, filename: Optional[str] = None) -> Optional[Path]:
        """
        Export report as plain text.
        
        Args:
            report_summary: Summary text
            filename: Output filename
            
        Returns:
            Path to exported file or None
        """
        try:
            if filename is None:
                filename = self.get_default_filename('txt')
            
            filepath = OUTPUT_DIR / filename
            
            with open(filepath, 'w') as f:
                f.write(report_summary)
            
            logger.info(f"TXT report exported to {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error exporting TXT: {str(e)}")
            return None

class PDFExporter(BaseExporter):
    """
    Export reports as PDF (requires reportlab).
    """
    
    def export(self, report_summary: str, image_path: str = None,
               filename: Optional[str] = None) -> Optional[Path]:
        """
        Export report as PDF.
        
        Args:
            report_summary: Summary text
            image_path: Path to image to include
            filename: Output filename
            
        Returns:
            Path to exported file or None
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            if filename is None:
                filename = self.get_default_filename('pdf')
            
            filepath = OUTPUT_DIR / filename
            
            # Create PDF
            doc = SimpleDocTemplate(str(filepath), pagesize=letter,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#0078d4',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Title
            elements.append(Paragraph("Exoplanet Light Curve Analysis Report", title_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Add image if provided
            if image_path and Path(image_path).exists():
                try:
                    img = Image(image_path, width=4*inch, height=3*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.3*inch))
                except Exception as e:
                    logger.warning(f"Could not add image to PDF: {str(e)}")
            
            # Add summary text
            for line in report_summary.split('\n'):
                if line.strip():
                    elements.append(Paragraph(line, styles['Normal']))
                else:
                    elements.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"PDF report exported to {filepath}")
            return filepath
        
        except ImportError:
            logger.error("reportlab not installed, cannot export PDF")
            return None
        except Exception as e:
            logger.error(f"Error exporting PDF: {str(e)}")
            return None