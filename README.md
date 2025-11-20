# iShortcuts - Apple Shortcuts Guide Scraper

A comprehensive web scraper that downloads the complete Apple Shortcuts Guide documentation and converts it into HTML, Markdown, and PDF formats.

## Features

- 🔍 **Complete Guide Download**: Automatically navigates through all pages of the Apple Shortcuts Guide
- 🌐 **Standalone HTML**: Beautiful, self-contained HTML document with navigation and styling
- 📝 **Markdown Export**: Generates a single, well-formatted Markdown file with table of contents
- 📄 **PDF Generation**: Creates a professional PDF document with proper styling
- 📂 **Organized Output**: Saves individual sections for easy reference
- 🛡️ **Robust Scraping**: Multiple scraper options (advanced, simple, full-featured)
- 📊 **Progress Tracking**: Real-time progress indicators and detailed logging
- ⚡ **Rate Limiting**: Respectful scraping with automatic delays
- 🎨 **Beautiful UI**: Styled HTML output with responsive design and smooth navigation

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome/Chromium browser (for Selenium fallback)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd iShortcuts
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start - Advanced Scraper (Recommended)

The advanced scraper includes HTML output with beautiful styling:

```bash
python advanced_scraper.py
```

This will generate:
- `output/apple-shortcuts-guide.html` - Beautiful standalone HTML
- `output/apple-shortcuts-guide.md` - Complete Markdown document
- `output/apple-shortcuts-guide.pdf` - Professional PDF (requires weasyprint)
- `sections/*.md` - Individual page files

### Other Scrapers

**Simple Scraper** (lightweight, no Selenium):
```bash
python simple_scraper.py
```

**Full Scraper** (with Selenium support):
```bash
python scraper.py
```

### Custom Options

Specify a different URL or max pages:

```bash
python advanced_scraper.py --url "https://support.apple.com/guide/shortcuts/welcome/ios" --max-pages 100
```

## Output Structure

```
iShortcuts/
├── output/
│   ├── apple-shortcuts-guide.html         # 🌐 Standalone HTML (NEW!)
│   ├── apple-shortcuts-guide.md           # 📝 Complete Markdown
│   ├── apple-shortcuts-guide.pdf          # 📄 PDF document
│   └── metadata.json                       # Scraping metadata
├── sections/
│   ├── 001-welcome.md                      # Individual sections
│   ├── 002-getting-started.md
│   └── ...
├── advanced_scraper.py                     # Advanced scraper (recommended)
├── simple_scraper.py                       # Lightweight scraper
└── scraper.py                              # Full-featured scraper
```

## Features Breakdown

### Smart Content Extraction

- Automatically identifies and extracts main content areas
- Removes navigation, headers, footers, and advertisements
- Preserves code examples and formatting
- Maintains hierarchical structure

### Dual Scraping Methods

1. **Requests + BeautifulSoup** (Primary): Fast, efficient scraping for static content
2. **Selenium WebDriver** (Fallback): Handles JavaScript-heavy pages and anti-scraping measures

### Document Compilation

- **Markdown**: Clean, readable format with:
  - Automatic table of contents with links
  - Proper heading hierarchy
  - Source links for each section
  - Code block preservation

- **PDF**: Professional document with:
  - Styled headings and text
  - Proper page margins and layout
  - Syntax-highlighted code blocks
  - Clickable table of contents

## Configuration

### Headers and User-Agent

The scraper uses browser-like headers to avoid being blocked. You can modify these in the `__init__` method of the `AppleShortcutsGuideScraper` class.

### Rate Limiting

Default delay between requests is 1 second. Adjust in the `scrape_guide` method:

```python
time.sleep(1)  # Modify this value
```

### Content Selectors

If Apple changes their page structure, update the selectors in:
- `extract_navigation_links()` - Navigation/TOC selectors
- `extract_main_content()` - Main content selectors

## Troubleshooting

### 403 Forbidden Errors

If you encounter 403 errors, the site may be blocking automated requests. The scraper will automatically fall back to Selenium, which uses a real browser engine.

### Selenium Issues

If Selenium fails to initialize:
```bash
# Update Chrome driver
pip install --upgrade webdriver-manager

# Ensure Chrome/Chromium is installed
# Ubuntu/Debian:
sudo apt-get install chromium-browser

# macOS:
brew install --cask google-chrome
```

### PDF Generation Fails

WeasyPrint requires additional system dependencies:

```bash
# Ubuntu/Debian:
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# macOS:
brew install cairo pango gdk-pixbuf libffi
```

## Technical Details

### Technologies Used

- **Requests**: HTTP library for fetching web pages
- **BeautifulSoup4**: HTML parsing and content extraction
- **Selenium**: Browser automation for dynamic content
- **WeasyPrint**: HTML to PDF conversion
- **Markdown**: Python Markdown library
- **tqdm**: Progress bar visualization

### Scraping Strategy

1. Start with the welcome/index page
2. Extract all navigation links from the table of contents
3. Visit each page and extract main content
4. Save individual sections as Markdown files
5. Compile all sections into a single document
6. Generate PDF from the compiled Markdown
7. Save metadata for reference

## Legal and Ethical Considerations

- This scraper is designed for personal, educational use
- Respects robots.txt and implements rate limiting
- Downloads publicly available documentation
- Does not circumvent paywalls or authentication
- Always review and comply with Apple's Terms of Service

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Apple Inc. for providing comprehensive Shortcuts documentation
- The open-source community for the excellent libraries used in this project

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Disclaimer**: This tool is not affiliated with or endorsed by Apple Inc. It is an independent project for educational purposes.
