# Contributing to Exoplanet Light Curve Classifier

## Getting Started

### Development Setup
1. Fork the repository
2. Clone your fork
3. Follow setup instructions in [SETUP.md](SETUP.md)
4. Create a feature branch: `git checkout -b feature/your-feature`

## Code Style

### Python
- Follow PEP 8 guidelines
- Use type hints where possible
- Maximum line length: 100 characters
- Use meaningful variable names

### Documentation
- Add docstrings to all functions and classes
- Use Google-style docstrings
- Document parameters and return values

### Example
```python
def analyze_signal(x_data: np.ndarray, y_data: np.ndarray) -> Dict[str, float]:
    """
    Analyze signal and extract features.
    
    Args:
        x_data: X-axis data points
        y_data: Y-axis data points
        
    Returns:
        dict: Analysis metrics
    """
    # Implementation
    pass
```

## Testing

1. Test your changes locally
2. Verify no existing tests break
3. Add new tests for new features
4. Run full test suite before submitting PR

## Commit Messages

Use clear, descriptive commit messages:
```
[Feature/Fix/Docs] Brief description

More detailed explanation if needed.

Fixes: #123
```

## Pull Request Process

1. Update README.md with any new features
2. Update SETUP.md if dependencies change
3. Ensure code follows style guidelines
4. Request review from maintainers
5. Address review feedback

## Reporting Issues

When reporting bugs, include:
- Python version
- OS and version
- Steps to reproduce
- Error messages/logs
- Expected vs actual behavior

## Feature Requests

Describe:
- Problem you're trying to solve
- Proposed solution
- Alternative approaches
- Impact on existing code

## Questions?

Open a discussion or issue on GitHub.

Thank you for contributing!
