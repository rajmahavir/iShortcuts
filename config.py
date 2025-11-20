"""
Configuration settings for the Apple Shortcuts Guide Scraper
"""

# Target URLs
BASE_URL = "https://support.apple.com/en-in/guide/shortcuts/welcome/ios"
DOMAIN = "https://support.apple.com"

# Output directories
OUTPUT_DIR = "output"
MARKDOWN_DIR = "output/markdown"
PDF_DIR = "output/pdf"
SECTIONS_DIR = "sections"

# Scraping settings
REQUEST_TIMEOUT = 30  # seconds
RATE_LIMIT_DELAY = 1  # seconds between requests
MAX_RETRIES = 3

# Browser settings for Selenium
HEADLESS_BROWSER = True
BROWSER_WIDTH = 1920
BROWSER_HEIGHT = 1080

# User-Agent string
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Content selectors for Apple's documentation
NAVIGATION_SELECTORS = [
    'nav.localnav',
    'nav[role="navigation"]',
    'aside.sidebar',
    'div.topics',
    'div.table-of-contents',
    'ul.toc',
    'nav#sections',
    'div#sections',
    'aside#sections'
]

CONTENT_SELECTORS = [
    'main',
    'article',
    'div[role="main"]',
    'div.content',
    'div#main-content',
    'div.article-content',
    'div#content'
]

# Elements to remove from scraped content
UNWANTED_SELECTORS = [
    'nav',
    'header',
    'footer',
    'aside.sidebar',
    'script',
    'style',
    'iframe',
    'noscript',
    '.advertisement',
    '.ads',
    '.social-share',
    '.breadcrumb',
    '.feedback',
    '.related-links'
]

# PDF styling
PDF_CSS = """
@page {
    margin: 2cm;
    size: A4;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
}
h1 {
    color: #000;
    border-bottom: 2px solid #000;
    padding-bottom: 0.3em;
    margin-top: 1.5em;
}
h2 {
    color: #333;
    border-bottom: 1px solid #ccc;
    padding-bottom: 0.2em;
    margin-top: 1.2em;
}
h3 {
    color: #555;
    margin-top: 1em;
}
code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', 'Monaco', monospace;
    font-size: 0.9em;
}
pre {
    background: #f4f4f4;
    padding: 12px;
    border-radius: 5px;
    overflow-x: auto;
    border-left: 3px solid #007AFF;
}
pre code {
    background: none;
    padding: 0;
}
a {
    color: #007AFF;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
blockquote {
    border-left: 4px solid #ddd;
    margin-left: 0;
    padding-left: 1em;
    color: #666;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: left;
}
th {
    background-color: #f8f8f8;
    font-weight: bold;
}
img {
    max-width: 100%;
    height: auto;
}
"""

# Logging settings
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
