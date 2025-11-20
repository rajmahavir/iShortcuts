#!/usr/bin/env python3
"""
Simplified Apple Shortcuts Guide Scraper
A lighter alternative using only requests and BeautifulSoup
"""

import os
import re
import time
import json
from urllib.parse import urljoin
from pathlib import Path
import requests
from bs4 import BeautifulSoup


class SimpleAppleShortcutsScraper:
    """Simplified scraper without Selenium dependency"""

    def __init__(self, base_url="https://support.apple.com/en-in/guide/shortcuts/welcome/ios"):
        self.base_url = base_url
        self.visited = set()
        self.pages = []

        # Create output directories
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        # Setup session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })

    def fetch_page(self, url):
        """Fetch a page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_links(self, soup, current_url):
        """Extract guide links"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/guide/shortcuts/' in href:
                full_url = urljoin(current_url, href)
                if full_url not in self.visited:
                    links.append({
                        'url': full_url,
                        'title': a.get_text(strip=True) or 'Untitled'
                    })
        return links

    def clean_content(self, soup):
        """Extract and clean main content"""
        # Remove unwanted elements
        for elem in soup.select('nav, header, footer, script, style'):
            elem.decompose()

        # Try to find main content
        main = soup.find('main') or soup.find('article') or soup.find('body')

        if not main:
            return ""

        # Extract text
        content = []
        for elem in main.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'code']):
            tag = elem.name
            text = elem.get_text(strip=True)

            if not text:
                continue

            if tag.startswith('h'):
                level = int(tag[1])
                content.append(f"\n{'#' * level} {text}\n")
            elif tag == 'p':
                content.append(f"{text}\n")
            elif tag in ['ul', 'ol']:
                for li in elem.find_all('li', recursive=False):
                    content.append(f"- {li.get_text(strip=True)}\n")
                content.append("\n")
            elif tag in ['pre', 'code']:
                content.append(f"\n```\n{text}\n```\n")

        return '\n'.join(content)

    def scrape(self, max_pages=100):
        """Scrape the guide"""
        print(f"Starting scrape from: {self.base_url}\n")

        to_visit = [{'url': self.base_url, 'title': 'Welcome'}]
        count = 0

        while to_visit and count < max_pages:
            page = to_visit.pop(0)
            url = page['url']

            if url in self.visited:
                continue

            print(f"[{count + 1}] {page['title']}")
            print(f"    {url}")

            html = self.fetch_page(url)
            if not html:
                continue

            self.visited.add(url)
            soup = BeautifulSoup(html, 'html.parser')

            # Get title
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else page['title']

            # Extract content
            content = self.clean_content(soup)

            self.pages.append({
                'title': title,
                'url': url,
                'content': content
            })

            # Find more links
            new_links = self.extract_links(soup, url)
            to_visit.extend(new_links)

            count += 1
            time.sleep(1)  # Rate limiting

        print(f"\n✓ Scraped {len(self.pages)} pages")

    def save_markdown(self):
        """Save as markdown"""
        output_file = self.output_dir / "apple-shortcuts-guide.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Apple Shortcuts Guide\n\n")
            f.write(f"Downloaded from: {self.base_url}\n\n")

            # Table of contents
            f.write("## Table of Contents\n\n")
            for i, page in enumerate(self.pages, 1):
                f.write(f"{i}. [{page['title']}](#{self.slugify(page['title'])})\n")

            f.write("\n---\n\n")

            # Content
            for page in self.pages:
                f.write(f"\n## {page['title']}\n\n")
                f.write(f"_Source: {page['url']}_\n\n")
                f.write(page['content'])
                f.write("\n\n---\n\n")

        print(f"✓ Saved to: {output_file}")
        return output_file

    def slugify(self, text):
        """Create URL slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')

    def run(self):
        """Run the scraper"""
        try:
            self.scrape()
            self.save_markdown()
            print("\n✓ Done!")
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        except Exception as e:
            print(f"\n✗ Error: {e}")


if __name__ == '__main__':
    scraper = SimpleAppleShortcutsScraper()
    scraper.run()
