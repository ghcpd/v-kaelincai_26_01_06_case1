# Quick Start Guide

## ⚡ One-Command Setup

```bash
pip install -r requirements.txt && pytest tests/ -v
```

## 📋 Project Summary

**Type**: Multi-Source Price Monitoring Scraper  
**Bug**: JSON Parsing Failure on Non-JSON Responses  
**Complexity**: Simple, Medium  
**Test Cases**: 14 total (5 demonstrate bug, 7 verify correct behavior)

## 🎯 The Bug

**Location**: [src/parser.py:28](src/parser.py#L28)  
**Function**: `ResponseParser.parse_response()`  
**Issue**: No content-type validation before JSON parsing

```python
def parse_response(self, response_data: Any) -> Dict[str, Any]:
    # 🐛 No validation - crashes on HTML/text responses
    return json.loads(response_data.text)
```

## 🧪 Run Tests

### All tests (14 tests, all pass)
```bash
pytest tests/ -v
```

### Bug demonstration only (5 tests)
```bash
pytest tests/test_parser.py::TestResponseParserBug -v
```

### Integration tests (7 tests, 2 show bug impact)
```bash
pytest tests/test_scraper.py -v
```

### With coverage report
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

## 📂 Key Files

| File | Purpose |
|------|---------|
| [src/parser.py](src/parser.py) | 🐛 Contains the bug (line 28) |
| [src/scraper.py](src/scraper.py) | Main scraper logic |
| [src/models.py](src/models.py) | Data models |
| [tests/test_parser.py](tests/test_parser.py) | 5 bug tests + 3 valid tests |
| [tests/test_scraper.py](tests/test_scraper.py) | 7 integration tests |
| [KNOWN_ISSUE.md](KNOWN_ISSUE.md) | Detailed bug analysis |
| [data/sample_responses.json](data/sample_responses.json) | Sample API responses |

## 🐛 Bug Scenarios

### Scenario A: HTML Error Page (500)
Server returns HTML error page instead of JSON → **Crash**

### Scenario B: Session Expired
Authentication expires, returns login page HTML → **Crash**

### Scenario C: Rate Limited
Returns plain text "Rate limit exceeded" → **Crash**

### Scenario D: Malformed JSON
Truncated or corrupted JSON response → **Crash**

## ✅ What Works

- Valid JSON parsing ✅
- Product data extraction ✅
- Price format parsing (¥1,299.00, $199.99, etc.) ✅
- Review ratings extraction ✅
- Cross-site product matching ✅

## 📊 Test Results

**Current Status: 5 FAILED ❌, 9 PASSED ✅**

```
tests/test_parser.py::TestResponseParserBug::
  test_parse_valid_json_response PASSED
  test_parse_html_error_page_should_fail FAILED ← Bug! Expects ValueError, gets JSONDecodeError
  test_parse_session_expired_redirect_page_should_fail FAILED ← Bug!
  test_parse_plain_text_error_should_fail FAILED ← Bug!
  test_parse_malformed_json_should_fail PASSED

tests/test_parser.py::TestProductDataExtraction::
  test_extract_product_listing PASSED
  test_extract_product_details PASSED
  test_parse_price_various_formats PASSED

tests/test_scraper.py::TestScraperIntegration::
  test_scrape_product_listing_success PASSED
  test_scrape_product_details_success PASSED
  test_scrape_fails_when_server_returns_html_error FAILED ← Bug!
  test_scrape_fails_when_session_expired FAILED ← Bug!
  test_match_cross_site_products PASSED

tests/test_scraper.py::TestScraperSessionManagement::
  test_check_session_status PASSED

============= 5 failed, 9 passed in 0.19s ==============
```

**Fix the bug to make all tests pass!**

## 🔧 Your Task

**Goal**: Fix the bug in [src/parser.py](src/parser.py#L28) to make all tests pass!

See [KNOWN_ISSUE.md](KNOWN_ISSUE.md) for suggested approaches:
1. **Defensive Parsing** - Add content-type validation before parsing
2. **Response Validator** - Pre-parse validation layer
3. **Proper Error Handling** - Raise `ValueError` instead of crashing

**Success Criteria**:
- All 14 tests pass ✅
- Parser raises `ValueError` (not `JSONDecodeError`) for non-JSON responses
- Error messages are clear and helpful

## 📖 Documentation

- [README.md](README.md) - Full project documentation
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Comprehensive overview
- [KNOWN_ISSUE.md](KNOWN_ISSUE.md) - Bug analysis and fixes
- **This file** - Quick reference

## 🎓 Learning Objectives

This project demonstrates:
- Common runtime exceptions in web scraping
- Importance of input validation
- Session/authentication handling
- Test-driven bug reproduction
- Content-type validation best practices

---

**Ready to debug? Run the tests and explore the code!** 🚀
