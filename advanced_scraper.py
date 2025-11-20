#!/usr/bin/env python3
"""
Apple Shortcuts Guide Scraper - Advanced Version
Downloads complete Apple Shortcuts documentation with enhanced navigation
and outputs to HTML, Markdown, and PDF formats
"""

import os
import re
import time
import json
import sys
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class AppleDocsNavigator:
    """Handles navigation structure of Apple documentation"""

    def __init__(self, base_url):
        self.base_url = base_url
        self.toc_structure = OrderedDict()
        self.visited = set()

    def extract_toc_links(self, soup, current_url):
        """Extract table of contents links from Apple's documentation"""
        links = []

        # Apple uses specific navigation patterns
        # Check for sidebar navigation
        nav_containers = soup.select('nav.localnav, aside[role="complementary"], div#sections, nav#sections, aside.sidebar, div.navigation')

        for nav in nav_containers:
            # Find all links in navigation
            for link in nav.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)

                # Only include shortcuts guide pages
                if '/guide/shortcuts/' in full_url and full_url not in self.visited:
                    title = link.get_text(strip=True)

                    # Determine hierarchy level
                    level = 0
                    parent = link.parent
                    while parent and parent.name != 'nav':
                        if parent.name in ['ul', 'ol']:
                            level += 1
                        parent = parent.parent

                    links.append({
                        'url': full_url,
                        'title': title or 'Untitled',
                        'level': level
                    })

        # Also check main content for "next" links
        next_links = soup.select('a.next, a[rel="next"], a.pagination-next')
        for link in next_links:
            href = link.get('href', '')
            if '/guide/shortcuts/' in href:
                full_url = urljoin(current_url, href)
                if full_url not in self.visited:
                    links.append({
                        'url': full_url,
                        'title': link.get_text(strip=True) or 'Next Page',
                        'level': 1
                    })

        return links


