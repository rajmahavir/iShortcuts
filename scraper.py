#!/usr/bin/env python3
"""
Apple Shortcuts Guide Scraper
Downloads the complete Apple Shortcuts documentation and converts to Markdown and PDF
"""

import os
import re
import time
import json
from urllib.parse import urljoin, urlparse
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class AppleShortcutsGuideScraper:
    """Scraper for Apple Shortcuts documentation"""

    def __init__(self, base_url="https://support.apple.com/en-in/guide/shortcuts/welcome/ios"):
        self.base_url = base_url
        self.domain = "https://support.apple.com"
        self.visited_urls = set()
        self.pages = []
        self.output_dir = Path("output")
        self.sections_dir = Path("sections")
        self.markdown_dir = self.output_dir / "markdown"
        self.pdf_dir = self.output_dir / "pdf"

        # Create directories
        for dir_path in [self.output_dir, self.sections_dir, self.markdown_dir, self.pdf_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Setup headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Setup Selenium driver
        self.driver = None

    def setup_selenium(self):
        """Initialize Selenium WebDriver with Chrome"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✓ Selenium WebDriver initialized")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize Selenium: {e}")
            return False

    def fetch_page_selenium(self, url):
        """Fetch page content using Selenium"""
        if not self.driver:
            if not self.setup_selenium():
                return None

        try:
            self.driver.get(url)
            # Wait for main content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            time.sleep(2)  # Additional wait for dynamic content
            return self.driver.page_source
        except Exception as e:
            print(f"✗ Selenium fetch failed for {url}: {e}")
            return None

    def fetch_page_requests(self, url):
        """Fetch page content using requests"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"✗ Request failed for {url}: {e}")
            return None

    def fetch_page(self, url):
        """Fetch page with fallback methods"""
        # Try requests first (faster)
        html = self.fetch_page_requests(url)
        if html:
            return html

        # Fallback to Selenium
        print(f"Trying Selenium for {url}...")
        html = self.fetch_page_selenium(url)
        return html

    def extract_navigation_links(self, soup, current_url):
        """Extract all navigation links from the guide's table of contents"""
        links = []

        # Apple's documentation typically uses specific navigation structures
        # Look for navigation elements
        nav_selectors = [
            'nav.localnav',
            'nav[role="navigation"]',
            'aside.sidebar',
            'div.topics',
            'div.table-of-contents',
            'ul.toc',
            'nav#sections'
        ]

        for selector in nav_selectors:
            nav = soup.select_one(selector)
            if nav:
                for link in nav.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)

                    # Only include shortcuts guide pages
                    if '/guide/shortcuts/' in full_url and full_url not in self.visited_urls:
                        links.append({
                            'url': full_url,
                            'title': link.get_text(strip=True),
                            'level': self.get_heading_level(link)
                        })

        # Also check main content for "next page" or sequential links
        content_links = soup.select('main a[href*="/guide/shortcuts/"]')
        for link in content_links:
            href = link['href']
            full_url = urljoin(current_url, href)
            if full_url not in self.visited_urls and full_url not in [l['url'] for l in links]:
                links.append({
                    'url': full_url,
                    'title': link.get_text(strip=True),
                    'level': 1
                })

        return links

    def get_heading_level(self, element):
        """Determine heading level based on element position/class"""
        # Check parent elements for indentation or level classes
        parent = element.parent
        level = 1
        while parent and level < 6:
            classes = parent.get('class', [])
            if any('level' in str(c) for c in classes):
                return level
            if parent.name in ['ul', 'ol']:
                level += 1
            parent = parent.parent
        return level

    def extract_main_content(self, soup, url):
        """Extract the main content from the page"""
        # Try different content selectors
        content_selectors = [
            'main',
            'article',
            'div[role="main"]',
            'div.content',
            'div#main-content',
            'div.article-content'
        ]

        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break

        if not content:
            content = soup.find('body')

        # Remove unwanted elements
        unwanted_selectors = [
            'nav',
            'header',
            'footer',
            'aside',
            'script',
            'style',
            'iframe',
            'noscript',
            '.advertisement',
            '.ads',
            '.social-share',
            '.breadcrumb'
        ]

        for selector in unwanted_selectors:
            for element in content.select(selector):
                element.decompose()

        return content

    def html_to_markdown(self, html_content, title=""):
        """Convert HTML content to Markdown"""
        if not html_content:
            return ""

        markdown = f"# {title}\n\n" if title else ""

        # Process headings
        for i in range(1, 7):
            for heading in html_content.find_all(f'h{i}'):
                text = heading.get_text(strip=True)
                markdown += f"{'#' * i} {text}\n\n"

        # Process paragraphs
        for p in html_content.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                markdown += f"{text}\n\n"

        # Process lists
        for ul in html_content.find_all('ul'):
            for li in ul.find_all('li', recursive=False):
                text = li.get_text(strip=True)
                markdown += f"- {text}\n"
            markdown += "\n"

        for ol in html_content.find_all('ol'):
            for idx, li in enumerate(ol.find_all('li', recursive=False), 1):
                text = li.get_text(strip=True)
                markdown += f"{idx}. {text}\n"
            markdown += "\n"

        # Process code blocks
        for code in html_content.find_all(['code', 'pre']):
            text = code.get_text()
            markdown += f"```\n{text}\n```\n\n"

        # Process links
        for a in html_content.find_all('a', href=True):
            text = a.get_text(strip=True)
            href = a['href']
            markdown += f"[{text}]({href})\n"

        return markdown

    def save_page(self, url, title, content, index):
        """Save individual page content"""
        # Sanitize filename
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = f"{index:03d}-{safe_title[:50]}.md"

        filepath = self.sections_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"Source: {url}\n\n")
            f.write("---\n\n")
            f.write(content)

        return filename

    def scrape_guide(self):
        """Main scraping function"""
        print(f"Starting scrape of Apple Shortcuts Guide...")
        print(f"Base URL: {self.base_url}\n")

        # Start with the welcome page
        to_visit = [{'url': self.base_url, 'title': 'Welcome', 'level': 0}]
        page_index = 0

        with tqdm(desc="Scraping pages", unit="page") as pbar:
            while to_visit:
                page_info = to_visit.pop(0)
                url = page_info['url']

                if url in self.visited_urls:
                    continue

                print(f"\n📄 Fetching: {page_info['title']}")
                print(f"   URL: {url}")

                html = self.fetch_page(url)
                if not html:
                    print(f"✗ Failed to fetch {url}")
                    continue

                self.visited_urls.add(url)
                soup = BeautifulSoup(html, 'lxml')

                # Extract title
                title = page_info['title']
                if not title or title == 'Welcome':
                    title_tag = soup.find('h1')
                    if title_tag:
                        title = title_tag.get_text(strip=True)

                # Extract main content
                main_content = self.extract_main_content(soup, url)
                markdown_content = self.html_to_markdown(main_content, title)

                # Save individual page
                filename = self.save_page(url, title, markdown_content, page_index)

                # Store page data
                self.pages.append({
                    'index': page_index,
                    'url': url,
                    'title': title,
                    'level': page_info['level'],
                    'filename': filename,
                    'content': markdown_content
                })

                # Find new pages to visit
                new_links = self.extract_navigation_links(soup, url)
                for link in new_links:
                    if link['url'] not in self.visited_urls:
                        to_visit.append(link)

                page_index += 1
                pbar.update(1)

                # Rate limiting
                time.sleep(1)

        print(f"\n✓ Scraped {len(self.pages)} pages")

    def compile_markdown(self):
        """Compile all pages into a single Markdown file"""
        print("\n📝 Compiling Markdown document...")

        output_file = self.markdown_dir / "apple-shortcuts-guide.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            # Write title and TOC
            f.write("# Apple Shortcuts Guide\n\n")
            f.write(f"Complete guide downloaded from {self.base_url}\n\n")
            f.write("## Table of Contents\n\n")

            for page in self.pages:
                indent = "  " * page['level']
                f.write(f"{indent}- [{page['title']}](#{self.slugify(page['title'])})\n")

            f.write("\n---\n\n")

            # Write all content
            for page in self.pages:
                f.write(f"\n\n## {page['title']}\n\n")
                f.write(f"_Source: [{page['url']}]({page['url']})_\n\n")
                f.write(page['content'])
                f.write("\n\n---\n\n")

        print(f"✓ Markdown saved to: {output_file}")
        return output_file

    def compile_pdf(self, markdown_file):
        """Convert Markdown to PDF using WeasyPrint"""
        print("\n📄 Generating PDF...")

        try:
            from weasyprint import HTML, CSS
            from markdown import markdown

            # Read markdown
            with open(markdown_file, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Convert to HTML
            html_content = markdown(md_content, extensions=['extra', 'codehilite'])

            # Add CSS styling
            css_style = """
            @page {
                margin: 2cm;
                size: A4;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            h1 { color: #000; border-bottom: 2px solid #000; padding-bottom: 0.3em; }
            h2 { color: #333; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            pre {
                background: #f4f4f4;
                padding: 12px;
                border-radius: 5px;
                overflow-x: auto;
            }
            """

            html_doc = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Apple Shortcuts Guide</title>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            output_file = self.pdf_dir / "apple-shortcuts-guide.pdf"
            HTML(string=html_doc).write_pdf(
                output_file,
                stylesheets=[CSS(string=css_style)]
            )

            print(f"✓ PDF saved to: {output_file}")
            return output_file

        except Exception as e:
            print(f"✗ PDF generation failed: {e}")
            print("  Install dependencies: pip install weasyprint markdown")
            return None

    def slugify(self, text):
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')

    def save_metadata(self):
        """Save scraping metadata"""
        metadata = {
            'base_url': self.base_url,
            'pages_scraped': len(self.pages),
            'pages': [
                {
                    'index': p['index'],
                    'title': p['title'],
                    'url': p['url'],
                    'level': p['level']
                }
                for p in self.pages
            ]
        }

        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Metadata saved to: {metadata_file}")

    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()

    def run(self):
        """Execute the complete scraping workflow"""
        try:
            # Scrape all pages
            self.scrape_guide()

            # Compile into single documents
            markdown_file = self.compile_markdown()
            self.compile_pdf(markdown_file)

            # Save metadata
            self.save_metadata()

            print("\n" + "="*60)
            print("✓ Scraping completed successfully!")
            print(f"  Total pages: {len(self.pages)}")
            print(f"  Output directory: {self.output_dir}")
            print("="*60)

        except KeyboardInterrupt:
            print("\n\n⚠ Scraping interrupted by user")
        except Exception as e:
            print(f"\n\n✗ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape Apple Shortcuts Guide')
    parser.add_argument(
        '--url',
        default='https://support.apple.com/en-in/guide/shortcuts/welcome/ios',
        help='Starting URL for the guide'
    )

    args = parser.parse_args()

    scraper = AppleShortcutsGuideScraper(base_url=args.url)
    scraper.run()


if __name__ == '__main__':
    main()
