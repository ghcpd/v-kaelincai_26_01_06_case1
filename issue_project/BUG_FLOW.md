# Bug Flow Diagram

## Normal Flow (✅ Works)

```
┌──────────────────┐
│  E-commerce API  │
└────────┬─────────┘
         │
         │ HTTP 200 + JSON
         │ {"products": [...]}
         ▼
┌──────────────────────┐
│  scraper.py          │
│  scrape_product_*()  │
└────────┬─────────────┘
         │
         │ response object
         ▼
┌──────────────────────┐
│  parser.py           │
│  parse_response()    │
│  ├─ json.loads() ✅  │
└────────┬─────────────┘
         │
         │ dict
         ▼
┌──────────────────────┐
│  Product Object      │
│  {id, name, price..} │
└──────────────────────┘
```

## Bug Flow - Scenario A: HTML Error Page (❌ Crash)

```
┌──────────────────┐
│  E-commerce API  │
│  (server error)  │
└────────┬─────────┘
         │
         │ HTTP 200 + HTML ⚠️
         │ <!DOCTYPE html>
         │ <h1>500 Error</h1>
         ▼
┌──────────────────────┐
│  scraper.py          │
│  scrape_product_*()  │
└────────┬─────────────┘
         │
         │ response object
         │ .text = HTML content
         ▼
┌──────────────────────────────┐
│  parser.py                   │
│  parse_response()            │
│  ├─ ⚠️ NO content-type check │
│  ├─ json.loads(HTML) 💥      │
│  └─ JSONDecodeError          │
└──────────────────────────────┘
         │
         │ 💥 EXCEPTION
         ▼
┌──────────────────────┐
│  CRASH               │
│  Entire scraper dies │
└──────────────────────┘
```

## Bug Flow - Scenario B: Session Expired (❌ Crash)

```
┌──────────────────┐
│  E-commerce API  │
│  (auth expired)  │
└────────┬─────────┘
         │
         │ HTTP 200 + HTML ⚠️
         │ <form action="/login">
         ▼
┌──────────────────────┐
│  scraper.py          │
│  scrape_product_*()  │
└────────┬─────────────┘
         │
         │ response.text = login page
         ▼
┌──────────────────────────────┐
│  parser.py                   │
│  parse_response()            │
│  └─ json.loads(HTML) 💥      │
└──────────────────────────────┘
         │
         │ 💥 JSONDecodeError
         ▼
┌──────────────────────┐
│  CRASH               │
│  No re-auth attempt  │
└──────────────────────┘
```

## Expected Fixed Flow (Future)

```
┌──────────────────┐
│  E-commerce API  │
└────────┬─────────┘
         │
         │ HTTP 200 + ???
         ▼
┌──────────────────────┐
│  scraper.py          │
└────────┬─────────────┘
         │
         ▼
┌────────────────────────────────┐
│  parser.py (FIXED)             │
│  parse_response()              │
│  ├─ ✅ Check Content-Type      │
│  ├─ ✅ Validate status code    │
│  ├─ ✅ Detect session expiry   │
│  └─ ✅ Handle errors           │
└────────┬───────────────────────┘
         │
         ├─ JSON → Parse ✅
         ├─ HTML → Raise ParseError
         ├─ Login page → SessionExpiredError
         └─ Text → InvalidContentError
```

## Code Location

```python
# src/parser.py, line 26-38

class ResponseParser:
    def parse_response(self, response_data: Any) -> Dict[str, Any]:
        """Parse HTTP response and extract JSON data.
        
        🐛 BUG: This function assumes response is always valid JSON.
        """
        # 🔴 Line 28 - THE BUG IS HERE 🔴
        return json.loads(response_data.text)
        #      ↑
        #      No validation!
        #      Crashes on HTML/text
```

## Test Coverage

### Tests that DEMONSTRATE the bug (Currently FAILING ❌):

1. `test_parse_html_error_page_should_fail` ← Scenario A
   - **Expects**: `ValueError` with clear message
   - **Gets**: `JSONDecodeError` (crash)

2. `test_parse_session_expired_redirect_page_should_fail` ← Scenario B
   - **Expects**: `ValueError` indicating wrong content type
   - **Gets**: `JSONDecodeError` (crash)

3. `test_parse_plain_text_error_should_fail` ← Scenario C
   - **Expects**: `ValueError` for non-JSON content
   - **Gets**: `JSONDecodeError` (crash)

4. `test_scrape_fails_when_server_returns_html_error` ← Integration A
   - **Expects**: Graceful error handling at scraper level
   - **Gets**: Crash propagated from parser

5. `test_scrape_fails_when_session_expired` ← Integration B
   - **Expects**: Proper session detection
   - **Gets**: Crash propagated from parser

These tests use `pytest.raises(ValueError)` to verify proper error handling.
**They FAIL because the code raises `JSONDecodeError` instead.**

### Tests that verify CORRECT behavior (Currently PASSING ✅):

- `test_parse_valid_json_response` ← Normal flow works
- `test_extract_product_details` ← Data extraction works
- `test_parse_price_various_formats` ← Price parsing works
- etc. (9 tests total)

## Fix Strategy

```diff
  def parse_response(self, response_data: Any) -> Dict[str, Any]:
-     return json.loads(response_data.text)
+     # Validate content type
+     content_type = response_data.headers.get('Content-Type', '')
+     if 'application/json' not in content_type:
+         raise ValueError(f"Expected JSON, got {content_type}")
+     
+     # Parse with error handling
+     try:
+         return json.loads(response_data.text)
+     except json.JSONDecodeError as e:
+         logger.error(f"JSON parse failed: {response_data.text[:200]}")
+         raise ParsingError(f"Invalid JSON: {str(e)}")
```

---

**Visual Summary:**

```
Normal:  API → JSON → Parser ✅ → Product (Tests PASS)
Bug:     API → HTML → Parser 💥 → JSONDecodeError → CRASH (Tests FAIL)
Fixed:   API → HTML → Parser → ValueError → Handled (Tests PASS)
```

**Current Test Status: 5 FAILED, 9 PASSED**

Fix the bug in `src/parser.py` to make all 14 tests pass!
