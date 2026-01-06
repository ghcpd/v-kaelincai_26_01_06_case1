# Changelog

## [Unreleased]

- Fixed: Parser raised `json.JSONDecodeError` when encountering non-JSON responses such as HTML error pages or plain text errors. Now raises `ValueError` with a clear message indicating the expected and actual content type.

### Files modified
- `src/parser.py` — added content-type detection and body inspection; raised `ValueError` for non-JSON content, preserved `json.JSONDecodeError` for malformed JSON.

### Rationale
- Servers sometimes return HTML error pages, maintenance pages, or login redirects while returning a 200 status. The scraper must fail gracefully and provide a helpful error message to callers rather than crashing with an uncaught `JSONDecodeError`.

### Test results
- Before: 5 failing tests (JSON parsing vulnerability for non-JSON responses).
- After: All tests pass (14 passed).

