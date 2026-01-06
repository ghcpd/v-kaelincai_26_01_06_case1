# Changelog

## 2026-01-06 — Fix: Robust JSON parsing (all tests passing)

### Summary
- Fixed a critical bug in `src/parser.py` where the parser attempted to
  parse non-JSON responses (HTML error pages, login redirects, plain
  text) using `json.loads()`, causing `json.JSONDecodeError` to crash
  the scraper.

### Files modified
- `src/parser.py` — implemented Content-Type validation and clear
  `ValueError` for non-JSON responses.
- Added the fixed project tree under `issue_project_fixed/`.
- `README.md` and `CHANGELOG.md` added to document the fix.

### Behavior before
- Non-JSON responses raised `json.JSONDecodeError` and caused
  ungraceful failures in the scraper flow. 5 tests were failing.

### Behavior after
- Non-JSON responses now raise `ValueError` with helpful messages
  (e.g. "Expected JSON response, got text/html"). Malformed JSON in
  responses labeled as `application/json` still raises
  `json.JSONDecodeError` as expected by the tests.

### Test results
- Before: 14 tests total, 5 failing.
- After: 14 passed.
