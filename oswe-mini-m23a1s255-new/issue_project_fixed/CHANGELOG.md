# Changelog

## [Unreleased]

### Fixed
- `src/parser.py`: validate `Content-Type` and handle non-JSON responses gracefully. Parser now raises `ValueError` for HTML/plain-text responses (instead of crashing with `json.JSONDecodeError`).

### Files modified
- `src/parser.py` (bug fix)
- `README.md` (status + instructions)
- `CHANGELOG.md` (this file)

### Tests
- Before: 5 failing / 14 total (JSON parsing on non-JSON responses caused crashes)
- After: 0 failing / 14 total — all tests pass

### High-level summary
The parser now explicitly checks the response content-type, applies
sane heuristics when the header is missing, and surfaces clear,
actionable errors to callers (e.g. "Expected JSON response, got text/html"). This prevents the scraper from crashing on maintenance pages,
login redirects, or plain-text error messages.
