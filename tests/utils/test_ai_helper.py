import pytest
from unittest.mock import patch, MagicMock
import json
import sys
import os
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.ai_helper import (
    parse_user_query,
    rank_recommendations,
    _parse_ai_response,
    _extract_json_from_text,
    _ensure_complete_structure,
    _create_fallback_query_structure,
)

class TestAIHelper:
    @pytest.fixture
    def mock_genai_model(self):
        """Mock the Gemini model for testing"""
        with patch('utils.ai_helper.genai.GenerativeModel') as mock_model:
            # Mock the generate_content method
            mock_instance = mock_model.return_value
            mock_response = MagicMock()
            mock_response.text = '{"product_type": "laptop", "product_category": "computer", "features": {"ram": "16GB", "storage": "512GB SSD"}, "attributes": {"ram": "16GB", "storage": "512GB SSD"}, "price_range": {"min": 0, "max": 1500}, "query_text": "I need a laptop with 16GB RAM"}'
            mock_instance.generate_content.return_value = mock_response
            yield mock_instance

    def test_parse_user_query_success(self, mock_genai_model):
        """Test parsing a user query successfully"""
        # Call the function
        result = parse_user_query("I need a laptop with 16GB RAM")
        
        # Verify result
        assert result["product_type"] == "laptop"
        assert result["attributes"]["ram"] == "16GB"
        assert result["attributes"]["storage"] == "512GB SSD"
        
        # Verify model was called with appropriate prompt
        call_args = mock_genai_model.generate_content.call_args[0][0]
        assert "Parse this user query" in call_args
        assert "I need a laptop with 16GB RAM" in call_args

    def test_parse_user_query_with_budget(self, mock_genai_model):
        """Test parsing a user query with budget"""
        # Call the function
        result = parse_user_query("I need a laptop with 16GB RAM", budget=1000)
        
        # Verify budget was included in the prompt
        call_args = mock_genai_model.generate_content.call_args[0][0]
        assert "budget" in call_args.lower()
        assert "1000" in call_args

    @patch('utils.ai_helper.genai.GenerativeModel')
    @patch('utils.ai_helper._create_fallback_query_structure')
    def test_parse_user_query_api_failure(self, mock_fallback, mock_model):
        """Test handling of API failures"""
        # Set up the mock to raise an exception
        mock_instance = mock_model.return_value
        mock_instance.generate_content.side_effect = ResourceExhausted("API quota exceeded")
        
        # Set up the fallback mock to return a simple structure
        fallback_response = {
            "product_type": "laptop",
            "keywords": ["laptop", "16GB RAM"],
            "query_text": "I need a laptop with 16GB RAM"
        }
        mock_fallback.return_value = fallback_response
        
        # Call the function - should handle the exception and return fallback
        result = parse_user_query("I need a laptop with 16GB RAM")
        
        # Verify we got the fallback response
        assert result == fallback_response
        assert result["product_type"] == "laptop"
        assert "16GB RAM" in result["keywords"]
        assert result["query_text"] == "I need a laptop with 16GB RAM"
        
        # Verify the fallback function was called with correct args
        mock_fallback.assert_called_once_with("I need a laptop with 16GB RAM", None)

    def test_extract_json_from_text(self):
        """Test extracting JSON from text"""
        # Test with clean JSON
        clean_json = '{"product": "laptop", "price": 1000}'
        result = _extract_json_from_text(clean_json)
        assert result["product"] == "laptop"
        assert result["price"] == 1000
        
        # Test with JSON embedded in text
        text_with_json = 'Here is the result: {"product": "laptop", "price": 1000} Hope that helps!'
        result = _extract_json_from_text(text_with_json)
        assert result["product"] == "laptop"
        assert result["price"] == 1000
        
        # Test with malformed JSON
        malformed_json = '{"product": "laptop", "price": }'
        result = _extract_json_from_text(malformed_json)
        assert result == {}
        
        # Test with no JSON at all
        no_json = "No JSON here, just text"
        result = _extract_json_from_text(no_json)
        assert result == {}

    def test_ensure_complete_structure(self):
        """Test ensuring complete structure of parsed data"""
        # Test with incomplete data
        incomplete_data = {"product_type": "laptop"}
        result = _ensure_complete_structure(incomplete_data, "I need a laptop with 16GB RAM", 1000)
        
        # Verify structure was filled in
        assert "attributes" in result
        assert "price_range" in result
        assert result["price_range"]["max"] == 1000
        assert result["query_text"] == "I need a laptop with 16GB RAM"
        
        # Test with complete data
        complete_data = {
            "product_type": "laptop",
            "attributes": {"ram": "16GB"},
            "price_range": {"min": 500, "max": 1500},
            "query_text": "Original query"
        }
        result = _ensure_complete_structure(complete_data, "New query", 2000)
        
        # Verify original data was preserved
        assert result["attributes"]["ram"] == "16GB"
        assert result["price_range"]["max"] == 1500  # Should keep original
        assert result["query_text"] == "Original query"  # Should keep original

    def test_create_fallback_query_structure(self):
        """Test creating fallback query structure"""
        # Test with simple query
        result = _create_fallback_query_structure("laptop 16GB RAM", 1000)
        
        assert result["product_type"] == "laptop"
        assert "16GB" in result["query_text"]
        assert result["price_range"]["max"] == 1000
        
        # Test with more complex query
        result = _create_fallback_query_structure("gaming desktop with RTX 3080 and i9 processor", 2000)
        
        assert result["product_type"] == "desktop"
        assert "gaming" in result["attributes"]
        assert "RTX 3080" in result["query_text"]
        assert result["price_range"]["max"] == 2000

    @patch('utils.ai_helper.genai.GenerativeModel')
    def test_rank_recommendations(self, mock_model):
        """Test ranking recommendations"""
        # Mock the model response
        mock_instance = mock_model.return_value
        mock_response = MagicMock()
        mock_response.text = json.dumps([
            {"id": 0, "score": 95, "reason": "Matches RAM requirement, Good price"},
            {"id": 1, "score": 80, "reason": "Lower specs, Good price"}
        ])
        mock_instance.generate_content.return_value = mock_response
        
        # Test data
        products = [
            {"id": "123", "title": "Laptop A", "price": 999, "specs": ["16GB RAM", "512GB SSD"]},
            {"id": "456", "title": "Laptop B", "price": 799, "specs": ["8GB RAM", "256GB SSD"]}
        ]
        user_preferences = {"product_type": "laptop", "attributes": {"ram": "16GB"}, "price_range": {"max": 1000}}
        
        # Call the function
        result = rank_recommendations(products, user_preferences)
        
        # Verify the model was called with the right arguments
        call_args = mock_instance.generate_content.call_args[0][0]
        assert "rank" in call_args.lower()
        assert "laptop a" in call_args.lower()
        assert "laptop b" in call_args.lower()
        
        # Verify result structure
        assert len(result) == 2
        assert result[0]["id"] == "123"
        assert "rank_score" in result[0]
        assert "rank_reason" in result[0]
        assert result[1]["id"] == "456"

    @patch('utils.ai_helper.genai.GenerativeModel')
    def test_rank_recommendations_api_failure(self, mock_model):
        """Test ranking recommendations with API failure"""
        # Setup mock to raise exception
        mock_instance = mock_model.return_value
        mock_instance.generate_content.side_effect = ServiceUnavailable("API unavailable")
        
        # Test data
        products = [
            {"id": "123", "title": "Laptop A", "price": 999},
            {"id": "456", "title": "Laptop B", "price": 799}
        ]
        user_preferences = {"product_type": "laptop", "attributes": {"ram": "16GB"}}
        
        # Call the function - should handle exception and return default ranking
        result = rank_recommendations(products, user_preferences)
        
        # Verify we get some kind of result even with API failure
        assert len(result) > 0 