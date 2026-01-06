# Issue Project (Fixed)

**Status:** ✅ All tests passing

This is a fixed version of the price monitoring scraper project. The critical bug in `src/parser.py` (which caused unhandled `JSONDecodeError` when the server returned HTML or plain text responses) has been resolved.

## What was fixed
- `src/parser.py`: Validate response content type and handle non-JSON (HTML / plain text) responses by raising `ValueError` with a clear message (e.g., "Expected JSON response, got text/html"). Malformed JSON with `application/json` content type still raises `json.JSONDecodeError`.

## Installation

1. Create a virtual environment (optional but recommended):

    python -m venv .venv
    .\.venv\Scripts\activate

2. Install dependencies:

    pip install -r requirements.txt

## Running tests

From the `issue_project_fixed/` directory run:

    pytest tests/ -v

Expected output:

```
================= 14 passed in 0.XXs =================
```

## Differences from buggy version
- `src/parser.py` now checks response headers and content before attempting JSON parsing and raises `ValueError` with helpful messages for HTML or text responses.
- No changes made to `tests/`, `src/models.py`, or `src/scraper.py`.