class AppleShortcutsAdvancedScraper:
    """Advanced scraper for Apple Shortcuts Guide with multiple output formats"""

    def __init__(self, base_url="https://support.apple.com/en-in/guide/shortcuts/welcome/ios"):
        self.base_url = base_url
        self.domain = "https://support.apple.com"
        self.navigator = AppleDocsNavigator(base_url)
        self.pages = []
        self.output_dir = Path("output")
        self.sections_dir = Path("sections")

        # Create directories
        for dir_path in [self.output_dir, self.sections_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Setup session with browser-like headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })

    def fetch_page(self, url, max_retries=3):
        """Fetch page with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"  ✗ Failed after {max_retries} attempts: {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def extract_main_content(self, soup, url):
        """Extract main content from Apple documentation page"""
        # Try multiple selectors for Apple's documentation
        content_selectors = [
            'main#main',
            'article',
            'div[role="main"]',
            'main',
            'div.content',
            'div#content',
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
        unwanted = [
            'nav', 'header', 'footer', 'aside.sidebar',
            'script', 'style', 'iframe', 'noscript',
            '.advertisement', '.ads', '.social-share',
            '.breadcrumb', '.feedback-form', '.related-links',
            'button', '.navigation', '.page-nav'
        ]

        for selector in unwanted:
            for element in content.select(selector):
                element.decompose()

        return content

    def extract_title(self, soup):
        """Extract page title"""
        # Try multiple title sources
        title = None

        # Try h1 first
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)

        # Fallback to title tag
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                # Clean up title
                title = title.split('—')[0].split('-')[0].strip()

        return title or "Untitled"

    def content_to_html(self, content, title=""):
        """Convert extracted content to clean HTML"""
        if not content:
            return ""

        html_parts = []

        if title:
            html_parts.append(f'<h1 id="{self.slugify(title)}">{title}</h1>')

        # Process all elements
        for element in content.children:
            if element.name:
                html_parts.append(str(element))

        return '\n'.join(html_parts)

    def content_to_markdown(self, content, title=""):
        """Convert content to Markdown"""
        if not content:
            return ""

        md = []

        if title:
            md.append(f"# {title}\n")

        # Process headings
        for level in range(2, 7):
            for heading in content.find_all(f'h{level}'):
                text = heading.get_text(strip=True)
                md.append(f"\n{'#' * level} {text}\n")

        # Process paragraphs
        for p in content.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                md.append(f"\n{text}\n")

        # Process lists
        for ul in content.find_all('ul'):
            for li in ul.find_all('li', recursive=False):
                text = li.get_text(strip=True)
                md.append(f"- {text}")
            md.append("")

        for ol in content.find_all('ol'):
            for idx, li in enumerate(ol.find_all('li', recursive=False), 1):
                text = li.get_text(strip=True)
                md.append(f"{idx}. {text}")
            md.append("")

        # Process code blocks
        for code in content.find_all(['pre', 'code']):
            text = code.get_text()
            if code.name == 'pre':
                md.append(f"\n```\n{text}\n```\n")
            else:
                md.append(f"`{text}`")

        return '\n'.join(md)

    def scrape_all_pages(self, max_pages=200):
        """Scrape all pages of the guide"""
        print(f"🚀 Starting scrape of Apple Shortcuts Guide")
        print(f"📍 Base URL: {self.base_url}\n")

        to_visit = [{'url': self.base_url, 'title': 'Welcome', 'level': 0}]
        page_count = 0

        with tqdm(total=max_pages, desc="Scraping pages", unit="page") as pbar:
            while to_visit and page_count < max_pages:
                page_info = to_visit.pop(0)
                url = page_info['url']

                if url in self.navigator.visited:
                    continue

                print(f"\n📄 [{page_count + 1}] {page_info['title']}")
                print(f"   🔗 {url}")

                html = self.fetch_page(url)
                if not html:
                    continue

                self.navigator.visited.add(url)
                soup = BeautifulSoup(html, 'html.parser')

                # Extract title
                title = self.extract_title(soup)

                # Extract main content
                main_content = self.extract_main_content(soup, url)

                # Convert to both formats
                html_content = self.content_to_html(main_content, title)
                md_content = self.content_to_markdown(main_content, title)

                # Save page data
                self.pages.append({
                    'index': page_count,
                    'url': url,
                    'title': title,
                    'level': page_info['level'],
                    'html': html_content,
                    'markdown': md_content
                })

                # Save individual section
                self.save_section(page_count, title, md_content, url)

                # Find new pages
                new_links = self.navigator.extract_toc_links(soup, url)
                for link in new_links:
                    if link['url'] not in self.navigator.visited:
                        to_visit.append(link)

                page_count += 1
                pbar.update(1)

                # Rate limiting
                time.sleep(1)

        print(f"\n✅ Scraped {len(self.pages)} pages")
        return len(self.pages)

    def save_section(self, index, title, content, url):
        """Save individual section as Markdown"""
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = f"{index:03d}-{safe_title[:50]}.md"

        filepath = self.sections_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"Source: {url}\n\n")
            f.write("---\n\n")
            f.write(content)

    def compile_markdown(self):
        """Compile all pages into single Markdown file"""
        print("\n📝 Generating Markdown document...")

        output_file = self.output_dir / "apple-shortcuts-guide.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Apple Shortcuts Guide - Complete Documentation\n\n")
            f.write(f"Downloaded from: {self.base_url}\n\n")
            f.write(f"Total pages: {len(self.pages)}\n\n")
            f.write("---\n\n")

            # Table of Contents
            f.write("## Table of Contents\n\n")
            for page in self.pages:
                indent = "  " * page['level']
                f.write(f"{indent}- [{page['title']}](#{self.slugify(page['title'])})\n")

            f.write("\n---\n\n")

            # Content
            for page in self.pages:
                f.write(f"\n<div id=\"{self.slugify(page['title'])}\"></div>\n\n")
                f.write(f"## {page['title']}\n\n")
                f.write(f"_Source: [{page['url']}]({page['url']})_\n\n")
                f.write(page['markdown'])
                f.write("\n\n---\n\n")

        print(f"✅ Markdown saved: {output_file}")
        return output_file

    def compile_html(self):
        """Compile all pages into standalone HTML file"""
        print("\n🌐 Generating HTML document...")

        output_file = self.output_dir / "apple-shortcuts-guide.html"

        # Build table of contents
        toc_html = ['<nav class="toc"><h2>Table of Contents</h2><ul>']
        for page in self.pages:
            indent_class = f'level-{page["level"]}'
            toc_html.append(
                f'<li class="{indent_class}">'
                f'<a href="#{self.slugify(page["title"])}">{page["title"]}</a>'
                f'</li>'
            )
        toc_html.append('</ul></nav>')

        # Build content
        content_html = []
        for page in self.pages:
            content_html.append(f'<article id="{self.slugify(page["title"])}" class="page-section">')
            content_html.append(f'<div class="page-meta">')
            content_html.append(f'<small>Source: <a href="{page["url"]}">{page["url"]}</a></small>')
            content_html.append(f'</div>')
            content_html.append(page['html'])
            content_html.append('</article>')
            content_html.append('<hr class="section-divider"/>')

        # Complete HTML document
        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apple Shortcuts Guide - Complete Documentation</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1d1d1f;
            background: #f5f5f7;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: grid;
            grid-template-columns: 300px 1fr;
            min-height: 100vh;
        }}

        header {{
            grid-column: 1 / -1;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .toc {{
            background: #f9f9f9;
            border-right: 1px solid #e5e5e5;
            padding: 30px 20px;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }}

        .toc h2 {{
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #333;
        }}

        .toc ul {{
            list-style: none;
        }}

        .toc li {{
            margin: 8px 0;
        }}

        .toc li.level-1 {{
            margin-left: 15px;
            font-size: 0.95em;
        }}

        .toc li.level-2 {{
            margin-left: 30px;
            font-size: 0.9em;
        }}

        .toc a {{
            text-decoration: none;
            color: #0066cc;
            transition: color 0.2s;
        }}

        .toc a:hover {{
            color: #004499;
            text-decoration: underline;
        }}

        main {{
            padding: 40px;
        }}

        .page-section {{
            margin-bottom: 40px;
        }}

        .page-meta {{
            margin-bottom: 20px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }}

        .page-meta small {{
            color: #666;
        }}

        .page-meta a {{
            color: #0066cc;
            text-decoration: none;
        }}

        h1 {{
            font-size: 2.2em;
            color: #1d1d1f;
            margin: 30px 0 20px 0;
            font-weight: 600;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}

        h2 {{
            font-size: 1.8em;
            color: #333;
            margin: 25px 0 15px 0;
            font-weight: 600;
        }}

        h3 {{
            font-size: 1.4em;
            color: #555;
            margin: 20px 0 10px 0;
            font-weight: 600;
        }}

        h4, h5, h6 {{
            color: #666;
            margin: 15px 0 10px 0;
        }}

        p {{
            margin: 15px 0;
            line-height: 1.8;
        }}

        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}

        li {{
            margin: 8px 0;
            line-height: 1.6;
        }}

        code {{
            background: #f4f4f4;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            color: #c7254e;
        }}

        pre {{
            background: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }}

        pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}

        a {{
            color: #0066cc;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        img {{
            max-width: 100%;
            height: auto;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }}

        th {{
            background: #f8f8f8;
            font-weight: 600;
        }}

        .section-divider {{
            border: none;
            border-top: 2px solid #e5e5e5;
            margin: 40px 0;
        }}

        @media (max-width: 768px) {{
            .container {{
                grid-template-columns: 1fr;
            }}

            .toc {{
                position: static;
                height: auto;
                border-right: none;
                border-bottom: 1px solid #e5e5e5;
            }}

            main {{
                padding: 20px;
            }}
        }}

        @media print {{
            .toc {{
                display: none;
            }}

            .container {{
                grid-template-columns: 1fr;
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📱 Apple Shortcuts Guide</h1>
            <p>Complete Documentation - {len(self.pages)} Pages</p>
            <p><small>Source: {self.base_url}</small></p>
        </header>

        {''.join(toc_html)}

        <main>
            {''.join(content_html)}
        </main>
    </div>

    <script>
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});

        // Highlight current section in TOC
        window.addEventListener('scroll', () => {{
            const sections = document.querySelectorAll('.page-section');
            const tocLinks = document.querySelectorAll('.toc a');

            let current = '';
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                if (window.pageYOffset >= sectionTop - 100) {{
                    current = section.getAttribute('id');
                }}
            }});

            tocLinks.forEach(link => {{
                link.style.fontWeight = 'normal';
                if (link.getAttribute('href') === '#' + current) {{
                    link.style.fontWeight = 'bold';
                }}
            }});
        }});
    </script>
</body>
</html>"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_doc)

        print(f"✅ HTML saved: {output_file}")
        return output_file

    def compile_pdf(self, markdown_file):
        """Generate PDF from Markdown"""
        print("\n📄 Generating PDF document...")

        try:
            from weasyprint import HTML, CSS
            from markdown import markdown

            # Read markdown
            with open(markdown_file, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Convert to HTML
            html_content = markdown(md_content, extensions=['extra', 'codehilite', 'toc'])

            # CSS for PDF
            css_style = """
            @page {
                margin: 2.5cm;
                size: A4;
                @bottom-right {
                    content: counter(page);
                }
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                line-height: 1.8;
                color: #333;
                font-size: 11pt;
            }
            h1 {
                color: #000;
                border-bottom: 3px solid #667eea;
                padding-bottom: 0.5em;
                margin-top: 2em;
                page-break-before: always;
            }
            h1:first-of-type {
                page-break-before: avoid;
            }
            h2 {
                color: #333;
                border-bottom: 2px solid #ccc;
                padding-bottom: 0.3em;
                margin-top: 1.5em;
            }
            h3 {
                color: #555;
                margin-top: 1.2em;
            }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
            pre {
                background: #f8f8f8;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #667eea;
                overflow-x: auto;
                font-size: 9pt;
            }
            pre code {
                background: none;
                padding: 0;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background: #f0f0f0;
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
                <h1 style="text-align: center; border: none; font-size: 24pt;">Apple Shortcuts Guide</h1>
                <p style="text-align: center; color: #666;">Complete Documentation</p>
                <hr style="margin: 2em 0;"/>
                {html_content}
            </body>
            </html>
            """

            output_file = self.output_dir / "apple-shortcuts-guide.pdf"
            HTML(string=html_doc).write_pdf(
                output_file,
                stylesheets=[CSS(string=css_style)]
            )

            print(f"✅ PDF saved: {output_file}")
            return output_file

        except ImportError:
            print("⚠️  PDF generation skipped (install weasyprint and markdown)")
            print("   pip install weasyprint markdown")
            return None
        except Exception as e:
            print(f"✗ PDF generation failed: {e}")
            return None

    def save_metadata(self):
        """Save scraping metadata"""
        metadata = {
            'base_url': self.base_url,
            'total_pages': len(self.pages),
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

        print(f"✅ Metadata saved: {metadata_file}")

    def slugify(self, text):
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')

    def run(self):
        """Execute complete scraping workflow"""
        try:
            # Scrape all pages
            num_pages = self.scrape_all_pages()

            if num_pages == 0:
                print("\n⚠️  No pages scraped. Check the URL and try again.")
                return

            # Generate outputs
            md_file = self.compile_markdown()
            html_file = self.compile_html()
            self.compile_pdf(md_file)
            self.save_metadata()

            # Summary
            print("\n" + "="*70)
            print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
            print("="*70)
            print(f"📊 Statistics:")
            print(f"   Total pages scraped: {num_pages}")
            print(f"   Output directory: {self.output_dir.absolute()}")
            print(f"\n📁 Generated Files:")
            print(f"   📝 Markdown: {self.output_dir}/apple-shortcuts-guide.md")
            print(f"   🌐 HTML: {self.output_dir}/apple-shortcuts-guide.html")
            print(f"   📄 PDF: {self.output_dir}/apple-shortcuts-guide.pdf")
            print(f"   📂 Sections: {self.sections_dir}/ ({num_pages} files)")
            print("="*70)

        except KeyboardInterrupt:
            print("\n\n⚠️  Scraping interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n✗ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Advanced scraper for Apple Shortcuts Guide',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --url "https://support.apple.com/en-in/guide/shortcuts/welcome/ios"
  %(prog)s --max-pages 50

Output:
  - apple-shortcuts-guide.md    (Complete Markdown document)
  - apple-shortcuts-guide.html  (Standalone HTML with styling)
  - apple-shortcuts-guide.pdf   (PDF document)
  - sections/*.md               (Individual page files)
        """
    )

    parser.add_argument(
        '--url',
        default='https://support.apple.com/en-in/guide/shortcuts/welcome/ios',
        help='Starting URL for the guide (default: Apple Shortcuts iOS guide)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=200,
        help='Maximum number of pages to scrape (default: 200)'
    )

    args = parser.parse_args()

    print("="*70)
    print("  APPLE SHORTCUTS GUIDE SCRAPER - Advanced Version")
    print("="*70)
    print()

    scraper = AppleShortcutsAdvancedScraper(base_url=args.url)
    scraper.run()


if __name__ == '__main__':
    main()
