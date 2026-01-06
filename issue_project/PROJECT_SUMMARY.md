# Project Summary: Multi-Source Price Monitor Scraper

## Quick Start

### One-Command Setup and Test
```bash
pip install -r requirements.txt && pytest tests/ -v
```

## Project Overview

This is a **deliberately buggy** price monitoring scraper project that demonstrates a common runtime exception in web scraping scenarios.

### Business Context
An intelligent price monitoring system that scrapes product information from multiple e-commerce websites for price comparison and analysis.

### The Planted Bug 🐛

**Type**: Runtime Exception - `json.JSONDecodeError`

**Location**: [src/parser.py](src/parser.py#L28) in `parse_response()` function

**Issue**: The parser blindly attempts to parse all HTTP responses as JSON without validating content type. When servers return HTML error pages or login redirects, the application crashes.

## Project Structure

```
issue_project/
├── src/
│   ├── __init__.py
│   ├── models.py        # Data models (Product, Price, Review, etc.)
│   ├── parser.py        # 🐛 Contains the JSON parsing bug
│   └── scraper.py       # Main scraper orchestration
├── tests/
│   ├── __init__.py
│   ├── test_parser.py   # 5 tests demonstrating parser bug
│   └── test_scraper.py  # 7 integration tests (2 show bug impact)
├── data/
│   └── sample_responses.json  # Sample API responses
├── requirements.txt
├── README.md
├── KNOWN_ISSUE.md      # Detailed bug analysis and fix approaches
└── PROJECT_SUMMARY.md  # This file
```

## Test Results

**Current Status: 5 FAILED ❌, 9 PASSED ✅**

The failing tests demonstrate the bug:
- 5 tests **fail** because they expect graceful error handling (`ValueError`)
- Currently the parser crashes with `JSONDecodeError` instead
- 9 tests **pass** verifying that core functionality works with valid JSON

After fixing the bug, all 14 tests should pass!

### Key Test Cases

#### Bug Demonstration Tests (Currently FAILING ❌)
1. **test_parse_html_error_page_should_fail**
   - Expects: `ValueError` with message about content type
   - Gets: `JSONDecodeError` (crash)

2. **test_parse_session_expired_redirect_page_should_fail**
   - Expects: `ValueError` indicating invalid content
   - Gets: `JSONDecodeError` (crash)

3. **test_parse_plain_text_error_should_fail**
   - Expects: `ValueError` for non-JSON content
   - Gets: `JSONDecodeError` (crash)

4. **test_scrape_fails_when_server_returns_html_error**
   - Expects: Graceful error handling
   - Gets: Scraper crashes with `JSONDecodeError`

5. **test_scrape_fails_when_session_expired**
   - Expects: Proper session expiration detection
   - Gets: Crashes with `JSONDecodeError`

#### Passing Tests (Correct Behavior) ✅
- Valid JSON parsing works correctly
- Product data extraction is accurate
- Price format parsing handles multiple currencies (¥, $, etc.)
- Cross-site product matching functions properly

## The Bug in Detail

### What Happens
```python
# src/parser.py, line 28
def parse_response(self, response_data: Any) -> Dict[str, Any]:
    # 🐛 No validation - assumes all responses are JSON
    return json.loads(response_data.text)
```

### When It Fails
1. **Server Error**: Returns HTML error page with HTTP 200
2. **Session Expired**: Returns login redirect page
3. **Rate Limited**: Returns plain text error message
4. **Maintenance**: Returns maintenance page HTML

### Expected vs Actual Behavior

| Scenario | Expected Behavior | Actual Behavior | Test Status |
|----------|----------|--------|-------------|
| HTML error page | Raise `ValueError` with clear message | ❌ Crash with `JSONDecodeError` | ❌ FAILING |
| Session expired | Raise `ValueError` indicating wrong type | ❌ Crash with `JSONDecodeError` | ❌ FAILING |
| Plain text error | Raise `ValueError` for non-JSON | ❌ Crash with `JSONDecodeError` | ❌ FAILING |
| Valid JSON | Parse successfully | ✅ Works correctly | ✅ PASSING |

## Running the Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_parser.py -v
```

### Run with coverage
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Run specific bug demonstration test
```bash
pytest tests/test_parser.py::TestResponseParserBug::test_parse_html_error_page_should_fail -v
```

## Sample Data

See [data/sample_responses.json](data/sample_responses.json) for examples of:
- Valid JSON product listing response
- Valid JSON product detail response
- HTML error page (triggers bug)
- Session expired redirect page (triggers bug)
- Rate limit plain text response (triggers bug)

## Fix Strategies

See [KNOWN_ISSUE.md](KNOWN_ISSUE.md) for detailed fix approaches:
1. **Defensive Parsing** - Validate content-type before parsing
2. **Response Validation Layer** - Pre-parse validation
3. **Retry with Backoff** - Automatic retry for transient failures

## Technology Stack
- **Language**: Python 3.8+
- **HTTP**: requests library (mocked in tests)
- **Testing**: pytest
- **Platform**: Windows 11

## Key Features Implemented
✅ Multi-stage data extraction workflow  
✅ Product listing scraping  
✅ Price extraction with multiple format support  
✅ Review ratings collection  
✅ Promotion information parsing  
✅ Cross-site product matching  
❌ Robust error handling (deliberately broken)

## Complexity Assessment
- **Bug Complexity**: Simple - single point of failure
- **Reproducibility**: 100% - deterministic test cases
- **Fix Complexity**: Simple - requires 5-10 lines of code
- **Test Coverage**: Good - multiple test cases cover the bug

## Next Steps for Bug Fix
1. Implement content-type validation in `parse_response()`
2. Add proper exception handling
3. Create custom exception types (e.g., `SessionExpiredError`)
4. Update tests to verify proper error handling
5. Add retry logic for transient failures

---

**Project Status**: ✅ Ready for bug bash  
**Bug Status**: 🔴 Present and reproducible  
**Test Status**: ❌ 5 tests failing (demonstrating the bug)
**Your Mission**: Fix the bug in `src/parser.py` to make all 14 tests pass!
