# AI-Powered Tech Deals Finder

A multi-platform web crawler that searches reselling sites based on user prompts, powered by AI to understand requests, search appropriate sites, and provide personalized recommendations.

## Features

- 🧠 **AI-Powered Search**: Understands natural language queries using Google's Gemini API
- 📍 **Location-Based Filtering**: Finds deals near you with customizable search radius
- 💰 **Budget Optimization**: Sets price limits and finds the best value for your money
- 🏆 **Smart Ranking**: Intelligently ranks products based on your preferences
- 🔍 **Multi-Platform Search**: Searches across multiple e-commerce and reselling platforms
- 🛡️ **Anti-Detection Measures**: Implements best practices to avoid scraping detection
- 🎨 **Beautiful UI**: Modern card-based interface with sorting options and filters
- 🏷️ **Keyword Tagging**: Add specific keywords to refine your search

## Installation

1. Download python 3.12

2. Clone the repository:
```bash
git clone https://github.com/reekid420/tech-deals-finder.git
cd deal-finder
```

3. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate, On Fish terminal: venv\bin\activate.fish 
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Install Playwright for Facebook Marketplace/Newegg browsing:
```bash
playwright install
```

6. Create a `.env` file and add your API keys and credentials:
```
GEMINI_API_KEY=your_api_key_here
FB_EMAIL=your_facebook_email
FB_PASSWORD=your_facebook_password
```

> **Note**: You can get a Gemini API key from the [Google AI Studio](https://ai.google.dev/).

## Usage

Run the Streamlit web application:

```bash
python main.py
```

This will open a web interface where you can:
1. Enter your search query in natural language
2. Set your budget and select which platforms to search
3. Add specific keywords or tags to refine your search
4. Configure location settings and search radius
5. Get personalized tech deal recommendations displayed in a beautiful card layout

### Example Queries

- "I need a gaming laptop with RTX graphics under $1000"
- "Looking for a 4K monitor with HDR support and at least 120Hz refresh rate"
- "Find me the best value iPhone 13 Pro in good condition"

## Project Structure

```
tech-deals-finder/
├── main.py               # Entry point for CLI version
├── requirements.txt      # Project dependencies
├── ui/
│   └── app.py            # Streamlit web interface
├── scrapers/
│   ├── __init__.py
│   ├── base.py           # Base scraper class
│   └── sites/            # Site-specific scrapers
│       ├── __init__.py
│       ├── ebay.py       # eBay scraper
│       ├── facebook.py   # Facebook Marketplace scraper
│       └── ...           # Other site scrapers
├── utils/
│   ├── __init__.py
│   ├── ai_helper.py      # Google Gemini API integration
│   ├── config.py         # Configuration management
│   └── location.py       # Geolocation services
└── data/
    └── cache/            # Cache for search results
```

## Supported Platforms

Currently supported:
- eBay
- Facebook Marketplace
- Newegg

Coming soon:
- Craigslist
- Amazon
- OfferUp

## Recent Updates

### Version 0.4.0 (Latest)
- Added Newegg integration for computer hardware and electronics
- Improved Facebook Marketplace scraper with better detection avoidance
- Enhanced JSON parsing in AI ranking system
- Added more robust error handling for marketplace scrapers
- Improved condition detection for better filtering

### Version 0.3.0
- Added Facebook Marketplace integration with Playwright
- Completely redesigned UI with card view and table view options
- Enhanced AI query processing with brand detection and keyword extraction
- Added support for keyword tagging to refine searches
- Improved error handling and fallback mechanisms
- Added sorting options (AI recommendation, price low-high, price high-low)
- Added platform selection to choose which sites to search

### Version 0.2.0
- Improved AI integration with Gemini API
- Enhanced error handling in AI processing
- Dynamic model selection for Gemini API
- Updated UI to better process structured AI responses
- Added fallback mechanisms when AI services are unavailable

### Version 0.1.0
- Initial release with basic functionality
- eBay integration
- Simple UI with Streamlit
- Location-based filtering

## Requirements

- Python 3.12 (tested with Python 3.12.9)
- Google Gemini API key
- Facebook account for Marketplace access (optional)
- Internet connection

## Troubleshooting

### Common Issues

- **ModuleNotFoundError**: Make sure you have installed all dependencies with `pip install -r requirements.txt`.
- **API Key Errors**: Check that your `.env` file contains the correct Gemini API key.
- **Location Services**: If location detection fails, you can manually set your location in the UI.
- **Facebook Authentication**: For Facebook Marketplace access, you need valid Facebook credentials in your `.env` file.
- **Playwright Issues**: Make sure you've installed browser dependencies with `playwright install`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

# Testing

This project includes a comprehensive test suite for automating testing of scrapers and other components without having to manually configure websites. The test suite uses mocking to simulate browser behavior and website responses.

## Test Structure

The test suite is organized as follows:

- `conftest.py` - Contains shared pytest fixtures used across multiple test files
- `fixtures/` - HTML fixtures to simulate website responses for consistent testing
- `scrapers/` - Tests for individual scraper modules
- `utils/` - Tests for utility functions
- `temp/` - Temporary directory for test artifacts (created automatically)

## Running Tests

To run the tests:

```bash
# Run all tests
./run_tests.py

# Run with verbose output
./run_tests.py -v

# Run with coverage report
./run_tests.py -c

# Run just the Facebook scraper tests
./run_tests.py -m scrapers/sites/test_facebook.py
```

## Test Coverage

Current test coverage is approximately 39% of the codebase. Here's the breakdown by module:

- eBay scraper: 83%
- Facebook scraper: 12%
- Newegg scraper: 22%
- AI Helper module: 64%
- Config module: 100%
- Location module: 83%
- Security module: 89%

See `tests/COVERAGE_REPORT.md` for a detailed breakdown and recommendations for improving coverage.

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

See `HOW_TO_RUN_TESTS.md` for more details on running and writing tests. 