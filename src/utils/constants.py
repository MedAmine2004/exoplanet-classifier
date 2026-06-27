"""Application constants and configuration"""

import os
from pathlib import Path

# Application Information
APP_NAME = "Exoplanet Light Curve Classifier"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Exoplanet Classifier Team"

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "assets"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

# Create directories if they don't exist
for directory in [TEMP_DIR, OUTPUT_DIR, ASSETS_DIR]:
    directory.mkdir(exist_ok=True)

# Classification Classes
CLASSES = {
    "exoplanet": "Exoplanet Transit",
    "binary": "Eclipsing Binary",
    "variable": "Stellar Variability",
    "noise": "Instrumental/Systematic Noise",
    "insufficient": "Insufficient Data",
    "unknown": "Unknown / Needs Human Review"
}

# Confidence Levels
CONFIDENCE_HIGH = 0.75
CONFIDENCE_MEDIUM = 0.50
CONFIDENCE_LOW = 0.00

# Analysis Parameters
MIN_POINTS_FOR_ANALYSIS = 50
SMOOTHING_WINDOW = 5
NOISE_THRESHOLD = 0.02
TRANSIT_DEPTH_THRESHOLD = 0.001

# Image Processing
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.webp'}
MAX_IMAGE_SIZE = (2048, 2048)
MIN_IMAGE_SIZE = (200, 200)

# GUI Configuration
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 1000
DARK_MODE_ENABLED = True

# Colors (Dark Mode)
COLOR_PRIMARY = "#1e1e1e"
COLOR_SECONDARY = "#2d2d2d"
COLOR_ACCENT = "#0078d4"
COLOR_SUCCESS = "#28a745"
COLOR_WARNING = "#ffc107"
COLOR_DANGER = "#dc3545"
COLOR_TEXT = "#ffffff"
COLOR_TEXT_DIM = "#a0a0a0"

# Export Formats
EXPORT_FORMATS = ['pdf', 'csv', 'json', 'txt']

# Zooniverse API
ZOONIVERSE_API_BASE = "https://www.zooniverse.org"
ZOONIVERSE_TIMEOUT = 10

# Feature Detection Thresholds
MIN_DIP_DEPTH = 0.005
MIN_DIP_WIDTH = 3
MAX_NOISE_LEVEL = 0.05
MIN_TRANSIT_POINTS = 10