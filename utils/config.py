import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Site configurations
SITES = {
    "ebay": {
        "enabled": True,
        "base_url": "https://www.ebay.com/sch/i.html?_nkw=",
        "requires_selenium": False
    },
    "craigslist": {
        "enabled": True,
        "base_url": "https://craigslist.org/search/sss?query=",
        "requires_selenium": False
    },
    "amazon": {
        "enabled": True,
        "base_url": "https://www.amazon.com/s?k=",
        "requires_selenium": True
    },
    "facebook": {
        "enabled": True,
        "base_url": "https://www.facebook.com/marketplace/search/?query=",
        "requires_selenium": True
    }
}

# Facebook credentials
FB_CREDENTIALS = {
    "email": os.getenv("FB_EMAIL"),
    "password": os.getenv("FB_PASSWORD")
}

# User agent rotation - Updated with more recent browser versions
USER_AGENTS = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    # Mobile
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S908U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36"
]

# Request settings
REQUEST_DELAY_MIN = 2  # seconds
REQUEST_DELAY_MAX = 5  # seconds

# Location settings
DEFAULT_SEARCH_RADIUS = 25  # miles

# Scraper settings
MAX_RESULTS_PER_SITE = 50  # Maximum results to return per site
SEARCH_TIMEOUT = 60  # seconds

# Security settings
SECURITY = {
    "api_key_encryption": True,
    "session_timeout": 3600,  # 1 hour in seconds
    "max_login_attempts": 5,
    "rate_limiting": {
        "enabled": True,
        "max_requests_per_minute": 60
    },
    "proxy_settings": {
        "enabled": False,
        "proxy_rotation": False,
        "proxy_list": []  # Add your proxies here
    },
    "cors_settings": {
        "allowed_origins": ["http://localhost:8501"],
        "allowed_methods": ["GET", "POST"]
    },
    "headers": {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'self'"
    }
}

# Anti-detection measures
ANTI_DETECTION = {
    "randomize_user_agent": True,
    "delay_between_requests": True,
    "simulate_human_behavior": True,
    "handle_cookies": True,
    "fingerprint_randomization": True
}

# Logging configuration
LOGGING = {
    "log_level": "INFO",
    "log_file": "crawler.log",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "max_log_size": 10485760,  # 10MB
    "backup_count": 5
} 