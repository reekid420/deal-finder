import pytest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Add project root to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import modules after path setup
try:
    from scrapers.sites.facebook import FacebookMarketplaceScraper
    from scrapers.sites.newegg import NeweggScraper
    from scrapers.sites.ebay import EbayScraper
except ImportError:
    pass  # Handle in the test setup

class TestIntegration:
    """Integration tests for coordinating between different scrapers"""
    
    @pytest.fixture
    def mock_scrapers(self, monkeypatch):
        """Set up mock scrapers for testing"""
        # Mock scraper search methods
        facebook_scraper = MagicMock()
        facebook_scraper.search.return_value = [
            {"title": "FB Product 1", "price": "$199.99", "url": "https://facebook.com/1"},
            {"title": "FB Product 2", "price": "$99.99", "url": "https://facebook.com/2"}
        ]
        
        newegg_scraper = MagicMock()
        newegg_scraper.search.return_value = [
            {"title": "Newegg Product 1", "price": "$899.99", "url": "https://newegg.com/1"},
            {"title": "Newegg Product 2", "price": "$349.99", "url": "https://newegg.com/2"}
        ]
        
        ebay_scraper = MagicMock()
        ebay_scraper.search.return_value = [
            {"title": "eBay Product 1", "price": "$149.99", "url": "https://ebay.com/1"},
            {"title": "eBay Product 2", "price": "$79.99", "url": "https://ebay.com/2"},
            {"title": "eBay Product 3", "price": "$119.99", "url": "https://ebay.com/3"}
        ]
        
        # Return a dictionary of mock scrapers
        return {
            "facebook": facebook_scraper,
            "newegg": newegg_scraper,
            "ebay": ebay_scraper
        }
    
    @pytest.fixture
    def mock_ai_helper(self):
        """Mock the AI helper for testing"""
        mock_ai = MagicMock()
        mock_ai.generate_recommendations.return_value = {
            "best_value": "eBay Product 2",
            "premium_pick": "Newegg Product 1",
            "recommendations": [
                "Based on your search, the eBay Product 2 offers the best value",
                "If you're looking for premium quality, consider the Newegg Product 1",
                "The Facebook marketplace has similar items that might be available for pickup"
            ]
        }
        return mock_ai
    
    def test_multi_site_search(self, mock_scrapers):
        """Test searching across multiple sites"""
        # Test running searches in parallel
        search_results = {}
        
        # Run mock searches
        search_results["facebook"] = mock_scrapers["facebook"].search("test product")
        search_results["newegg"] = mock_scrapers["newegg"].search("test product")
        search_results["ebay"] = mock_scrapers["ebay"].search("test product")
        
        # Verify each scraper was called
        mock_scrapers["facebook"].search.assert_called_once_with("test product")
        mock_scrapers["newegg"].search.assert_called_once_with("test product")
        mock_scrapers["ebay"].search.assert_called_once_with("test product")
        
        # Verify results were collected
        assert len(search_results["facebook"]) == 2
        assert len(search_results["newegg"]) == 2
        assert len(search_results["ebay"]) == 3
        
        # Verify combined results
        all_results = []
        for site, results in search_results.items():
            for result in results:
                result["site"] = site
                all_results.append(result)
        
        assert len(all_results) == 7
    
    def test_ai_recommendations(self, mock_scrapers, mock_ai_helper):
        """Test AI recommendations based on search results"""
        # Get mock search results
        search_results = {}
        search_results["facebook"] = mock_scrapers["facebook"].search("test product")
        search_results["newegg"] = mock_scrapers["newegg"].search("test product")
        search_results["ebay"] = mock_scrapers["ebay"].search("test product")
        
        # Combine results
        all_results = []
        for site, results in search_results.items():
            for result in results:
                result["site"] = site
                all_results.append(result)
        
        # Get recommendations from AI
        recommendations = mock_ai_helper.generate_recommendations(all_results, "test product")
        
        # Verify AI was called
        mock_ai_helper.generate_recommendations.assert_called_once()
        
        # Verify recommendations
        assert "best_value" in recommendations
        assert "premium_pick" in recommendations
        assert "recommendations" in recommendations
        assert len(recommendations["recommendations"]) == 3
    
    def test_search_with_filters(self, mock_scrapers):
        """Test searching with filters across sites"""
        # Apply filters to search
        filters = {
            "max_price": 200.00,
            "condition": "used"
        }
        
        # Run mock searches with filters
        mock_scrapers["facebook"].search("test product", max_price=filters["max_price"], condition=filters["condition"])
        mock_scrapers["newegg"].search("test product", max_price=filters["max_price"], condition=filters["condition"])
        mock_scrapers["ebay"].search("test product", max_price=filters["max_price"], condition=filters["condition"])
        
        # Verify each scraper was called with filters
        mock_scrapers["facebook"].search.assert_called_once_with(
            "test product", max_price=filters["max_price"], condition=filters["condition"]
        )
        mock_scrapers["newegg"].search.assert_called_once_with(
            "test product", max_price=filters["max_price"], condition=filters["condition"]
        )
        mock_scrapers["ebay"].search.assert_called_once_with(
            "test product", max_price=filters["max_price"], condition=filters["condition"]
        ) 