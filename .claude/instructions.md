# Claude Code - iShortcuts Project Instructions

## Project Overview

This is the iShortcuts project - a comprehensive web scraper for downloading and archiving the complete Apple Shortcuts Guide documentation.

## Quick Commands

### Run the Scraper

```bash
# Advanced scraper (recommended - includes HTML output)
python advanced_scraper.py

# Simple scraper (lightweight)
python simple_scraper.py

# Full scraper (with Selenium)
python scraper.py
```

### Development

```bash
# Install dependencies
make install

# Clean output
make clean

# Format code
make format

# Lint code
make lint
```

## GitHub Operations

If working with GitHub integration, remember to:

1. Load environment variables:
```bash
source .env
```

2. Use GitHub API for uploads (if needed):
```bash
./scripts/upload-to-github.sh iShortcuts "Update files"
```

## Project Structure

- `advanced_scraper.py` - Main scraper with HTML/MD/PDF output
- `simple_scraper.py` - Lightweight alternative
- `scraper.py` - Full-featured with Selenium
- `config.py` - Configuration settings
- `output/` - Generated documentation files
- `sections/` - Individual page downloads

## Notes

- The scraper respects rate limiting (1 second between requests)
- Apple's documentation may change structure over time
- HTML output is standalone and includes all styling
- PDF generation requires weasyprint system dependencies

## Target URL

https://support.apple.com/en-in/guide/shortcuts/welcome/ios
