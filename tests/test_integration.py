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
    
    def test_multi_scraper_combined_results(self, mock_scrapers):
        """Test combining results from multiple scrapers with uniform format"""
        # Create a list of all products from all scrapers
        all_products = []
        all_products.extend(mock_scrapers["facebook"].search.return_value)
        all_products.extend(mock_scrapers["newegg"].search.return_value)
        all_products.extend(mock_scrapers["ebay"].search.return_value)
        
        # Verify we have the expected number of products
        assert len(all_products) == 7
        
        # Simulate the formatting that would be done by the main application
        formatted_products = []
        for product in all_products:
            # Make sure price is a float for consistent sorting
            price = product["price"]
            if isinstance(price, str):
                price = float(price.replace("$", ""))
            
            formatted_product = {
                "title": product["title"],
                "price": price,
                "url": product.get("url", product.get("link", "")),
                "source": next((s for s in ["facebook", "newegg", "ebay"] if s in product.get("url", "")), "unknown")
            }
            
            formatted_products.append(formatted_product)
        
        # Verify all products were formatted
        assert len(formatted_products) == 7
        
        # Test sorting by price (low to high)
        sorted_products = sorted(formatted_products, key=lambda x: x["price"])
        assert sorted_products[0]["price"] < sorted_products[-1]["price"]
        
        # Test filtering by source
        facebook_products = [p for p in formatted_products if p["source"] == "facebook"]
        assert len(facebook_products) == 2
        
        newegg_products = [p for p in formatted_products if p["source"] == "newegg"]
        assert len(newegg_products) == 2
        
        # Test filtering by price range
        budget_products = [p for p in formatted_products if p["price"] <= 200]
        assert len(budget_products) >= 5  # Should include most FB and eBay products
    
    def test_ai_integration_with_multiple_scrapers(self, mock_scrapers, mock_ai_helper):
        """Test AI integration with results from multiple scrapers"""
        # Get products from all scrapers
        facebook_products = mock_scrapers["facebook"].search.return_value
        newegg_products = mock_scrapers["newegg"].search.return_value
        ebay_products = mock_scrapers["ebay"].search.return_value
        
        # Combine all products
        all_products = facebook_products + newegg_products + ebay_products
        
        # Simulate a user query
        user_query = "I need a laptop with a good price"
        
        # Mock the AI recommendation function (which would be from utils.ai_helper)
        def mock_get_ai_recommendations(products, query):
            # Simulate AI ranking based on query keywords and product data
            # In this case, we'll simulate a focus on "good price" by ranking cheaper products higher
            ranked_products = sorted(products, key=lambda p: float(str(p["price"]).replace("$", "")))
            return ranked_products
        
        # Set the mock_ai_helper's get_recommendations method to use our mock function
        mock_ai_helper.get_recommendations.side_effect = mock_get_ai_recommendations
        
        # Get AI recommendations
        recommendations = mock_ai_helper.get_recommendations(all_products, user_query)
        
        # Verify we get back the same number of products
        assert len(recommendations) == len(all_products)
        
        # Verify that the cheapest product is ranked first
        cheapest_price = min([float(str(p["price"]).replace("$", "")) for p in all_products])
        assert float(str(recommendations[0]["price"]).replace("$", "")) == cheapest_price
    
    def test_error_resilience_with_multiple_scrapers(self, monkeypatch):
        """Test that the system can handle a scraper failing while others succeed"""
        # Create real scraper instances
        facebook_scraper = FacebookMarketplaceScraper()
        newegg_scraper = NeweggScraper()
        ebay_scraper = EbayScraper()
        
        # Mock the search methods
        # Facebook scraper fails with an exception
        def mock_facebook_error(*args, **kwargs):
            raise Exception("Simulated Facebook scraper error")
        
        # Newegg returns empty results
        def mock_newegg_empty(*args, **kwargs):
            return []
        
        # eBay returns results successfully
        def mock_ebay_success(*args, **kwargs):
            return [
                {"title": "Test Product 1", "price": 99.99, "url": "https://ebay.com/1", "source": "ebay"},
                {"title": "Test Product 2", "price": 199.99, "url": "https://ebay.com/2", "source": "ebay"}
            ]
        
        monkeypatch.setattr(facebook_scraper, "search", mock_facebook_error)
        monkeypatch.setattr(newegg_scraper, "search", mock_newegg_empty)
        monkeypatch.setattr(ebay_scraper, "search", mock_ebay_success)
        
        # Create a function that simulates what the main application would do
        def search_all_sites(query, scrapers):
            results = []
            
            for name, scraper in scrapers.items():
                try:
                    site_results = scraper.search(query)
                    results.extend(site_results)
                except Exception as e:
                    # Log but continue with other scrapers
                    print(f"Error with {name} scraper: {e}")
            
            return results
        
        # Run the test using all scrapers
        all_scrapers = {
            "facebook": facebook_scraper,
            "newegg": newegg_scraper,
            "ebay": ebay_scraper
        }
        
        results = search_all_sites("test query", all_scrapers)
        
        # We should get results only from eBay, since Facebook failed and Newegg returned empty
        assert len(results) == 2
        assert all(result["source"] == "ebay" for result in results) 