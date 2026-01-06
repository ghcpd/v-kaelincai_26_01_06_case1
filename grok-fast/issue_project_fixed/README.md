# Multi-Source Price Monitor Scraper (Fixed Version)

## Overview
An intelligent price monitoring system that scrapes product information from multiple e-commerce websites for price comparison and analysis.

## Project Structure
```
issue_project_fixed/
├── src/
│   ├── __init__.py
│   ├── scraper.py       # Main scraper logic
│   ├── parser.py        # Response parser with data extraction (FIXED)
│   └── models.py        # Data models for products
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py  # Scraper integration tests
│   └── test_parser.py   # Parser unit tests
├── data/
│   └── sample_responses.json  # Sample API responses
├── requirements.txt
├── README.md
├── CHANGELOG.md         # Details of the bug fix
└── KNOWN_ISSUE.md       # Original known issues (for reference)
```

## Features
- Multi-stage data extraction workflow
- Product listing scraping
- Price and inventory extraction
- Review ratings collection
- Promotion information gathering
- Cross-site product matching
- **Robust error handling for non-JSON responses**

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
✅ **All 14 tests PASSING** - JSON parsing bug has been fixed!

### Test Results
- **14 tests PASSING** ✅
- Parser now gracefully handles HTML error pages, session expiration, and plain text responses
- Raises `ValueError` with clear error messages instead of crashing with `JSONDecodeError`

## Differences from Original Version
This fixed version includes:
- Enhanced `src/parser.py` with proper content-type validation
- Clear error messages for non-JSON responses
- Maintains all existing functionality for valid JSON parsing
- Updated documentation reflecting the fixed status

## Tech Stack
- Python 3.8+
- requests for HTTP operations
- pytest for testing