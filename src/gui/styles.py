"""GUI styling and theme configuration"""

import customtkinter as ctk
from ..utils.constants import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    COLOR_TEXT, COLOR_TEXT_DIM, DARK_MODE_ENABLED
)

def apply_theme():
    """
    Apply dark mode theme to the application.
    """
    if DARK_MODE_ENABLED:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    else:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

def get_colors():
    """
    Get color palette for current theme.
    
    Returns:
        dict: Color palette
    """
    return {
        'primary': COLOR_PRIMARY,
        'secondary': COLOR_SECONDARY,
        'accent': COLOR_ACCENT,
        'success': COLOR_SUCCESS,
        'warning': COLOR_WARNING,
        'danger': COLOR_DANGER,
        'text': COLOR_TEXT,
        'text_dim': COLOR_TEXT_DIM,
    }

def get_button_style():
    """
    Get button styling parameters.
    
    Returns:
        dict: Button style parameters
    """
    return {
        'font': ('Segoe UI', 11, 'bold'),
        'corner_radius': 8,
        'border_width': 0,
        'hover_color': COLOR_ACCENT,
    }

def get_label_style():
    """
    Get label styling parameters.
    
    Returns:
        dict: Label style parameters
    """
    return {
        'font': ('Segoe UI', 10),
        'text_color': COLOR_TEXT,
    }

def get_entry_style():
    """
    Get entry styling parameters.
    
    Returns:
        dict: Entry style parameters
    """
    return {
        'font': ('Segoe UI', 10),
        'corner_radius': 6,
        'border_width': 1,
        'border_color': COLOR_SECONDARY,
    }