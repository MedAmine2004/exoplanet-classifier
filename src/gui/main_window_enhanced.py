"""Enhanced main window with full integration"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

from .styles import apply_theme, get_button_style, get_label_style
from .widgets import ProgressIndicator, ClassificationResult, InfoPanel, DragDropFrame
from ..utils.logger import get_logger
from ..utils.constants import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, SUPPORTED_FORMATS

logger = get_logger(__name__)

class EnhancedMainWindow(ctk.CTk):
    """
    Enhanced main application window with full integration.
    """
    
    def __init__(self):
        super().__init__()
        
        # Apply theme
        apply_theme()
        
        # Window configuration
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1200, 800)
        
        # App reference (set by controller)
        self.app = None
        
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
        """
        # Create tabview
        self.tabview = ctk.CTkTabview(parent)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_input = self.tabview.add("📥 Input")
        self.tab_analysis = self.tabview.add("📊 Analysis")
        self.tab_results = self.tabview.add("📈 Results")
        self.tab_export = self.tabview.add("💾 Export")
        
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
        
        # Title
        title = ctk.CTkLabel(
            container,
            text="Load Light Curve Data",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=10)
        
        # Drag and drop area
        self.drag_drop_frame = DragDropFrame(
            container,
            callback=self._on_drop_files,
            fg_color="#2d2d2d",
            border_width=2,
            border_color="#0078d4",
            corner_radius=10
        )
        self.drag_drop_frame.pack(fill="both", expand=True, pady=20, padx=10)
        
        drag_label = ctk.CTkLabel(
            self.drag_drop_frame,
            text="🎯 Drag & Drop Image Here\nor Use Buttons Below",
            font=("Segoe UI", 14),
            text_color="#a0a0a0"
        )
        drag_label.pack(expand=True)
        
        # Divider
        divider = ctk.CTkFrame(container, height=2, fg_color="#404040")
        divider.pack(fill="x", pady=10)
        
        # Input method selection
        method_label = ctk.CTkLabel(
            container,
            text="Or Select Input Method:",
            font=("Segoe UI", 12, "bold")
        )
        method_label.pack(pady=5)
        
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
        divider2 = ctk.CTkFrame(container, height=2, fg_color="#404040")
        divider2.pack(fill="x", pady=10)
        
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
            height=40,
            font=("Segoe UI", 11)
        )
        self.input_entry.pack(fill="x", pady=5)
        
        # Action button
        action_btn = ctk.CTkButton(
            container,
            text="▶ Analyze",
            command=self._on_analyze_click,
            **get_button_style(),
            fg_color="#28a745",
            hover_color="#218838"
        )
        action_btn.pack(pady=10, fill="x")
        
        # Info panel
        self.info_panel = InfoPanel(container, title="Instructions")
        self.info_panel.pack(fill="both", expand=True, pady=10, ipady=20)
        self.info_panel.set_text(
            "🎓 Welcome to Exoplanet Light Curve Classifier!\n\n"
            "Choose one of three methods to analyze a light curve:\n\n"
            "📁 Upload Image: Select a PNG, JPG, JPEG, or WEBP file from your computer\n\n"
            "🔗 Paste Image URL: Provide a direct URL to a light curve image\n\n"
            "🌐 Zooniverse Subject: Paste a Zooniverse subject page URL for automatic extraction\n\n"
            "The application will automatically:\n"
            "  • Extract the light curve from the image\n"
            "  • Analyze signal properties and features\n"
            "  • Classify into exoplanet, binary, variable star, or noise\n"
            "  • Provide confidence scores and reasoning"
        )
    
    def _build_analysis_tab(self):
        """
        Build analysis tab with visualization.
        """
        container = ctk.CTkFrame(self.tab_analysis)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="📊 Analysis Visualization",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=10)
        
        # Canvas for matplotlib figure
        self.analysis_frame = ctk.CTkFrame(container, fg_color="#1e1e1e")
        self.analysis_frame.pack(fill="both", expand=True, pady=10)
        
        placeholder = ctk.CTkLabel(
            self.analysis_frame,
            text="📈 Visualization will appear here after analysis",
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
            text="📈 Classification Results",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=10)
        
        # Recommendation frame
        rec_frame = ctk.CTkFrame(container, fg_color="#2d2d2d", corner_radius=10)
        rec_frame.pack(fill="x", pady=10, padx=10)
        
        rec_label = ctk.CTkLabel(
            rec_frame,
            text="Recommendation:",
            font=("Segoe UI", 12, "bold")
        )
        rec_label.pack(side="left", padx=15, pady=10)
        
        self.recommendation_label = ctk.CTkLabel(
            rec_frame,
            text="Pending analysis...",
            font=("Segoe UI", 11),
            text_color="#0078d4"
        )
        self.recommendation_label.pack(side="left", padx=10, pady=10)
        
        # Classification results
        self.results_display = ClassificationResult(container, fg_color="transparent")
        self.results_display.pack(fill="x", pady=10)
        
        # Confidence info
        confidence_frame = ctk.CTkFrame(container, fg_color="#2d2d2d", corner_radius=10)
        confidence_frame.pack(fill="x", pady=10, padx=10)
        
        conf_label = ctk.CTkLabel(
            confidence_frame,
            text="Overall Confidence: ",
            font=("Segoe UI", 12, "bold")
        )
        conf_label.pack(side="left", padx=15, pady=10)
        
        self.confidence_label = ctk.CTkLabel(
            confidence_frame,
            text="-- ",
            font=("Segoe UI", 12, "bold"),
            text_color="#0078d4"
        )
        self.confidence_label.pack(side="left", padx=5, pady=10)
        
        self.confidence_level_label = ctk.CTkLabel(
            confidence_frame,
            text="(Pending)",
            font=("Segoe UI", 11),
            text_color="#a0a0a0"
        )
        self.confidence_level_label.pack(side="left", padx=5, pady=10)
        
        # Reasoning panel
        self.reasoning_panel = InfoPanel(container, title="Classification Reasoning")
        self.reasoning_panel.pack(fill="both", expand=True, pady=10)
        self.reasoning_panel.set_text("Reasoning will appear here after analysis...")
    
    def _build_export_tab(self):
        """
        Build export tab for saving results.
        """
        container = ctk.CTkFrame(self.tab_export)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            container,
            text="💾 Export Results",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=10)
        
        export_frame = ctk.CTkFrame(container)
        export_frame.pack(fill="x", pady=20, padx=10)
        
        export_formats = [
            ("📄 PDF Report", "pdf"),
            ("📊 CSV Data", "csv"),
            ("📋 JSON", "json"),
            ("📝 TXT Summary", "txt")
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
            "📥 Export your analysis results in multiple formats:\n\n"
            "📄 PDF: Full report with visualizations and analysis\n"
            "📊 CSV: Numerical light curve data for spreadsheets\n"
            "📋 JSON: Structured data for programmatic use\n"
            "📝 TXT: Plain text summary of the analysis\n\n"
            "💾 All exports are saved to the 'output/' directory."
        )
    
    def _build_status_bar(self, parent):
        """
        Build status bar.
        """
        status_frame = ctk.CTkFrame(parent, height=50, fg_color="#2d2d2d", corner_radius=5)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="✓ Ready",
            text_color="#28a745",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="left", padx=15, pady=10)
        
        self.progress_bar = ProgressIndicator(status_frame, width=400, height=20)
        self.progress_bar.pack(side="right", padx=15, pady=10)
    
    # Event handlers
    
    def _on_drop_files(self, files: list):
        """
        Handle dropped files.
        """
        if files:
            file_path = files[0]
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file_path)
            self._on_analyze_click()
    
    def _on_upload_image(self):
        """
        Handle upload image button click.
        """
        logger.info("Upload image button clicked")
        file_types = [("Image files", " ".join(f"*{fmt}" for fmt in SUPPORTED_FORMATS))]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file_path)
            self._on_analyze_click()
    
    def _on_paste_url(self):
        """
        Handle paste URL button click.
        """
        logger.info("Paste URL button clicked")
        self.input_entry.delete(0, "end")
        self.input_entry.focus()
        self.update_status("📋 Ready to paste image URL")
    
    def _on_paste_zooniverse(self):
        """
        Handle paste Zooniverse URL button click.
        """
        logger.info("Paste Zooniverse URL button clicked")
        self.input_entry.delete(0, "end")
        self.input_entry.focus()
        self.update_status("📋 Ready to paste Zooniverse subject URL")
    
    def _on_analyze_click(self):
        """
        Handle analyze button click.
        """
        input_value = self.input_entry.get().strip()
        
        if not input_value:
            messagebox.showwarning("Input Required", "Please provide an image file or URL")
            return
        
        if not self.app:
            messagebox.showerror("Error", "Application not initialized")
            return
        
        # Check if it's a file path or URL
        if Path(input_value).exists():
            # Local file
            thread = threading.Thread(target=self._analyze_file, args=(input_value,))
            thread.daemon = True
            thread.start()
        elif input_value.startswith('http'):
            if 'zooniverse' in input_value.lower():
                # Zooniverse URL
                thread = threading.Thread(target=self._analyze_zooniverse, args=(input_value,))
            else:
                # Image URL
                thread = threading.Thread(target=self._analyze_url, args=(input_value,))
            thread.daemon = True
            thread.start()
        else:
            messagebox.showerror("Invalid Input", "Please provide a valid file path or URL")
    
    def _analyze_file(self, file_path: str):
        """
        Analyze local file.
        """
        if not self.app.load_image(file_path):
            self.update_status("❌ Failed to load image")
            return
        
        if not self.app.analyze_image():
            self.update_status("❌ Analysis failed")
            return
        
        self._update_results_display()
    
    def _analyze_url(self, url: str):
        """
        Analyze image from URL.
        """
        if not self.app.download_and_analyze(url):
            self.update_status("❌ Failed to download and analyze image")
            return
        
        if not self.app.analyze_image():
            self.update_status("❌ Analysis failed")
            return
        
        self._update_results_display()
    
    def _analyze_zooniverse(self, url: str):
        """
        Analyze image from Zooniverse.
        """
        if not self.app.download_from_zooniverse(url):
            self.update_status("❌ Failed to extract and analyze from Zooniverse")
            return
        
        if not self.app.analyze_image():
            self.update_status("❌ Analysis failed")
            return
        
        self._update_results_display()
    
    def _update_results_display(self):
        """
        Update results display after analysis.
        """
        # Update classification results
        self.results_display.display_results(self.app.classification)
        
        # Update confidence
        conf_text = f"{self.app.confidence*100:.1f}%"
        self.confidence_label.configure(text=conf_text)
        
        # Determine confidence level
        if self.app.confidence >= 0.75:
            conf_level = "(High Confidence)"
            color = "#28a745"
        elif self.app.confidence >= 0.50:
            conf_level = "(Medium Confidence)"
            color = "#ffc107"
        else:
            conf_level = "(Low Confidence)"
            color = "#dc3545"
        
        self.confidence_level_label.configure(text=conf_level, text_color=color)
        
        # Update recommendation
        primary_class = max(self.app.classification, key=self.app.classification.get)
        recommendation = self.app.classifier.get_recommendation(primary_class, self.app.confidence)
        self.recommendation_label.configure(text=recommendation)
        
        # Update reasoning
        reasoning_text = self.app.classifier.generate_reasoning()
        self.reasoning_panel.set_text(reasoning_text)
        
        # Update status
        self.update_status(f"✓ Analysis complete: {primary_class}")
    
    def _on_export(self, format_type: str):
        """
        Handle export button click.
        """
        if not self.app or not self.app.classification:
            messagebox.showwarning("No Analysis", "Please analyze an image first")
            return
        
        thread = threading.Thread(target=self.app.export_report, args=(format_type,))
        thread.daemon = True
        thread.start()
    
    def update_status(self, message: str):
        """
        Update status bar message.
        """
        self.status_label.configure(text=message)
        self.update()
    
    def update_progress(self, value: float, label: str = ""):
        """
        Update progress bar.
        """
        self.progress_bar.update_progress(value, label)
        self.update()