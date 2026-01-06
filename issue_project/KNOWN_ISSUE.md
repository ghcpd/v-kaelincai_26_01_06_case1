# Known Issues

## Issue #1: JSON Parsing Failure on Non-JSON Responses

### Problem Type
**Runtime Exception - JSONDecodeError**

### Description
The `ResponseParser.parse_response()` function blindly attempts to parse all HTTP responses as JSON without validating the response content type. When e-commerce servers return HTML error pages, login redirects, or plain text responses (while still returning HTTP 200 status), the parser crashes with a `json.JSONDecodeError`.

### Root Cause
**File**: [src/parser.py](src/parser.py)  
**Function**: `parse_response()`  
**Lines**: 26-38

```python
def parse_response(self, response_data: Any) -> Dict[str, Any]:
    """Parse HTTP response and extract JSON data."""
    # 🐛 PROBLEM: No content-type validation or error handling
    # Directly attempts JSON parsing without checking response format
    return json.loads(response_data.text)
```

The function assumes all responses are valid JSON and does not:
1. Check the `Content-Type` header
2. Validate response status code
3. Handle parsing exceptions
4. Detect session expiration indicators

### Trigger Conditions

#### Scenario A: Server Internal Error
- **When**: Server encounters internal error but returns HTTP 200
- **Response**: HTML error page instead of JSON
- **Expected**: Handle error gracefully, log issue, possibly retry
- **Actual**: `JSONDecodeError` crashes the entire scraper

#### Scenario B: Session/Cookie Expiration
- **When**: Authentication session expires during scraping
- **Response**: HTML login redirect page
- **Expected**: Detect session expiration, re-authenticate, retry request
- **Actual**: `JSONDecodeError` terminates the scraping job

#### Scenario C: Rate Limiting
- **When**: Too many requests trigger rate limiting
- **Response**: Plain text error message
- **Expected**: Implement backoff strategy, retry after delay
- **Actual**: Crash with parsing error

### Reproduction

Run the test suite to see the failing tests that expose this bug:

```bash
pytest tests/ -v
```

**Current Test Results: 5 FAILED, 9 PASSED**

**Failing Tests** (expose the bug):
1. `tests/test_parser.py::TestResponseParserBug::test_parse_html_error_page_should_fail`
   - Expected: `ValueError` with clear message about content type
   - Actual: `JSONDecodeError: Expecting value...` (crashes)

2. `tests/test_parser.py::TestResponseParserBug::test_parse_session_expired_redirect_page_should_fail`
   - Expected: `ValueError` indicating invalid content type
   - Actual: `JSONDecodeError` (crashes)

3. `tests/test_parser.py::TestResponseParserBug::test_parse_plain_text_error_should_fail`
   - Expected: `ValueError` for non-JSON content
   - Actual: `JSONDecodeError` (crashes)

4. `tests/test_scraper.py::TestScraperIntegration::test_scrape_fails_when_server_returns_html_error`
   - Expected: Graceful error handling at scraper level
   - Actual: Scraper crashes with `JSONDecodeError`

5. `tests/test_scraper.py::TestScraperIntegration::test_scrape_fails_when_session_expired`
   - Expected: Detect session expiration properly
   - Actual: Crashes with `JSONDecodeError`

These tests will **pass** once the bug is fixed.

### Impact
- **Severity**: HIGH
- **Frequency**: Medium (occurs in ~5-10% of requests in production)
- **Blast Radius**: Entire scraping job fails, no partial results
- **User Impact**: Price monitoring data becomes incomplete or outdated

### Sample Error Output
```
FAILED tests/test_parser.py::TestResponseParserBug::test_parse_html_error_page_should_fail
AssertionError: assert 'json' in 'expecting value: line 2 column 9 (char 9)'

The test expects ValueError with message containing 'json',
but parser raises JSONDecodeError instead, indicating no validation.

Actual exception from parser:
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  File "src/parser.py", line 28, in parse_response
    return json.loads(response_data.text)
```

## Fix Approach

To fix this bug, you need to add proper validation in the `parse_response()` method. Consider:

### Required Changes:
1. **Content-Type Validation** - Check `Content-Type` header before parsing
2. **Graceful Error Handling** - Raise `ValueError` with clear message instead of letting `JSONDecodeError` propagate
3. **Response Validation** - Verify response is actually JSON before attempting parse

### Suggested Strategies:
- **Option 1**: Defensive parsing with content-type checks
- **Option 2**: Response validation layer before parsing
- **Option 3**: Retry logic with exponential backoff for transient failures

### Success Criteria:
After implementing your fix:
1. ✅ All 5 currently failing tests should pass
2. ✅ All 9 currently passing tests should still pass
3. ✅ Parser raises `ValueError` (not `JSONDecodeError`) for non-JSON responses
4. ✅ Error messages clearly indicate the problem (e.g., "Expected JSON, got text/html")

### Testing Strategy:
```bash
# Before fix: 5 failed, 9 passed
pytest tests/ -v

# After fix: 14 passed
pytest tests/ -v
```

**Note**: The fix should be implemented in `src/parser.py` in the `parse_response()` method around line 28.

### Related Issues
- Session management needs improvement (separate issue)
- Rate limiting detection should be automated (separate issue)
- Response logging for debugging (enhancement)

---

**Status**: 🔴 OPEN  
**Priority**: P0 (Critical)  
**Assigned**: TBD  
**Created**: 2024-01-06
