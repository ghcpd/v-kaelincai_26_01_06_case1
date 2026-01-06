# Price Monitor — fixed version

Status: ✅ All tests passing

This repository contains a fixed version of the Price Monitor scraper. The
critical fix addresses a JSON parsing vulnerability where non-JSON HTTP
responses (HTML error pages, login redirects, plain-text errors) caused
uncaught exceptions and crashed the scraper.

Key changes
- `src/parser.py`: robust content-type validation and clear error messages
- Tests unchanged; all tests now pass

Quickstart
1. Create a virtualenv and install deps:

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

2. Run tests:

   pytest tests/ -v

What was fixed
- The parser now raises `ValueError` (with helpful message) for
  non-JSON responses instead of allowing `json.JSONDecodeError` to
  propagate. Malformed JSON with an explicit JSON content-type still
  raises `json.JSONDecodeError` so callers can distinguish the cases.

Differences from the buggy version
- Only `src/parser.py` was modified. Tests and other source files were
  copied unchanged.
