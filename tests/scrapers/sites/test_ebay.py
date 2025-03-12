import os
import pytest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
import requests

from scrapers.sites.ebay import EbayScraper

class TestEbayScraper:
    
    @pytest.fixture
    def scraper(self, test_env):
        """Create a scraper instance for testing"""
        return EbayScraper()
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock HTTP response"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = """
        <html>
            <body>
                <div class="srp-results">
                    <ul class="srp-results">
                        <li class="s-item">
                            <div class="s-item__info">
                                <a class="s-item__link" href="https://www.ebay.com/item/123456">
                                    <h3 class="s-item__title">Test Product</h3>
                                </a>
                                <span class="s-item__price">$99.99</span>
                                <span class="s-item__shipping">Free shipping</span>
                                <div class="s-item__details">
                                    <span class="s-item__detail s-item__detail--primary">
                                        <span>Used</span>
                                    </span>
                                    <span class="s-item__detail s-item__detail--secondary">
                                        <span>10 sold</span>
                                    </span>
                                </div>
                            </div>
                            <div class="s-item__image-section">
                                <div class="s-item__image">
                                    <img src="https://example.com/image.jpg" alt="Test Product">
                                </div>
                            </div>
                        </li>
                    </ul>
                </div>
            </body>
        </html>
        """
        return mock_resp
    
    def test_init(self, scraper):
        """Test scraper initialization"""
        assert scraper.base_url == "https://www.ebay.com/sch/i.html?_nkw="
    
    def test_search_calls_requests(self, scraper, mock_response, monkeypatch):
        """Test that search uses requests to fetch results"""
        # Mock requests.get
        monkeypatch.setattr(requests, "get", MagicMock(return_value=mock_response))
        
        # Call search
        results = scraper.search("test keywords")
        
        # Verify requests.get was called with correct URL
        requests.get.assert_called_once()
        call_args = requests.get.call_args[0][0]
        assert "https://www.ebay.com/sch/i.html?_nkw=test+keywords" in call_args
    
    def test_search_handles_http_errors(self, scraper, monkeypatch):
        """Test that search handles HTTP errors properly"""
        # Mock requests.get to return an error status
        mock_error_response = MagicMock()
        mock_error_response.status_code = 404
        monkeypatch.setattr(requests, "get", MagicMock(return_value=mock_error_response))
        
        # Call search
        results = scraper.search("test keywords")
        
        # Should handle error and return empty list
        assert results == []
    
    def test_search_handles_request_exceptions(self, scraper, monkeypatch):
        """Test that search handles request exceptions properly"""
        # Mock requests.get to raise an exception
        def mock_error(*args, **kwargs):
            raise requests.exceptions.RequestException("Test error")
            
        monkeypatch.setattr(requests, "get", mock_error)
        
        # Call search
        results = scraper.search("test keywords")
        
        # Should handle exception and return empty list
        assert results == []
    
    def test_parse_product_extracts_correct_data(self, scraper, mock_response):
        """Test that product parsing extracts the correct data"""
        # Parse product from mock response
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(mock_response.text, "html.parser")
        product_element = soup.select_one(".s-item")
        
        product = scraper._parse_product(product_element)
        
        # Verify product data was extracted correctly
        assert product["title"] == "Test Product"
        assert product["price"] == "$99.99"
        assert product["shipping"] == "Free shipping"
        assert product["condition"] == "Used"
        assert product["url"] == "https://www.ebay.com/item/123456"
        assert product["image"] == "https://example.com/image.jpg"
    
    def test_search_applies_filters(self, scraper, mock_response, monkeypatch):
        """Test that search applies filters correctly"""
        # Mock requests.get
        monkeypatch.setattr(requests, "get", MagicMock(return_value=mock_response))
        
        # Call search with filters
        results = scraper.search("test keywords", max_price=100.00, condition="used")
        
        # Verify requests.get was called with correct URL including filters
        requests.get.assert_called_once()
        call_args = requests.get.call_args[0][0]
        assert "_udhi=100.00" in call_args  # max price filter
        assert "LH_ItemCondition" in call_args  # condition filter 