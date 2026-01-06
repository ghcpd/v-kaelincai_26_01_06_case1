# Price Monitor Scraper (Fixed)

Project: Price monitoring scraper for e-commerce sites.

**Status:** All tests passing ✅

## Description

This project implements a simple scraper and parser for product listings and product details from various e-commerce APIs. This fixed version addresses a critical JSON parsing issue where non-JSON responses (HTML error pages, session redirects, or plain text errors) caused the parser to crash with a `JSONDecodeError`.

## What was fixed

- `src/parser.py` now validates response content (headers and body) before attempting to parse JSON
- For non-JSON content (e.g., `text/html`, `text/plain`, or HTML bodies), the parser raises `ValueError` with a clear message like "Expected JSON response but got HTML content (content-type=text/html)". Malformed JSON still raises `json.JSONDecodeError`.

## Installation

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Running tests

From the project root (`issue_project_fixed/`), run:

```bash
pytest tests/ -v
```

Expected output:

```
================= 14 passed in 0.XX s =================
```

## Differences from buggy version

- `src/parser.py` was modified to perform content-type and payload validation and to raise `ValueError` for non-JSON payloads. No other source or test files were changed.

## Notes

- The fix is intentionally minimal and backwards-compatible: it preserves existing behavior for valid JSON responses (including propagating `json.JSONDecodeError` for malformed JSON), and adds clearer, safer handling for non-JSON responses.
