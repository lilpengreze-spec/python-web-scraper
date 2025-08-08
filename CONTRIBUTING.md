# Contributing to Review Scraper

Thank you for your interest in contributing to the Review Scraper project! 🎉

## Ways to Contribute

- 🐛 **Report bugs** using our bug report template
- 💡 **Suggest features** using our feature request template  
- 🔧 **Submit pull requests** with improvements
- 📖 **Improve documentation**
- 🧪 **Add tests** for better coverage

## Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/review-scraper.git
   cd review-scraper
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python app.py
   ```

## Making Changes

1. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following these guidelines:
   - Follow PEP 8 style guidelines
   - Add comprehensive error handling
   - Include detailed logging
   - Use type hints
   - Add docstrings to new functions

3. **Test your changes**:
   ```bash
   python test_scraper.py
   python demo.py
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: Your descriptive commit message"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Code Style Guidelines

- **Python**: Follow PEP 8
- **Imports**: Group imports (standard library, third-party, local)
- **Error Handling**: Always include try-catch blocks for external calls
- **Logging**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- **Type Hints**: Add type hints to function parameters and returns
- **Docstrings**: Document all public functions and classes

## Example Code Structure

```python
def scrape_reviews(input_str: str) -> List[Dict[str, Any]]:
    """
    Scrape reviews from a given input.
    
    Args:
        input_str: Business ID or URL to scrape
        
    Returns:
        List of review dictionaries
        
    Raises:
        Exception: If scraping fails
    """
    try:
        # Implementation here
        logger.info(f"Starting scrape for: {input_str}")
        # ... rest of implementation
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise
```

## Testing

- Test all API endpoints manually
- Verify error handling works correctly
- Test with both valid and invalid inputs
- Check that logging is working properly

## Documentation

- Update README.md if adding new features
- Add API documentation for new endpoints
- Update environment variable documentation
- Include examples in docstrings

## Railway Deployment

- Test locally before submitting
- Ensure Railway configuration files are updated if needed
- Test environment variable handling

## Questions?

Feel free to open an issue for questions or join the discussion in existing issues.

## Recognition

Contributors will be recognized in the project README and release notes.

Thank you for contributing! 🚀
