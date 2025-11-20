.PHONY: help install install-dev scrape simple-scrape clean test lint format

help:
	@echo "iShortcuts - Apple Shortcuts Guide Scraper"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make install-dev   - Install dev dependencies"
	@echo "  make scrape        - Run full scraper (with Selenium)"
	@echo "  make simple-scrape - Run simple scraper (requests only)"
	@echo "  make clean         - Clean output directories"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linter"
	@echo "  make format        - Format code"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install black flake8 pytest

scrape:
	python scraper.py

simple-scrape:
	python simple_scraper.py

clean:
	rm -rf output/ sections/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

test:
	python -m pytest tests/ -v

lint:
	flake8 scraper.py simple_scraper.py config.py

format:
	black scraper.py simple_scraper.py config.py
