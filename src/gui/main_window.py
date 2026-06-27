"""Main application window"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional
import threading

from .styles import apply_theme, get_button_style, get_label_style
from .widgets import ProgressIndicator, ClassificationResult, InfoPanel
from ..utils.logger import get_logger
from ..utils.constants import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT

logger = get_logger(__name__)

class MainWindow(ctk.CTk):
    """
    Main application window for the Exoplanet Classifier.
    """
    
    def __init__(self):
        super().__init__()
        
        # Apply theme
        apply_theme()
        
        # Window configuration
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1200, 800)
        
        logger.info(f"Initializing {APP_NAME}")
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """
        Build the main user interface.
        """
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self._build_header(main_container)
        
        # Main content area with tabs
        self._build_content_area(main_container)
        
        # Status bar
        self._build_status_bar(main_container)
    
    def _build_header(self, parent):
        """
        Build header section.
        
        Args:
            parent: Parent widget
        """
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🌟 Exoplanet Light Curve Classifier",
            font=("Segoe UI", 20, "bold")
        )
        title_label.pack(side="left")
        
        version_label = ctk.CTkLabel(
            header_frame,
            text=f"v{APP_VERSION}",
            font=("Segoe UI", 10),
            text_color="#a0a0a0"
        )
        version_label.pack(side="right", padx=10)
    
    def _build_content_area(self, parent):
        """
        Build main content area with tabs.
        
        Args:
            parent: Parent widget
        """
        # Create tabview
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_input = self.tabview.add("Input")
        self.tab_analysis = self.tabview.add("Analysis")
        self.tab_results = self.tabview.add("Results")
        self.tab_export = self.tabview.add("Export")
        
        self._build_input_tab()
        self._build_analysis_tab()
        self._build_results_tab()
        self._build_export_tab()
    
    def _build_input_tab(self):
        """
        Build input tab for uploading/selecting light curves.
        """
        container = ctk.CTkFrame(self.tab_input)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Input method selection
        method_label = ctk.CTkLabel(
            container,
            text="Select Input Method:",
            font=("Segoe UI", 14, "bold")
        )
        method_label.pack(pady=10)
        
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=10)
        
        upload_btn = ctk.CTkButton(
            button_frame,
            text="📁 Upload Image",
            command=self._on_upload_image,
            **get_button_style(),
            width=200
        )
        upload_btn.pack(side="left", padx=5)
        
        url_btn = ctk.CTkButton(
            button_frame,
            text="🔗 Paste Image URL",
            command=self._on_paste_url,
            **get_button_style(),
            width=200
        )
        url_btn.pack(side="left", padx=5)
        
        zoo_btn = ctk.CTkButton(
            button_frame,
            text="🌐 Zooniverse Subject",
            command=self._on_paste_zooniverse,
            **get_button_style(),
            width=200
        )
        zoo_btn.pack(side="left", padx=5)
        
        # Divider
        divider = ctk.CTkFrame(container, height=2, fg_color="#404040")
        divider.pack(fill="x", pady=20)
        
        # URL/file input area
        input_label = ctk.CTkLabel(
            container,
            text="URL or File Path:",
            **get_label_style()
        )
        input_label.pack(anchor="w", pady=5)
        
        self.input_entry = ctk.CTkEntry(
            container,
            placeholder_text="Paste URL or file path here...",
            height=40
        )
        self.input_entry.pack(fill="x", pady=5)
        
        # Info panel
        self.info_panel = InfoPanel(container, title="Instructions")
        self.info_panel.pack(fill="both", expand=True, pady=10)
        self.info_panel.set_text(
            "Welcome to Exoplanet Light Curve Classifier!\n\n"
            "Choose one of three methods to analyze a light curve:\n\n"
            "1. 📁 Upload Image: Select a PNG, JPG, JPEG, or WEBP file from your computer\n\n"
            "2. 🔗 Paste Image URL: Provide a direct URL to a light curve image\n\n"
            "3. 🌐 Zooniverse Subject: Paste a Zooniverse subject page URL for automatic extraction\n\n"
            "The application will analyze the image, extract the light curve, and classify it."
        )
    
    def _build_analysis_tab(self):
        """
        Build analysis tab with visualization.
        """
        container = ctk.CTkFrame(self.tab_analysis)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="Analysis Visualization",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=10)
        
        # Placeholder for matplotlib figure
        self.analysis_frame = ctk.CTkFrame(container, fg_color="#2d2d2d")
        self.analysis_frame.pack(fill="both", expand=True, pady=10)
        
        placeholder = ctk.CTkLabel(
            self.analysis_frame,
            text="📊 Visualization will appear here",
            text_color="#a0a0a0",
            font=("Segoe UI", 12)
        )
        placeholder.pack(expand=True)
        
        # Analysis info
        self.analysis_info = InfoPanel(container, title="Analysis Details")
        self.analysis_info.pack(fill="x", pady=10, ipady=50)
        self.analysis_info.set_text("Analysis details will appear here...")
    
    def _build_results_tab(self):
        """
        Build results tab with classification scores.
        """
        container = ctk.CTkFrame(self.tab_results)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="Classification Results",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=10)
        
        # Classification results
        self.results_display = ClassificationResult(container)
        self.results_display.pack(fill="x", pady=10)
        
        # Confidence info
        confidence_frame = ctk.CTkFrame(container)
        confidence_frame.pack(fill="x", pady=10)
        
        conf_label = ctk.CTkLabel(
            confidence_frame,
            text="Overall Confidence: ",
            font=("Segoe UI", 12, "bold")
        )
        conf_label.pack(side="left", padx=5)
        
        self.confidence_label = ctk.CTkLabel(
            confidence_frame,
            text="--",
            font=("Segoe UI", 12, "bold"),
            text_color="#0078d4"
        )
        self.confidence_label.pack(side="left", padx=5)
        
        # Reasoning panel
        self.reasoning_panel = InfoPanel(container, title="Classification Reasoning")
        self.reasoning_panel.pack(fill="both", expand=True, pady=10)
        self.reasoning_panel.set_text("Reasoning will appear here...")
    
    def _build_export_tab(self):
        """
        Build export tab for saving results.
        """
        container = ctk.CTkFrame(self.tab_export)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="Export Results",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=10)
        
        export_frame = ctk.CTkFrame(container)
        export_frame.pack(fill="x", pady=20)
        
        export_formats = [
            ("📄 PDF", "pdf"),
            ("📊 CSV", "csv"),
            ("📋 JSON", "json"),
            ("📝 TXT", "txt")
        ]
        
        for label, fmt in export_formats:
            btn = ctk.CTkButton(
                export_frame,
                text=label,
                command=lambda f=fmt: self._on_export(f),
                **get_button_style(),
                width=150
            )
            btn.pack(side="left", padx=5)
        
        # Export info
        self.export_panel = InfoPanel(container, title="Export Information")
        self.export_panel.pack(fill="both", expand=True, pady=10)
        self.export_panel.set_text(
            "Click on any format button to export your analysis results.\n\n"
            "• PDF: Full report with visualizations\n"
            "• CSV: Numerical data in spreadsheet format\n"
            "• JSON: Structured data for programmatic use\n"
            "• TXT: Plain text summary"
        )
    
    def _build_status_bar(self, parent):
        """
        Build status bar.
        
        Args:
            parent: Parent widget
        """
        status_frame = ctk.CTkFrame(parent, height=50)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            text_color="#a0a0a0",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="left", padx=10)
        
        self.progress_bar = ProgressIndicator(status_frame, width=300, height=20)
        self.progress_bar.pack(side="right", padx=10)
    
    # Event handlers
    
    def _on_upload_image(self):
        """
        Handle upload image button click.
        """
        logger.info("Upload image button clicked")
        self.status_label.configure(text="Opening file browser...")
    
    def _on_paste_url(self):
        """
        Handle paste URL button click.
        """
        logger.info("Paste URL button clicked")
        self.status_label.configure(text="Ready to paste URL")
    
    def _on_paste_zooniverse(self):
        """
        Handle paste Zooniverse URL button click.
        """
        logger.info("Paste Zooniverse URL button clicked")
        self.status_label.configure(text="Ready to paste Zooniverse URL")
    
    def _on_export(self, format_type: str):
        """
        Handle export button click.
        
        Args:
            format_type: Export format (pdf, csv, json, txt)
        """
        logger.info(f"Export {format_type.upper()} button clicked")
        self.status_label.configure(text=f"Exporting as {format_type.upper()}...")
    
    def update_status(self, message: str):
        """
        Update status bar message.
        
        Args:
            message: Status message
        """
        self.status_label.configure(text=message)
        self.update()
    
    def update_progress(self, value: float, label: str = ""):
        """
        Update progress bar.
        
        Args:
            value: Progress value (0-1)
            label: Optional label
        """
        self.progress_bar.update_progress(value, label)
        self.update()