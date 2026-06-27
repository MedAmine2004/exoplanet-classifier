"""Custom widgets for the application"""

import customtkinter as ctk
from typing import Callable, Optional
from ..utils.constants import COLOR_ACCENT, COLOR_TEXT_DIM

class ProgressIndicator(ctk.CTkProgressBar):
    """
    Custom progress bar with label.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.label = ctk.CTkLabel(master, text="0%", text_color=COLOR_TEXT_DIM)
    
    def update_progress(self, value: float, label: str = ""):
        """
        Update progress bar and label.
        
        Args:
            value: Progress value (0-1)
            label: Optional label text
        """
        self.set(value)
        if label:
            self.label.configure(text=label)
        else:
            self.label.configure(text=f"{int(value * 100)}%")

class ClassificationResult(ctk.CTkFrame):
    """
    Display classification results with confidence bars.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.results_widgets = {}
    
    def display_results(self, results: dict):
        """
        Display classification results.
        
        Args:
            results: Dictionary with class names and probabilities
        """
        for widget in self.results_widgets.values():
            widget.destroy()
        self.results_widgets.clear()
        
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        
        for idx, (class_name, probability) in enumerate(sorted_results):
            frame = ctk.CTkFrame(self)
            frame.pack(fill="x", padx=10, pady=5)
            
            label = ctk.CTkLabel(frame, text=f"{class_name}", width=150, anchor="w")
            label.pack(side="left", padx=5)
            
            bar = ctk.CTkProgressBar(frame, value=probability)
            bar.pack(side="left", fill="x", expand=True, padx=5)
            
            percent_label = ctk.CTkLabel(frame, text=f"{probability*100:.1f}%", width=50)
            percent_label.pack(side="left", padx=5)
            
            self.results_widgets[class_name] = frame

class DragDropFrame(ctk.CTkFrame):
    """
    Frame that accepts drag and drop files.
    """
    def __init__(self, master, callback: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.callback = callback
        self.drop_target_register()
    
    def drop_target_register(self):
        """
        Register this frame as a drop target.
        """
        try:
            from tkinterdnd2 import DND_FILES, DND_TEXT
            self.drop_target_register(DND_FILES, DND_TEXT)
            self.dnd_bind('<<Drop>>', self._on_drop)
        except ImportError:
            # tkinterdnd2 not available, skip drag-drop support
            pass
    
    def _on_drop(self, event):
        """
        Handle drop event.
        """
        if self.callback:
            files = self.parse_dnd_files(event.data)
            self.callback(files)
    
    @staticmethod
    def parse_dnd_files(data: str):
        """
        Parse dropped files from DND data.
        
        Args:
            data: DND event data
            
        Returns:
            list: File paths
        """
        # Handle both Windows and Unix formats
        if data.startswith('{'):
            return data.strip('{}').split('} {')
        return data.split()

class InfoPanel(ctk.CTkFrame):
    """
    Panel for displaying analysis information.
    """
    def __init__(self, master, title: str = "", **kwargs):
        super().__init__(master, **kwargs)
        
        if title:
            title_label = ctk.CTkLabel(self, text=title, font=("Segoe UI", 12, "bold"))
            title_label.pack(side="top", fill="x", padx=10, pady=10)
        
        self.text_widget = ctk.CTkTextbox(self, wrap="word", activate_scrollbars=True)
        self.text_widget.pack(fill="both", expand=True, padx=10, pady=10)
    
    def set_text(self, text: str):
        """
        Set panel text content.
        
        Args:
            text: Text to display
        """
        self.text_widget.configure(state="normal")
        self.text_widget.delete(1.0, "end")
        self.text_widget.insert(1.0, text)
        self.text_widget.configure(state="disabled")
    
    def append_text(self, text: str):
        """
        Append text to panel.
        
        Args:
            text: Text to append
        """
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", text)
        self.text_widget.configure(state="disabled")
        self.text_widget.see("end")