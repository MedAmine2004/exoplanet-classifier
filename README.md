# 🌟 Exoplanet Light Curve Classifier

A professional desktop Python application that assists volunteers in classifying stellar light curves from the **Zooniverse Exoplanet Explorers** project.

## 🎯 Purpose

This tool helps classify astronomical light curves into:
- ✅ **Exoplanet Transit**
- ✅ **Eclipsing Binary**
- ✅ **Stellar Variability**
- ✅ **Instrumental/Systematic Noise**
- ✅ **Insufficient Data**
- ✅ **Unknown / Needs Human Review**

## 🚀 Features

### 📥 Input Methods
1. **Image Upload** - PNG, JPG, JPEG, WEBP
2. **URL Paste** - Automatic download
3. **Zooniverse URL** - Direct extraction from subject pages

### 🔬 Advanced Analysis
- Automatic graph detection and curve extraction
- Signal preprocessing and noise estimation
- Transit depth, duration, and symmetry analysis
- Feature detection (dips, eclipses, oscillations)
- Baseline stability and outlier detection

### 🤖 ML-Based Classification
- Multi-class probability estimation
- Confidence scoring (High/Medium/Low)
- Explainable reasoning engine
- False positive detection

### 📊 Visualization
- Original and processed images
- Extracted curves with smoothing
- Transit models and residuals
- Interactive, zoomable plots
- Real-time analysis updates

### 📄 Export Options
- PDF reports with analysis
- CSV numerical data
- JSON structured results
- TXT plain text summary

### 🎨 User Interface
- Modern dark mode design
- CustomTkinter framework
- Drag-and-drop support
- Progress indicators
- Interactive plots

## 📋 Installation

```bash
git clone https://github.com/MedAmine2004/exoplanet-classifier.git
cd exoplanet-classifier
pip install -r requirements.txt
```

## ▶️ Usage

```bash
python main.py
```

## 📁 Project Structure

```
exoplanet-classifier/
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── src/
│   ├── __init__.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── styles.py
│   │   └── widgets.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── image_processor.py
│   │   ├── curve_extractor.py
│   │   └── downloader.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── signal_analyzer.py
│   │   ├── classifier.py
│   │   └── feature_detector.py
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── report_generator.py
│   │   └── exporters.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── constants.py
└── assets/
    └── icons/
```

## 🔧 Technical Stack

- **GUI**: CustomTkinter (modern dark mode)
- **Image Processing**: OpenCV, scikit-image
- **Numerical Analysis**: NumPy, SciPy, pandas
- **Plotting**: Matplotlib
- **Classification**: scikit-learn
- **Reporting**: ReportLab, pandas

## ⚡ Performance

- Multithreaded analysis (no UI freezing)
- Efficient image processing with OpenCV
- Real-time progress indicators
- Optimized curve extraction algorithms

## 📊 Analysis Metrics

- Transit depth & duration
- Signal-to-noise ratio
- Ingress/egress slopes
- Baseline stability
- Multiple dip detection
- Periodic spacing analysis
- Asymmetry measurements
- V-shaped vs U-shaped eclipses

## 🎓 Classification Engine

Uses feature-based analysis with confidence scoring:
- Exoplanet characteristics
- Binary star signatures
- Variable star patterns
- Noise indicators
- Artifact detection

## 📝 License

MIT License

---

**Built for the Zooniverse Exoplanet Explorers Project**