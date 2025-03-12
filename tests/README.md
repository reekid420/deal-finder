# Web Crawler Test Suite

This directory contains automated tests for the web crawler project, allowing you to verify the functionality of scrapers without having to manually interact with websites.

## Test Structure

- `conftest.py` - Contains shared pytest fixtures used across multiple test files
- `fixtures/` - HTML fixtures to simulate website responses for consistent testing
- `scrapers/` - Tests for individual scraper modules
- `utils/` - Tests for utility functions
- `temp/` - Temporary directory for test artifacts (created automatically)

## Running Tests

You can run the tests using the `run_tests.py` script in the root directory:

```bash
# Run all tests
./run_tests.py

# Run with verbose output
./run_tests.py -v

# Run with coverage report
./run_tests.py -c

# Run a specific test module
./run_tests.py -m scrapers/sites/test_facebook.py
```

## Mocking vs. Real Testing

The test suite uses mocking to simulate browser behavior and website responses, which provides several benefits:

1. **Speed** - Tests run much faster without launching real browsers
2. **Reliability** - Tests don't depend on network conditions or website changes
3. **Consistency** - Tests produce the same results every time
4. **No Credentials** - No need to use real login credentials in tests

## Adding New Tests

When adding new tests:

1. Create a new test file in the appropriate directory
2. Add HTML fixtures if needed
3. Use the existing fixtures in `conftest.py` for browser mocking
4. Follow the pattern of existing tests for consistency

## Mock Data

The test suite includes mock HTML responses in the `fixtures/` directory to simulate website responses. When adding new tests, you can:

1. Use the existing fixtures
2. Create new fixtures for different scenarios
3. Modify existing fixtures to test edge cases

## Handling Captchas in Tests

For websites with captchas like Newegg, the test suite simulates both scenarios:

1. No captcha detected (normal flow)
2. Captcha detected (requires manual intervention in real usage, but mocked in tests)

## Test Coverage

Run tests with the `-c` flag to generate a coverage report showing which parts of the code are covered by tests. 