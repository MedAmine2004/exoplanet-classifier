# Development Setup Guide

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone Repository
```bash
git clone https://github.com/MedAmine2004/exoplanet-classifier.git
cd exoplanet-classifier
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Application
```bash
python main.py
```

## Project Structure

```
exoplanet-classifier/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── SETUP.md              # This file
├── src/
│   ├── __init__.py
│   ├── integration.py    # Main app controller
│   ├── gui/              # GUI components
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── main_window_enhanced.py
│   │   ├── styles.py
│   │   └── widgets.py
│   ├── processors/       # Image and curve processing
│   │   ├── __init__.py
│   │   ├── image_processor.py
│   │   ├── curve_extractor.py
│   │   └── downloader.py
│   ├── analysis/         # Signal analysis and classification
│   │   ├── __init__.py
│   │   ├── signal_analyzer.py
│   │   ├── feature_detector.py
│   │   └── classifier.py
│   ├── reporting/        # Report generation and export
│   │   ├── __init__.py
│   │   ├── report_generator.py
│   │   └── exporters.py
│   └── utils/            # Utilities
│       ├── __init__.py
│       ├── logger.py
│       └── constants.py
├── output/               # Export destination
├── temp/                 # Temporary files
└── logs/                 # Application logs
```

## Key Features

### 📥 Input Methods
- **Upload Image**: Select PNG, JPG, JPEG, or WEBP files
- **Paste URL**: Direct image URLs
- **Zooniverse Integration**: Automatic extraction from Zooniverse subject pages
- **Drag & Drop**: Support for drag-and-drop file loading

### 🔬 Analysis Capabilities
- **Image Processing**: White border removal, contrast enhancement, artifact removal
- **Graph Detection**: Automatic detection and extraction of graph regions
- **Curve Extraction**: Sophisticated curve extraction with color detection
- **Signal Analysis**: 
  - Statistical measures (mean, median, std, skewness, kurtosis)
  - Noise level estimation
  - Signal-to-noise ratio (SNR) calculation
  - Baseline detection and stability analysis
  - Transit/eclipse detection and property measurement
  - Outlier and saturation detection
  - Periodic spacing detection

### 🤖 Classification Features
- **Exoplanet Detection**: Single, U-shaped transits with smooth ingress/egress
- **Eclipsing Binary Detection**: Multiple periodic dips with V-shaped profile
- **Variable Star Detection**: Oscillations and multiple dips
- **Noise Detection**: Noise-dominated signals
- **Data Quality Assessment**: Insufficient data and gaps detection

### 📊 Visualization
- Real-time progress indicators
- Interactive classification results display
- Confidence scoring (High/Medium/Low)
- Classification reasoning explanation

### 📤 Export Options
- **PDF**: Full report with analysis details
- **CSV**: Raw and smoothed light curve data
- **JSON**: Structured analysis results
- **TXT**: Plain text summary

## Configuration

### Modify Constants
Edit `src/utils/constants.py` to adjust:
- Window size
- Color scheme
- Analysis thresholds
- Supported file formats
- Confidence levels
- Export directory

### Analysis Parameters
Key parameters in `constants.py`:
```python
MIN_POINTS_FOR_ANALYSIS = 50      # Minimum data points
SMOOTHING_WINDOW = 5               # Savitzky-Golay window
NOISE_THRESHOLD = 0.02             # Noise detection threshold
TRANSIT_DEPTH_THRESHOLD = 0.001    # Minimum transit depth
CONFIDENCE_HIGH = 0.75             # High confidence threshold
CONFIDENCE_MEDIUM = 0.50           # Medium confidence threshold
```

## Troubleshooting

### Import Errors
If you get import errors, ensure:
1. You're in the project root directory
2. Virtual environment is activated
3. All dependencies are installed: `pip install -r requirements.txt`

### GUI Issues
- Ensure CustomTkinter is properly installed
- Try updating: `pip install --upgrade customtkinter`
- On Linux, you may need additional system libraries

### Image Processing Issues
- Verify OpenCV is installed: `pip list | grep opencv`
- Image must be in supported format (PNG, JPG, JPEG, WEBP)
- Minimum image size: 200x200 pixels

### Network Issues
For URL/Zooniverse features:
- Check internet connection
- Verify URL is accessible
- Check firewall/proxy settings

## Development

### Adding New Features
1. Create new module in appropriate package
2. Add imports to `__init__.py`
3. Follow existing code style
4. Add logging using `get_logger(__name__)`
5. Update README if user-facing

### Running Tests
```bash
# Add test suite as needed
python -m pytest tests/
```

### Logging
Logs are saved to `logs/exoplanet_YYYYMMDD.log`
Set log level in `src/utils/logger.py`

## Performance Tips

1. **Large Images**: Application automatically handles up to 2048x2048 pixels
2. **Multiple Analyses**: Each analysis uses separate threads to prevent UI freezing
3. **Memory**: Temporary files are cleaned up after processing
4. **Export**: Large PDF reports may take a few seconds to generate

## Dependencies

### Core Libraries
- **customtkinter**: Modern GUI framework
- **opencv-python**: Image processing
- **scikit-image**: Advanced image operations
- **scipy**: Scientific computing
- **numpy**: Numerical operations
- **scikit-learn**: Classification

### Utilities
- **matplotlib**: Visualization
- **pandas**: Data handling
- **pillow**: Image manipulation
- **requests**: HTTP requests
- **reportlab**: PDF generation
- **beautifulsoup4**: Web scraping

See `requirements.txt` for specific versions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review logs in `logs/` directory
3. Open a new GitHub issue with details

## License

MIT License - See LICENSE file for details

## Citation

If you use this tool in your research, please cite:
```
Exoplanet Light Curve Classifier (2024)
https://github.com/MedAmine2004/exoplanet-classifier
```

## Acknowledgments

- Built for Zooniverse Exoplanet Explorers project
- Inspired by professional astronomical data analysis workflows
- Thanks to the open-source community
