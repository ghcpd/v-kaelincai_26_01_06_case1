# Changelog

## [Unreleased]

### Fixed
- Addressed bug where `ResponseParser.parse_response()` attempted to parse non-JSON responses and crashed with `json.JSONDecodeError`.
  - File changed: `src/parser.py` (added content-type checking and HTML/plain-text detection)
  - Behavior: Now raises `ValueError` for non-JSON responses with clear messages like "Expected JSON response, got text/html (status=200)".

### Tests
- All original tests were preserved. After the fix, the test suite passes: **14 passed, 0 failed**.

## Notes
- The fix is minimal and focused on response validation before parsing; it does not alter JSON parsing behavior when the response is legitimately `application/json`.
