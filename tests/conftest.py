import os
import sys
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from playwright.sync_api import sync_playwright

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a mocked test environment
@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables and directories"""
    # Create test directories
    test_dir = Path("tests/temp")
    test_dir.mkdir(exist_ok=True)
    
    test_screenshot_dir = Path("tests/temp/screenshots")
    test_screenshot_dir.mkdir(exist_ok=True)
    
    test_user_data_dir = Path("tests/temp/user_data")
    test_user_data_dir.mkdir(exist_ok=True)
    
    # Mock environment variables
    with patch.dict(os.environ, {
        "GEMINI_API_KEY": "test_api_key",
        "FB_EMAIL": "test@example.com",
        "FB_PASSWORD": "test_password"
    }):
        yield
    
    # Cleanup can be added here if needed

@pytest.fixture
def mock_sync_playwright():
    """Mock Playwright for testing without real browser"""
    class MockPage:
        def __init__(self):
            self.content = ""
            self.url = ""
            self.eval_results = {}
            self.click_selectors = []
            self.fill_data = {}
            self.navigation_history = []
            self.screenshots = []
            self.timeout = 30000
            self.navigation_timeout = 30000
            self.wait_selectors = []
            self.cookies = []
            
        def goto(self, url, **kwargs):
            self.url = url
            self.navigation_history.append(url)
            return
            
        def content(self):
            return self.content
            
        def set_content(self, content):
            self.content = content
            
        def evaluate(self, script, **kwargs):
            return self.eval_results.get(script, None)
            
        def set_default_timeout(self, timeout):
            self.timeout = timeout
            
        def set_default_navigation_timeout(self, timeout):
            self.navigation_timeout = timeout
            
        def screenshot(self, **kwargs):
            path = kwargs.get('path', f"screenshot_{len(self.screenshots)}.png")
            self.screenshots.append(path)
            
        def wait_for_selector(self, selector, **kwargs):
            self.wait_selectors.append(selector)
            if selector in self.eval_results:
                return MagicMock(is_visible=lambda: True)
            return MagicMock(is_visible=lambda: False)
            
        def click(self, selector, **kwargs):
            self.click_selectors.append(selector)
            
        def fill(self, selector, value):
            self.fill_data[selector] = value

    class MockContext:
        def __init__(self):
            self.is_closed = False
            self.pages = []
            
        def new_page(self):
            page = MockPage()
            self.pages.append(page)
            return page
            
        def close(self):
            self.is_closed = True
            
        def cookies(self):
            return []
            
        def add_cookies(self, cookies):
            pass

    class MockBrowser:
        def __init__(self):
            self.is_closed = False
            
        def new_context(self, **kwargs):
            return MockContext()
            
        def close(self):
            self.is_closed = True
            
        def launch_persistent_context(self, **kwargs):
            return MockContext()

    class MockPlaywright:
        def __init__(self):
            self.chromium = MockBrowser()
            self.firefox = MockBrowser()
            self.webkit = MockBrowser()
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch('playwright.sync_api.sync_playwright', return_value=MockPlaywright()):
        yield MockPlaywright()

@pytest.fixture
def sample_html_responses():
    """Load sample HTML responses for testing"""
    return {
        'facebook_marketplace': Path('tests/fixtures/facebook_marketplace.html').read_text()
        if Path('tests/fixtures/facebook_marketplace.html').exists() else "",
        'newegg_search': Path('tests/fixtures/newegg_search.html').read_text()
        if Path('tests/fixtures/newegg_search.html').exists() else "",
        'ebay_search': Path('tests/fixtures/ebay_search.html').read_text()
        if Path('tests/fixtures/ebay_search.html').exists() else ""
    } 