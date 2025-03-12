# Changelog

All notable changes to the Deal Finder project will be documented in this file.

## [0.5.3] - 2025-03-13
- Improved test coverage from 49% to 50%
- Enhanced Facebook Marketplace scraper tests, increasing coverage from 18% to 24%
- Added comprehensive tests for condition extraction in Facebook scraper
- Implemented captcha detection and handling tests
- Added tests for HTML extraction fallback mechanism
- Added tests for error handling and retry mechanisms
- Fixed all failing tests (73/73 tests now pass, 1 skipped)
- Updated coverage report with latest metrics and improvement recommendations

## [0.5.2] - 2025-03-12
- Improved test coverage from 46% to 49%
- Added comprehensive logging setup tests, increasing logging coverage from 19% to 91%
- Added more Facebook Marketplace scraper tests (session restoration, retry logic)
- Fixed failing tests by making them more robust to implementation changes
- Updated test coverage report with latest metrics

## [0.5.1] - 2025-03-12
- Improved test coverage from 43% to 44%
- Enhanced Facebook scraper tests with 8 new test cases
- Fixed headless mode operation in all scrapers
- Added comprehensive test suite documentation
- Improved .gitignore configuration to exclude sensitive keys and temporary files
- Fixed all failing tests across modules (61/61 tests now pass)

## [0.5.0] - 2025-03-10
- Achieved reliable Facebook Marketplace scraping with robust error handling
- Stabilized Newegg integration with captcha detection and handling
- Added headless mode support for all scrapers
- Improved browser context management for better performance
- Enhanced product parsing logic across all supported sites
- Optimized search URL construction with better parameter handling
- Added support for automated testing of all scraper components

## [0.4.0]
- Added Newegg integration for computer hardware and electronics
- Improved Facebook Marketplace scraper with better detection avoidance
- Enhanced JSON parsing in AI ranking system
- Added more robust error handling for marketplace scrapers
- Improved condition detection for better filtering

## [0.3.0]
- Added Facebook Marketplace integration with Playwright
- Completely redesigned UI with card view and table view options
- Enhanced AI query processing with brand detection and keyword extraction
- Added support for keyword tagging to refine searches
- Improved error handling and fallback mechanisms
- Added sorting options (AI recommendation, price low-high, price high-low)
- Added platform selection to choose which sites to search

## [0.2.0]
- Improved AI integration with Gemini API
- Enhanced error handling in AI processing
- Dynamic model selection for Gemini API
- Updated UI to better process structured AI responses
- Added fallback mechanisms when AI services are unavailable

## [0.1.0]
- Initial release with basic functionality
- eBay integration
- Simple UI with Streamlit
- Location-based filtering 