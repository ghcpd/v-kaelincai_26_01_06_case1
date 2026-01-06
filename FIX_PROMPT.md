# Bug Fix Prompt

## Task Description

You are a senior software engineer tasked with fixing a buggy Python project. This is a price monitoring web scraper that has a critical JSON parsing issue causing runtime exceptions.

## Current Situation

- **Project Location**: `issue_project/` (the buggy version)
- **Problem**: 5 out of 14 tests are failing
- **Symptom**: When servers return HTML error pages or plain text instead of JSON, the application crashes with `JSONDecodeError`
- **Impact**: The scraper cannot handle non-JSON responses gracefully

## Your Task

Create a **fixed version** of this project in a new directory called `issue_project_fixed/` with the following requirements:

### 1. Directory Structure

Create the following structure for the fixed version:

```
issue_project_fixed/
├── src/
│   ├── __init__.py
│   ├── models.py          # Copy from original (no changes needed)
│   ├── parser.py          # ⚠️ FIX THE BUG HERE
│   └── scraper.py         # Copy from original (no changes needed)
├── tests/
│   ├── __init__.py
│   ├── test_parser.py     # Copy from original
│   └── test_scraper.py    # Copy from original
├── data/
│   └── sample_responses.json  # Copy from original
├── requirements.txt       # Copy from original
├── README.md              # Update to reflect fixed status
└── CHANGELOG.md           # Document what was fixed
```

### 2. Files to Copy (No Modifications)

Copy these files as-is from `issue_project/` to `issue_project_fixed/`:
- `src/models.py`
- `src/scraper.py`
- `src/__init__.py`
- `tests/__init__.py`
- `tests/test_parser.py`
- `tests/test_scraper.py`
- `data/sample_responses.json`
- `requirements.txt`

### 3. File to Fix

**`src/parser.py`** - This file contains the bug. You need to:
- Analyze the failing tests to identify which method(s) are causing the failures
- Understand what the tests expect vs. what's currently happening
- Implement a fix that makes all tests pass
- Ensure the fix handles HTML error pages, session expiration, and plain text responses gracefully
- Make sure valid JSON parsing continues to work correctly

**Do NOT provide the specific implementation code.** Use the test failures as your guide to locate and fix the issue.

### 4. Documentation to Create/Update

#### `README.md`
Create a new README for the fixed version that includes:
- Project description
- **Status**: All tests passing ✅
- Installation instructions
- How to run tests
- Differences from the buggy version

#### `CHANGELOG.md`
Create a changelog documenting:
- What was the bug
- What files were modified
- What the fix does (high-level)
- Test results before and after

### 5. Success Criteria

After implementing your fix:
- ✅ All 14 tests must pass
- ✅ The parser should raise `ValueError` (not `JSONDecodeError`) for non-JSON responses
- ✅ Error messages should be clear and helpful (e.g., "Expected JSON, got text/html")
- ✅ All existing functionality (valid JSON parsing) must still work
- ✅ No changes to test files
- ✅ No changes to `models.py` or `scraper.py`

### 6. Testing Your Fix

Run the following command from the `issue_project_fixed/` directory:

```bash
pytest tests/ -v
```

Expected output:
```
================= 14 passed in 0.XX s =================
```

All tests should pass with 0 failures.

## Important Guidelines

1. **Analyze First**: Read the failing test cases carefully to understand what behavior they expect
2. **Minimal Changes**: Only modify what's necessary in `src/parser.py`
3. **No Breaking Changes**: Ensure valid JSON parsing still works perfectly
4. **Clear Errors**: Error messages should help developers understand what went wrong
5. **No Test Modifications**: Do not change any test files
6. **Use Relative Paths**: All paths should be relative (e.g., `src/parser.py` not `/absolute/path/...`)

## Hints (Without Solution)

Start by analyzing the test failures:
- Read the failing test cases carefully - what do they expect?
- What exceptions are currently being raised vs. what should be raised?
- What information is available in the response object that could help validate it?
- How can you determine if a response contains JSON before attempting to parse it?
- What's the most appropriate way to signal "wrong content type" to the caller?

## Deliverables

1. Complete `issue_project_fixed/` directory with all files
2. Fixed `src/parser.py` with the bug resolved
3. Updated `README.md` showing fixed status
4. New `CHANGELOG.md` documenting the changes
5. Proof that all 14 tests pass

Good luck! 🚀
