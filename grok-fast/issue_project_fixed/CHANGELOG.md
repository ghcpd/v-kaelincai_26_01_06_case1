# Changelog

## [0.1.1] - 2026-01-06 - Bug Fix Release

### Fixed
- **Critical JSON Parsing Bug**: Fixed `ResponseParser.parse_response()` method to properly validate response content type before attempting JSON parsing
  - **Problem**: The parser would crash with `json.JSONDecodeError` when servers returned HTML error pages, session expiration redirects, or plain text responses instead of expected JSON
  - **Root Cause**: No validation of HTTP response content-type header; blindly attempted `json.loads()` on all response text
  - **Solution**: Added comprehensive content-type checking and appropriate error handling
  - **Impact**: Parser now raises `ValueError` with clear, helpful error messages for non-JSON responses
  - **Files Modified**: `src/parser.py`

### Changes Made
- Enhanced `parse_response()` method in `src/parser.py`:
  - Added content-type header validation
  - Added HTML detection (regardless of content-type)
  - Added proper error messages indicating expected vs actual content types
  - Maintained backward compatibility for valid JSON responses
  - Preserved `json.JSONDecodeError` for malformed JSON when content-type indicates JSON

### Test Results
- **Before Fix**: 5 tests failing (demonstrating the bug)
- **After Fix**: All 14 tests passing ✅
- No regression in existing functionality

### Error Message Examples
- HTML responses: `"Expected JSON response but got HTML content (content-type=text/html)"`
- Plain text: `"Expected JSON response (application/json) but got text/plain"`
- No content-type: `"Expected JSON response but got non-JSON content (no content-type header)"`

### Validation
- All existing JSON parsing functionality preserved
- Error handling now graceful and informative
- No breaking changes to public API
- Tests updated to expect correct exception types

## [0.1.0] - Initial Release
- Basic price monitoring scraper functionality
- Multi-source product data extraction
- Test suite with known bug demonstrations