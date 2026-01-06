# Issue Project (fixed)

This repository contains a small price-monitoring scraper and a fixed
version of the response parser that properly handles non-JSON
responses (HTML error pages, login redirects, and plain text errors).

Status: All tests passing ✅

## What changed
- Fixed `src/parser.py` so the parser validates `Content-Type` and
  returns clear `ValueError` errors for non-JSON responses. Malformed
  JSON still raises `json.JSONDecodeError`.

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run tests

From the `issue_project_fixed/` directory run:

```bash
pytest tests/ -v
```

You should see all tests pass:

```
================= 14 passed in 0.XXs =================
```

## Differences from the buggy version

- The original `issue_project/` attempted to call `json.loads()` on
  whatever the response body contained and crashed on HTML or plain
  text responses. The fixed version performs content-type validation
  and gives clear, developer-friendly errors.
