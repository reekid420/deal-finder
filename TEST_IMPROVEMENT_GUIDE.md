# Test Coverage Improvement Guide

This guide explains how to implement the test improvements to increase coverage for the Facebook Marketplace scraper and the logging setup module.

## Current Coverage

According to the latest test run, the current coverage is:

| Module | Coverage |
|--------|----------|
| Facebook Scraper | 15% |
| Logging Setup | 19% |
| Overall Project | 46% |

## Goal

Increase the coverage to:

| Module | Current | Target |
|--------|---------|--------|
| Facebook Scraper | 15% | 30% |
| Logging Setup | 19% | 70% |
| Overall Project | 46% | 55% |

## Implementation Steps

### 1. Facebook Marketplace Scraper Tests

We've created new test methods in `tests/scrapers/sites/test_facebook_improvements.py`. To implement them:

1. Open your existing `tests/scrapers/sites/test_facebook.py` file
2. Copy each test method from `test_facebook_improvements.py` to your existing test class
3. Adjust the imports if needed (most imports should already be present)
4. Run the tests with `./run_tests.py -v -m tests/scrapers/sites/test_facebook.py` to verify they pass

These new tests focus on:
- Testing the session restoration functionality
- Testing condition extraction from product cards
- Testing captcha handling during browser searches
- Testing search URL construction with various filters
- Testing retry logic in the search method
- Testing product parsing when fields are missing
- Testing product extraction when script evaluation fails

### 2. Logging Setup Tests

We've created a new test file `tests/utils/test_logging_setup.py`. To implement it:

1. Ensure the file is in the correct location
2. Run the tests with `./run_tests.py -v -m tests/utils/test_logging_setup.py`
3. If there are any failures, adjust the tests based on your specific implementation

These tests cover:
- Directory creation during setup
- Logger configuration
- Exception handler registration
- Custom configuration handling
- InterceptHandler functionality
- Module constants

## Verification

After implementing the improvements, run the full test suite with coverage:

```bash
./run_tests.py -v -c
```

Compare the new coverage results with the old ones to verify improvement. Update the coverage statistics in:

1. `.cursorcontext.json`
2. `tests/COVERAGE_REPORT.md`
3. Update the `CHANGELOG.md` with the new coverage improvements

## Tips for Improving Coverage Further

1. **Mock Complex Browser Interactions**: For Facebook Marketplace, continue to mock browser interactions to test complex flows without actual browser automation.

2. **Focus on Error Handling**: Test error handling paths, which are often missed in coverage.

3. **Isolate Pure Functions**: Identify pure functions (those without side effects) and test them thoroughly, as they're easier to test.

4. **Parameterized Tests**: Use pytest's parameterize feature to test the same function with multiple inputs.

Example:
```python
@pytest.mark.parametrize("condition_text,expected", [
    ("New", "New"),
    ("Like New", "Like New"),
    ("Good", "Good"),
    ("Fair", "Fair"),
    (None, "Unknown"),
])
def test_extract_condition_parametrized(self, scraper, condition_text, expected):
    card = MagicMock()
    if condition_text:
        card.query_selector.return_value.inner_text.return_value = condition_text
    else:
        card.query_selector.return_value = None
    assert scraper._extract_condition(card) == expected
``` 