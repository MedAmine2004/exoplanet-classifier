"""Application integration module"""

from src.gui.main_window_enhanced import EnhancedMainWindow
from src.processors.image_processor import ImageProcessor
from src.processors.curve_extractor import CurveExtractor
from src.processors.downloader import Downloader
from src.analysis.signal_analyzer import SignalAnalyzer
from src.analysis.feature_detector import FeatureDetector
from src.analysis.classifier import Classifier
from src.reporting.report_generator import ReportGenerator
from src.reporting.exporters import JSONExporter, CSVExporter, TXTExporter, PDFExporter
from src.utils.logger import get_logger
from src.utils.constants import APP_NAME, APP_VERSION

logger = get_logger(__name__)

class ExoplanetClassifier:
    """
    Main application controller integrating all components.
    """
    
    def __init__(self):
        """Initialize the application."""
        logger.info(f"Initializing {APP_NAME} v{APP_VERSION}")
        
        # Initialize components
        self.image_processor = ImageProcessor()
        self.curve_extractor = CurveExtractor()
        self.signal_analyzer = None
        self.feature_detector = None
        self.classifier = Classifier()
        self.report_generator = ReportGenerator()
        
        # Current analysis state
        self.current_image_path = None
        self.analysis_results = {}
        self.classification = {}
        self.confidence = 0.0
        
        # Create GUI
        self.window = EnhancedMainWindow()
        self.window.app = self
    
    def load_image(self, image_path: str) -> bool:
        """Load and preprocess image."""
        self.current_image_path = image_path
        self.window.update_status("📂 Loading image...")
        self.window.update_progress(0.1, "Loading")
        
        if not self.image_processor.load_image(image_path):
            self.window.update_status("❌ Failed to load image")
            return False
        
        self.window.update_progress(0.2, "Preprocessing")
        if not self.image_processor.preprocess_pipeline():
            self.window.update_status("❌ Preprocessing failed")
            return False
        
        self.window.update_progress(0.4, "Detecting graph")
        self.image_processor.detect_graph_region()
        
        self.window.update_status("✓ Image loaded")
        self.window.update_progress(0.5, "Ready")
        return True
    
    def analyze_image(self, x_range=(0, 1), y_range=(0.95, 1.05)) -> bool:
        """Perform complete analysis."""
        try:
            self.window.update_status("🔍 Extracting curve...")
            self.window.update_progress(0.5, "Extraction")
            
            image = self.image_processor.get_processed_image()
            if image is None:
                return False
            
            if not self.curve_extractor.extract_curve(image):
                self.window.update_status("❌ Curve extraction failed")
                return False
            
            self.curve_extractor.calibrate_axes(image, x_range, y_range)
            if not self.curve_extractor.reconstruct_light_curve():
                return False
            
            self.window.update_progress(0.65, "Smoothing")
            self.curve_extractor.smooth_curve()
            
            x_data, y_data = self.curve_extractor.get_raw_curve()
            
            self.window.update_status("📊 Analyzing signal...")
            self.window.update_progress(0.7, "Analysis")
            
            self.signal_analyzer = SignalAnalyzer(x_data, y_data)
            self.signal_analyzer.compute_basic_stats()
            self.signal_analyzer.estimate_noise_level()
            self.signal_analyzer.calculate_snr()
            self.signal_analyzer.detect_baseline()
            
            dips = self.signal_analyzer.detect_dips()
            if dips['count'] > 0:
                self.signal_analyzer.measure_transit_properties(dips['indices'])
            
            self.signal_analyzer.check_baseline_stability()
            self.signal_analyzer.detect_periodic_spacing()
            self.signal_analyzer.detect_outliers()
            self.signal_analyzer.check_saturated_regions()
            
            self.analysis_results = self.signal_analyzer.get_all_metrics()
            
            self.window.update_status("🔎 Detecting features...")
            self.window.update_progress(0.8, "Features")
            
            self.feature_detector = FeatureDetector(y_data, x_data)
            self.feature_detector.detect_single_dip()
            self.feature_detector.detect_multiple_dips()
            self.feature_detector.detect_periodic_dips()
            self.feature_detector.detect_eclipsing_binary_signature()
            self.feature_detector.detect_secondary_eclipse()
            self.feature_detector.detect_odd_even_difference()
            self.feature_detector.detect_variable_star_oscillations()
            self.feature_detector.detect_noise(self.analysis_results.get('noise_level', 0))
            self.feature_detector.detect_data_gaps()
            self.feature_detector.detect_transit_characteristics()
            
            features = self.feature_detector.get_all_features()
            
            self.window.update_status("🤖 Classifying...")
            self.window.update_progress(0.9, "Classification")
            
            self.classification, primary = self.classifier.classify_from_features(features, self.analysis_results)
            self.confidence, _ = self.classifier.calculate_confidence(self.classification)
            
            self.window.update_status(f"✓ Complete: {primary}")
            self.window.update_progress(1.0, "Done")
            
            logger.info("Analysis complete")
            return True
        
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            self.window.update_status(f"❌ Error: {str(e)}")
            return False
    
    def download_and_analyze(self, url: str) -> bool:
        """Download and analyze image from URL."""
        self.window.update_status("⬇️ Downloading image...")
        self.window.update_progress(0.1, "Download")
        
        image = Downloader.download_image(url)
        if image is None:
            self.window.update_status("❌ Download failed")
            return False
        
        temp_path = Downloader.save_image_temp(image)
        return self.load_image(str(temp_path)) if temp_path else False
    
    def download_from_zooniverse(self, zooniverse_url: str) -> bool:
        """Extract and analyze from Zooniverse URL."""
        self.window.update_status("🌐 Accessing Zooniverse...")
        self.window.update_progress(0.1, "Fetch")
        
        image_url = Downloader.extract_zooniverse_image(zooniverse_url)
        return self.download_and_analyze(image_url) if image_url else False
    
    def export_report(self, format_type: str) -> bool:
        """Export analysis report."""
        try:
            self.window.update_status(f"💾 Exporting {format_type.upper()}...")
            
            self.report_generator.create_report(
                self.current_image_path,
                self.analysis_results,
                self.classification,
                self.confidence,
                self.classifier.get_reasoning_list()
            )
            
            if format_type == 'json':
                exporter = JSONExporter()
                result = exporter.export(self.report_generator.get_report_data())
            elif format_type == 'csv':
                exporter = CSVExporter()
                x_data, y_data = self.curve_extractor.get_raw_curve()
                _, y_smooth = self.curve_extractor.get_smoothed_curve()
                result = exporter.export(x_data, y_data, y_smooth)
            elif format_type == 'txt':
                exporter = TXTExporter()
                summary = self.report_generator.get_summary()
                result = exporter.export(summary)
            elif format_type == 'pdf':
                exporter = PDFExporter()
                summary = self.report_generator.get_summary()
                result = exporter.export(summary, self.current_image_path)
            else:
                return False
            
            if result:
                self.window.update_status(f"✓ Exported to {result.name}")
                return True
            
            self.window.update_status("❌ Export failed")
            return False
        
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            self.window.update_status(f"❌ Export error")
            return False
    
    def run(self):
        """Start the application."""
        logger.info(f"Starting {APP_NAME}")
        self.window.mainloop()

def main():
    """Main entry point."""
    app = ExoplanetClassifier()
    app.run()

if __name__ == "__main__":
    main()