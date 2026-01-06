# Multi-Source Price Monitor Scraper

## Overview
An intelligent price monitoring system that scrapes product information from multiple e-commerce websites for price comparison and analysis.

## Project Structure
```
issue_project/
├── src/
│   ├── __init__.py
│   ├── scraper.py       # Main scraper logic
│   ├── parser.py        # Response parser with data extraction
│   └── models.py        # Data models for products
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py  # Scraper integration tests
│   └── test_parser.py   # Parser unit tests
├── data/
│   └── sample_responses.json  # Sample API responses
├── requirements.txt
├── README.md
└── KNOWN_ISSUE.md       # Known issues and fix approach
```

## Features
- Multi-stage data extraction workflow
- Product listing scraping
- Price and inventory extraction
- Review ratings collection
- Promotion information gathering
- Cross-site product matching

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
pytest tests/ -v
```

### Run Tests with Coverage
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

## Current Status
⚠️ **Known Issues**: See [KNOWN_ISSUE.md](KNOWN_ISSUE.md) for details about the JSON parsing bug.

### Test Results
- **5 tests FAILING** ❌ - Demonstrating the JSON parsing bug
- **9 tests PASSING** ✅ - Core functionality works correctly
- Fix the bug in `src/parser.py` to make all tests pass!

## Tech Stack
- Python 3.8+
- requests for HTTP operations
- pytest for testing
