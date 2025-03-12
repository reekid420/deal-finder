import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.location import (
    get_user_location,
    get_location_by_address,
    get_zipcode_from_coords,
    calculate_distance
)

class TestLocation:
    @pytest.fixture
    def mock_ip_response(self):
        """Mock response from IP geolocation service"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ip": "8.8.8.8",
            "city": "Mountain View",
            "region": "California",
            "country": "US",
            "loc": "37.3860,-122.0838",
            "postal": "94035"
        }
        return mock_response
    
    @pytest.fixture
    def mock_geocoder(self):
        """Mock Nominatim geocoder"""
        mock_nominatim = MagicMock()
        mock_location = MagicMock()
        mock_location.address = "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA"
        mock_location.latitude = 37.4224
        mock_location.longitude = -122.0841
        mock_location.raw = {
            "address": {
                "city": "Mountain View",
                "state": "California",
                "postcode": "94043",
                "country": "United States"
            }
        }
        mock_nominatim.geocode.return_value = mock_location
        return mock_nominatim
    
    @patch('utils.location.requests.get')
    def test_get_user_location(self, mock_get, mock_ip_response):
        """Test getting user location from IP"""
        # Set up the mock
        mock_get.return_value = mock_ip_response
        
        # Call the function
        location = get_user_location()
        
        # Verify the result
        assert location['city'] == "Mountain View"
        assert location['region'] == "California"
        assert location['country'] == "US"
        assert location['zipcode'] == "94035"
        assert location['latitude'] == 37.3860
        assert location['longitude'] == -122.0838
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with('https://ipinfo.io/json')
    
    @patch('utils.location.requests.get')
    def test_get_user_location_error(self, mock_get):
        """Test error handling in get_user_location"""
        # Set up the mock to raise an exception
        mock_get.side_effect = Exception("API error")
        
        # Call the function
        location = get_user_location()
        
        # Verify None is returned on error
        assert location is None
    
    @patch('utils.location.Nominatim')
    def test_get_location_by_address(self, mock_nominatim_class, mock_geocoder):
        """Test getting location details from an address"""
        # Set up the mock
        mock_nominatim_class.return_value = mock_geocoder
        
        # Call the function
        address = "1600 Amphitheatre Parkway, Mountain View, CA"
        location = get_location_by_address(address)
        
        # Verify the result
        assert location['city'] == "Mountain View"
        assert location['region'] == "California"
        assert location['zipcode'] == "94043"
        assert location['country'] == "United States"
        assert location['latitude'] == 37.4224
        assert location['longitude'] == -122.0841
        
        # Verify the geocoder was called correctly
        mock_geocoder.geocode.assert_called_once_with(address, addressdetails=True, language="en")
    
    @patch('utils.location.Nominatim')
    def test_get_location_by_address_not_found(self, mock_nominatim_class):
        """Test handling when address is not found"""
        # Set up the mock to return None (address not found)
        mock_geocoder = MagicMock()
        mock_geocoder.geocode.return_value = None
        mock_nominatim_class.return_value = mock_geocoder
        
        # Verify None is returned when address is not found
        location = get_location_by_address("Non-existent address")
        assert location is None
    
    @patch('utils.location.Nominatim')
    def test_get_zipcode_from_coords(self, mock_nominatim_class):
        """Test getting zipcode from coordinates"""
        # Set up the mock
        mock_geocoder = MagicMock()
        mock_location = MagicMock()
        mock_location.raw = {
            "address": {
                "postcode": "94043"
            }
        }
        mock_geocoder.reverse.return_value = mock_location
        mock_nominatim_class.return_value = mock_geocoder
        
        # Call the function
        zipcode = get_zipcode_from_coords(37.4224, -122.0841)
        
        # Verify the result
        assert zipcode == "94043"
        
        # Verify the geocoder was called correctly
        mock_geocoder.reverse.assert_called_once_with((37.4224, -122.0841))
    
    @patch('utils.location.Nominatim')
    def test_get_zipcode_from_coords_error(self, mock_nominatim_class):
        """Test error handling in get_zipcode_from_coords"""
        # Set up the mock to raise an exception
        mock_geocoder = MagicMock()
        mock_geocoder.reverse.side_effect = Exception("API error")
        mock_nominatim_class.return_value = mock_geocoder
        
        # Call the function
        zipcode = get_zipcode_from_coords(37.4224, -122.0841)
        
        # Verify None is returned on error
        assert zipcode is None
    
    def test_calculate_distance(self):
        """Test distance calculation between two points"""
        # Test with tuples of coordinates
        origin = (37.7749, -122.4194)  # San Francisco
        destination = (34.0522, -118.2437)  # Los Angeles
        
        distance = calculate_distance(origin, destination)
        
        # Distance should be around 350 miles
        assert isinstance(distance, (int, float))
        assert distance > 0 