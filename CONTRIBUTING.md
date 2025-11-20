# Contributing to iShortcuts

Thank you for your interest in contributing to iShortcuts! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/iShortcuts.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit and push
7. Create a Pull Request

## Development Setup

```bash
# Install dependencies
make install-dev

# Or manually:
pip install -r requirements.txt
pip install black flake8 pytest
```

## Code Style

We follow PEP 8 style guidelines. Please ensure your code is formatted properly:

```bash
# Format code
make format

# Check linting
make lint
```

## Testing

Before submitting a PR, make sure:

1. Code passes linting: `make lint`
2. Code is formatted: `make format`
3. Imports work correctly
4. The scraper runs without errors on a test page

## Pull Request Guidelines

1. **Clear Description**: Explain what your PR does and why
2. **Small Changes**: Keep PRs focused on a single feature or fix
3. **Test Your Code**: Ensure it works before submitting
4. **Update Documentation**: Update README if you add features
5. **Follow Code Style**: Use `make format` and `make lint`

## Types of Contributions

### Bug Reports

When reporting bugs, please include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)
- Relevant error messages or logs

### Feature Requests

When requesting features:
- Describe the feature clearly
- Explain the use case
- Provide examples if possible

### Code Contributions

Areas where contributions are welcome:

1. **Improved Content Extraction**
   - Better selectors for Apple's documentation
   - Handling edge cases in HTML structure

2. **Output Formats**
   - Additional export formats (EPUB, HTML)
   - Better PDF styling
   - Improved Markdown formatting

3. **Error Handling**
   - More robust error recovery
   - Better retry logic
   - Improved logging

4. **Performance**
   - Faster scraping methods
   - Parallel page downloads
   - Caching mechanisms

5. **Documentation**
   - Improved README
   - Code comments
   - Usage examples

6. **Testing**
   - Unit tests
   - Integration tests
   - CI/CD improvements

## Coding Standards

### Python Code

- Use Python 3.8+ features
- Type hints are encouraged
- Docstrings for all functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Documentation

- Update README.md for new features
- Add docstrings to new functions
- Comment complex logic
- Include usage examples

### Commits

- Use clear, descriptive commit messages
- Start with a verb: "Add", "Fix", "Update", "Remove"
- Reference issues when applicable: "Fix #123"

Example:
```
Add support for EPUB export

- Implement EPUB conversion from Markdown
- Add epub dependencies to requirements.txt
- Update README with EPUB usage
```

## Project Structure

```
iShortcuts/
├── scraper.py           # Main scraper with Selenium
├── simple_scraper.py    # Lightweight scraper
├── config.py            # Configuration settings
├── requirements.txt     # Dependencies
├── README.md           # Documentation
├── LICENSE             # MIT License
├── Makefile            # Build commands
└── .github/
    └── workflows/
        └── test.yml    # CI/CD pipeline
```

## Need Help?

- Open an issue for questions
- Check existing issues and PRs
- Read the README thoroughly

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to iShortcuts! 🚀
