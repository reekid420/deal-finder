import requests
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def get_user_location():
    """
    Get the user's location based on IP address
    
    Returns:
        dict: Location information including city, state, zipcode, lat, lng
    """
    try:
        # Use a free IP geolocation service
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        
        location = {
            'city': data.get('city'),
            'region': data.get('region'),
            'country': data.get('country'),
            'loc': data.get('loc'),
            'zipcode': data.get('postal')
        }
        
        # Parse coordinates
        if location['loc']:
            lat, lng = location['loc'].split(',')
            location['latitude'] = float(lat)
            location['longitude'] = float(lng)
            
        return location
        
    except Exception as e:
        print(f"Error getting location: {e}")
        return None

def get_location_by_address(address):
    """
    Get location information from a specific address or place name
    
    Args:
        address (str): User-provided address, city name, or place name
        
    Returns:
        dict: Location information including city, region, country, coordinates, zipcode
    """
    try:
        geolocator = Nominatim(user_agent="tech_deals_finder")
        location_data = geolocator.geocode(address, addressdetails=True, language="en")
        
        if not location_data:
            return None
            
        raw_address = location_data.raw.get('address', {})
        
        location = {
            'city': raw_address.get('city') or raw_address.get('town') or raw_address.get('village') or raw_address.get('hamlet'),
            'region': raw_address.get('state'),
            'country': raw_address.get('country'),
            'loc': f"{location_data.latitude},{location_data.longitude}",
            'latitude': location_data.latitude,
            'longitude': location_data.longitude,
            'zipcode': raw_address.get('postcode'),
            'county': raw_address.get('county')
        }
        
        return location
    except Exception as e:
        print(f"Error getting location from address: {e}")
        return None

def get_zipcode_from_coords(latitude, longitude):
    """Convert coordinates to zipcode using Nominatim (OpenStreetMap)"""
    try:
        geolocator = Nominatim(user_agent="tech_deals_finder")
        location = geolocator.reverse((latitude, longitude))
        
        # Extract postal code
        address = location.raw.get('address', {})
        zipcode = address.get('postcode')
        
        return zipcode
    except Exception as e:
        print(f"Error getting zipcode: {e}")
        return None

def calculate_distance(origin, destination):
    """
    Calculate distance between two geographical points
    
    Args:
        origin (tuple): (latitude, longitude) of origin point
        destination (tuple): (latitude, longitude) of destination point
        
    Returns:
        float: Distance in miles
    """
    try:
        # geodesic returns distance in kilometers, convert to miles
        distance_km = geodesic(origin, destination).kilometers
        distance_miles = distance_km * 0.621371
        return distance_miles
    except Exception as e:
        print(f"Error calculating distance: {e}")
        return None 