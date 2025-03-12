# AI-Powered Deal Finder

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
git clone https://github.com/reekid420/deal-finder.git
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

Run the application:

```bash
python main.py
```
or
```bash
./run.sh
```

This will open a web interface where you can:
1. Enter your search query in natural language
2. Set your budget and select which platforms to search
3. Add specific keywords or tags to refine your search
4. Configure location settings and search radius
5. Get personalized deal recommendations displayed in a beautiful card layout

### Example Queries

- "I need a gaming laptop with RTX graphics under $1000"
- "Looking for a 4K monitor with HDR support and at least 120Hz refresh rate"
- "Find me the best value iPhone 13 Pro in good condition"

## Project Structure

```
deal-finder/
├── main.py               # Entry point for CLI version
├── requirements.txt      # Project dependencies
├── run_tests.py          # Script to run the test suite
├── ui/
│   └── app.py            # Streamlit web interface
├── scrapers/
│   ├── __init__.py
│   ├── base.py           # Base scraper class
│   └── sites/            # Site-specific scrapers
│       ├── __init__.py
│       ├── ebay.py       # eBay scraper
│       ├── facebook.py   # Facebook Marketplace scraper
│       └── newegg.py     # Newegg scraper
├── utils/
│   ├── __init__.py
│   ├── ai_helper.py      # Google Gemini API integration
│   ├── config.py         # Configuration management
│   ├── location.py       # Geolocation services
│   └── security.py       # Security and encryption utilities
├── tests/
│   ├── conftest.py       # Pytest fixtures
│   ├── fixtures/         # HTML fixtures for testing
│   ├── scrapers/         # Tests for scraper modules
│   └── utils/            # Tests for utility modules
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

## Testing

This project includes a comprehensive test suite for automating testing of scrapers and other components without having to manually configure websites. The test suite uses mocking to simulate browser behavior and website responses.

### Running Tests

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

### Test Coverage

Current test coverage is approximately 49% of the codebase. Here's the breakdown by module:

- eBay scraper: 83%
- Facebook scraper: 18%
- Newegg scraper: 42%
- AI Helper module: 68%
- Config module: 100%
- Location module: 87%
- Security module: 89%
- Logging module: 91%

See `tests/COVERAGE_REPORT.md` for a detailed breakdown and recommendations for improving coverage.

### Headless Mode

All scrapers support headless mode operation for running without displaying browser UI. This is particularly useful for:
- Running in environments without displays
- Automation and CI/CD pipelines
- Improved performance in production environments

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

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes to this project.

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) - see the [LICENSE](LICENSE) file for details.

### What this means:

- You are free to use, modify, and distribute this software.
- If you distribute modified versions, you must:
  - Disclose the source code
  - License your modifications under the GPL-3.0
  - Maintain copyright notices
  - Document changes you've made
- This program comes with ABSOLUTELY NO WARRANTY.

For more details on the GPL-3.0 license, visit [https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html) 