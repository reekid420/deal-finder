# How to Run the Web Crawler Tests

This guide explains how to use the automated test suite for the web crawler project, which allows you to verify scraper functionality without having to manually configure settings on each website.

## Prerequisites

Make sure you have all required dependencies installed:

```bash
pip install -r requirements.txt
```

## Running Tests

We've created a simple script to run the tests with various options:

```bash
# Run all tests
./run_tests.py

# Run with verbose output (more detailed)
./run_tests.py -v

# Run with coverage report (shows how much of the code is tested)
./run_tests.py -c

# Run just the Facebook scraper tests
./run_tests.py -m scrapers/sites/test_facebook.py

# Run tests with both verbose output and coverage
./run_tests.py -v -c
```

## Test Output

The test output will show which tests passed and failed. By default, it will just show summary information. With the `-v` (verbose) flag, you'll see more details about each test.

Example output:

```
================================================================================
RUNNING WEB CRAWLER TESTS
================================================================================
Running: python -m pytest -v
collected 18 items

tests/scrapers/sites/test_ebay.py::TestEbayScraper::test_init PASSED       [  5%]
tests/scrapers/sites/test_ebay.py::TestEbayScraper::test_search_calls_requests PASSED [ 11%]
...

============================== 18 passed in 2.47s ===============================
```

## Test Structure

The tests are organized into different categories:

- **Unit Tests**: Test individual components in isolation
  - `tests/scrapers/sites/test_facebook.py`
  - `tests/scrapers/sites/test_newegg.py`
  - `tests/scrapers/sites/test_ebay.py`

- **Integration Tests**: Test how components work together
  - `tests/test_integration.py`

## How It Works

The test suite uses "mocking" to simulate website responses and browser behavior. This means:

1. No actual browser is launched
2. No network requests are made
3. Logins are simulated without real credentials
4. Captchas are mocked for testing both detection and handling

This allows tests to run quickly and consistently without depending on external services.

## Adding Your Own Tests

If you want to add more tests, you can follow the patterns in the existing test files. Look at:

- `tests/scrapers/sites/test_facebook.py` for browser-based scraper testing
- `tests/scrapers/sites/test_ebay.py` for request-based scraper testing
- `tests/test_integration.py` for integration testing

## Advanced Usage

You can directly use pytest with additional options:

```bash
# Run tests that match a specific name pattern
python -m pytest -k "facebook"

# Stop on first failure
python -m pytest -x

# Run only tests that failed last time
python -m pytest --lf
```

For more options, run `python -m pytest --help`. 