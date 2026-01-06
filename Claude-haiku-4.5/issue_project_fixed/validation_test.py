"""Direct validation tests for the parser fix."""
print("\n=== TESTING PARSER FIX DIRECTLY ===\n")

import sys
sys.path.insert(0, '.')

from src.parser import ResponseParser
from src.scraper import MockResponse

parser = ResponseParser()

# Test 1: Valid JSON (should work)
print("Test 1: Valid JSON Response")
response = MockResponse(
    text='{"status": "ok", "data": {"id": "123"}}',
    content_type='application/json'
)
try:
    result = parser.parse_response(response)
    print(f"  ✓ PASS: Successfully parsed JSON")
    print(f"    Result: {result}")
except Exception as e:
    print(f"  ✗ FAIL: {type(e).__name__}: {e}")

# Test 2: HTML Error Page (should raise ValueError)
print("\nTest 2: HTML Error Page")
html_response = MockResponse(
    text='<html><h1>500 Internal Server Error</h1></html>',
    status_code=500,
    content_type='text/html'
)
try:
    result = parser.parse_response(html_response)
    print(f"  ✗ FAIL: Should have raised ValueError")
except ValueError as e:
    print(f"  ✓ PASS: Correctly raised ValueError")
    print(f"    Error message: {str(e)[:80]}...")
except Exception as e:
    print(f"  ✗ FAIL: Wrong exception type: {type(e).__name__}")

# Test 3: Plain Text Response (should raise ValueError)
print("\nTest 3: Plain Text Error Response")
text_response = MockResponse(
    text='Service temporarily unavailable',
    content_type='text/plain'
)
try:
    result = parser.parse_response(text_response)
    print(f"  ✗ FAIL: Should have raised ValueError")
except ValueError as e:
    print(f"  ✓ PASS: Correctly raised ValueError")
    print(f"    Error message: {str(e)[:80]}...")
except Exception as e:
    print(f"  ✗ FAIL: Wrong exception type: {type(e).__name__}")

# Test 4: Session Expiration Page (should raise ValueError)
print("\nTest 4: Session Expiration Page")
session_response = MockResponse(
    text='<html><meta http-equiv="refresh" content="0;url=/login"></html>',
    content_type='text/html'
)
try:
    result = parser.parse_response(session_response)
    print(f"  ✗ FAIL: Should have raised ValueError")
except ValueError as e:
    print(f"  ✓ PASS: Correctly raised ValueError")
    print(f"    Error message: {str(e)[:80]}...")
except Exception as e:
    print(f"  ✗ FAIL: Wrong exception type: {type(e).__name__}")

# Test 5: Malformed JSON with JSON content-type (should raise JSONDecodeError)
print("\nTest 5: Malformed JSON")
import json
malformed_response = MockResponse(
    text='{"status": "ok", "data": {incomplete',
    content_type='application/json'
)
try:
    result = parser.parse_response(malformed_response)
    print(f"  ✗ FAIL: Should have raised JSONDecodeError")
except json.JSONDecodeError as e:
    print(f"  ✓ PASS: Correctly raised JSONDecodeError")
    print(f"    Error message: {str(e)[:80]}...")
except Exception as e:
    print(f"  ✗ FAIL: Wrong exception type: {type(e).__name__}")

print("\n=== ALL DIRECT PARSER TESTS COMPLETED ===\n")
