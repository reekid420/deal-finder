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

1. Clone the repository:
```bash
git clone https://github.com/your-username/tech-deals-finder.git
cd tech-deals-finder
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright for Facebook Marketplace browsing:
```bash
playwright install
```

5. Create a `.env` file and add your API keys and credentials:
```
GEMINI_API_KEY=your_api_key_here
FB_EMAIL=your_facebook_email
FB_PASSWORD=your_facebook_password
```

> **Note**: You can get a Gemini API key from the [Google AI Studio](https://ai.google.dev/).

## Usage

Run the Streamlit web application:

```bash
streamlit run ui/app.py
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

Coming soon:
- Craigslist
- Amazon
- OfferUp

## Recent Updates

### Version 0.3.0 (Latest)
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

- Python 3.8 or higher (tested with Python 3.13)
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