import os
import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.map_tools import is_maps_available, search_places, get_place_details, create_map


class TestMapTools(unittest.TestCase):
    """Test cases for the Google Maps tools module."""

    def setUp(self):
        """Set up test environment."""
        # Sample place data
        self.test_place = {
            "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
            "name": "Test Restaurant",
            "vicinity": "123 Test St, Seattle, WA",
            "rating": 4.5,
            "geometry": {
                "location": {
                    "lat": 47.6062,
                    "lng": -122.3321
                }
            }
        }
        
        self.test_place_details = {
            "name": "Test Restaurant",
            "formatted_address": "123 Test St, Seattle, WA 98101",
            "formatted_phone_number": "(555) 123-4567",
            "rating": 4.5,
            "user_ratings_total": 100,
            "geometry": {
                "location": {
                    "lat": 47.6062,
                    "lng": -122.3321
                }
            },
            "opening_hours": {
                "weekday_text": [
                    "Monday: 9:00 AM – 10:00 PM",
                    "Tuesday: 9:00 AM – 10:00 PM"
                ]
            }
        }
    
    @patch('utilities.map_tools.gmaps')
    def test_is_maps_available(self, mock_gmaps):
        """Test the is_maps_available function."""
        # Test when gmaps is not None
        mock_gmaps.return_value = MagicMock()
        self.assertTrue(is_maps_available())
        
        # Test when gmaps is None
        mock_gmaps.return_value = None
        self.assertFalse(is_maps_available())
    
    @patch('utilities.map_tools.is_maps_available')
    @patch('utilities.map_tools.gmaps')
    def test_search_places_with_valid_api(self, mock_gmaps, mock_is_maps):
        """Test search_places when Google Maps API is available."""
        # Mock API availability
        mock_is_maps.return_value = True
        
        # Mock geocode results
        mock_geocode_result = [{
            "geometry": {
                "location": {
                    "lat": 47.6062,
                    "lng": -122.3321
                }
            }
        }]
        
        # Mock places nearby results
        mock_places_result = {
            "results": [self.test_place]
        }
        
        # Set up the mock return values
        mock_gmaps.geocode.return_value = mock_geocode_result
        mock_gmaps.places_nearby.return_value = mock_places_result
        
        # Call the function
        results = search_places("Seattle, WA", "restaurant")
        
        # Assert that the mocks were called
        mock_gmaps.geocode.assert_called_once_with("Seattle, WA")
        mock_gmaps.places_nearby.assert_called_once()
        
        # Check results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Test Restaurant")
    
    @patch('utilities.map_tools.is_maps_available')
    def test_search_places_without_api(self, mock_is_maps):
        """Test search_places when Google Maps API is not available."""
        # Mock API unavailability
        mock_is_maps.return_value = False
        
        # Call the function
        results = search_places("Seattle, WA", "restaurant")
        
        # Check results
        self.assertEqual(results, [])
    
    @patch('utilities.map_tools.is_maps_available')
    @patch('utilities.map_tools.gmaps')
    def test_get_place_details_with_valid_api(self, mock_gmaps, mock_is_maps):
        """Test get_place_details when Google Maps API is available."""
        # Mock API availability
        mock_is_maps.return_value = True
        
        # Mock place details result
        mock_place_result = {
            "result": self.test_place_details
        }
        
        # Set up the mock return value
        mock_gmaps.place.return_value = mock_place_result
        
        # Call the function
        result = get_place_details("test_place_id")
        
        # Assert that the mock was called
        mock_gmaps.place.assert_called_once()
        
        # Check result
        self.assertEqual(result["name"], "Test Restaurant")
        self.assertEqual(result["rating"], 4.5)
    
    @patch('utilities.map_tools.is_maps_available')
    def test_get_place_details_without_api(self, mock_is_maps):
        """Test get_place_details when Google Maps API is not available."""
        # Mock API unavailability
        mock_is_maps.return_value = False
        
        # Call the function
        result = get_place_details("test_place_id")
        
        # Check result
        self.assertEqual(result, {})
    
    @patch('utilities.map_tools.is_maps_available')
    @patch('utilities.map_tools.gmaps')
    def test_create_map_with_valid_api(self, mock_gmaps, mock_is_maps):
        """Test create_map when Google Maps API is available."""
        # Mock API availability
        mock_is_maps.return_value = True
        
        # Prepare test data
        places = [self.test_place]
        
        # Call the function
        result = create_map(places)
        
        # Check that result is a non-empty string
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
    
    @patch('utilities.map_tools.is_maps_available')
    def test_create_map_without_api(self, mock_is_maps):
        """Test create_map when Google Maps API is not available."""
        # Mock API unavailability
        mock_is_maps.return_value = False
        
        # Call the function
        result = create_map([])
        
        # Check that result is a non-empty string (default map HTML)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


if __name__ == '__main__':
    unittest.main() 