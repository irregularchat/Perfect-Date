import os
import unittest
from unittest.mock import patch, MagicMock
import sys
from datetime import datetime
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.map_tools import is_maps_available, search_places, get_place_details, create_map, get_busy_status, search_places_for_date_idea


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
            },
            "opening_hours": {
                "open_now": True
            },
            "user_ratings_total": 150
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
                ],
                "open_now": True
            }
        }
    
    @patch('utilities.map_tools.gmaps', return_value=MagicMock())
    def test_is_maps_available_with_api(self, mock_gmaps):
        """Test is_maps_available when API is available."""
        # In the actual implementation, the function checks if gmaps is not None
        mock_gmaps.return_value = MagicMock()  # This won't matter, the patch is to set gmaps
        self.assertTrue(is_maps_available())
    
    @patch('utilities.map_tools.gmaps', None)
    def test_is_maps_available_without_api(self):
        """Test is_maps_available when API is not available."""
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
        
        # Mock places results
        mock_places_result = {
            "results": [self.test_place]
        }
        
        # Set up the mock return values
        mock_gmaps.geocode.return_value = mock_geocode_result
        mock_gmaps.places.return_value = mock_places_result
        mock_gmaps.places_nearby.return_value = {"results": []}
        
        # Call the function
        results = search_places("Seattle, WA", "restaurant")
        
        # Assert that the mocks were called
        mock_gmaps.geocode.assert_called_once_with("Seattle, WA")
        # We expect places to be called instead of places_nearby in the primary flow
        self.assertTrue(mock_gmaps.places.called)
        
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
    
    @patch('utilities.map_tools.folium.Map')
    @patch('utilities.map_tools.folium.Marker')
    @patch('utilities.map_tools.is_maps_available')
    def test_create_map_with_api(self, mock_is_maps, mock_marker, mock_map):
        """Test create_map when Maps API is available."""
        mock_is_maps.return_value = True
        
        # Mock Map and Marker objects
        mock_map_instance = MagicMock()
        mock_map.return_value = mock_map_instance
        
        mock_marker_instance = MagicMock()
        mock_marker.return_value = mock_marker_instance
        
        # Call function
        map_html, places_info, table_html = create_map([self.test_place], "Seattle, WA")
        
        # Assert map was created
        mock_map.assert_called_once()
        self.assertEqual(len(places_info), 1)
    
    @patch('utilities.map_tools.is_maps_available')
    def test_create_map_without_api(self, mock_is_maps):
        """Test create_map when Maps API is not available."""
        mock_is_maps.return_value = False
        
        # Call function
        map_html, places_info, table_html = create_map([], "Seattle, WA")
        
        # Assert error message was returned
        self.assertEqual(map_html, "")
        self.assertEqual(places_info, [])
        self.assertEqual(table_html, "")
    
    @patch('utilities.map_tools.is_maps_available')
    def test_create_map_without_places(self, mock_is_maps):
        """Test create_map when no places are provided."""
        mock_is_maps.return_value = True
        
        # Call function with empty places list
        map_html, places_info, table_html = create_map([], "Seattle, WA")
        
        # Assert error message was returned
        self.assertEqual(map_html, "")
        self.assertEqual(places_info, [])
        self.assertEqual(table_html, "")
    
    @patch('utilities.map_tools.datetime')
    def test_get_busy_status(self, mock_datetime):
        """Test get_busy_status function."""
        # Set up mock for current time (Friday at 6 PM)
        mock_now = MagicMock()
        mock_now.weekday.return_value = 4  # Friday (0-6, Monday is 0)
        mock_now.hour = 18  # 6:00 PM
        mock_datetime.now.return_value = mock_now
        
        # Test place with opening hours during peak time
        place_with_hours = {
            "name": "Test Restaurant",
            "rating": 4.5,
            "user_ratings_total": 150,
            "opening_hours": {
                "open_now": True
            }
        }
        
        busy_status = get_busy_status(place_with_hours)
        
        # Friday at 6 PM should be busy for a highly rated place
        self.assertEqual(busy_status, "Might be busy right now")
        
        # Test place without opening hours
        place_without_hours = {
            "name": "Place Without Hours"
            # No opening_hours field
        }
        
        busy_status = get_busy_status(place_without_hours)
        self.assertEqual(busy_status, "")
        
        # Test place with opening_hours showing it's closed
        closed_place = {
            "name": "Closed Place",
            "opening_hours": {"open_now": False}
        }
        
        busy_status = get_busy_status(closed_place)
        self.assertEqual(busy_status, "Currently closed")

    @patch('utilities.map_tools.is_maps_available')
    @patch('utilities.map_tools.search_places')
    @patch('utilities.map_tools.get_place_details')
    @patch('utilities.map_tools.create_map')
    def test_search_places_for_date_idea(self, mock_create_map, mock_get_place_details, mock_search_places, mock_is_maps):
        """Test search_places_for_date_idea function."""
        # Mock API availability
        mock_is_maps.return_value = True
        
        # Mock search_places to return a list with one place
        mock_search_places.return_value = [self.test_place]
        
        # Mock get_place_details to return place details
        mock_get_place_details.return_value = self.test_place_details
        
        # Mock create_map to return the expected tuple values
        mock_create_map.return_value = ("<div>Map HTML</div>", [self.test_place_details, self.test_place_details], "place info")
        
        # Call the function
        map_html, places, place_info_html = search_places_for_date_idea("Seattle, WA", ["restaurant", "cafe"])
        
        # Check that the mocks were called
        mock_search_places.assert_called()
        mock_get_place_details.assert_called()
        mock_create_map.assert_called()
        
        # Check results
        self.assertEqual(map_html, "<div>Map HTML</div>")
        self.assertEqual(len(places), 2)  # Two components, one place each
        self.assertIsInstance(place_info_html, str)
        
        # Test when Maps API is not available
        mock_is_maps.return_value = False
        map_html, places, place_info_html = search_places_for_date_idea("Seattle, WA", ["restaurant"])
        self.assertIn("Maps Feature Not Available", map_html)
        self.assertEqual(places, [])
        self.assertEqual(place_info_html, "")


if __name__ == '__main__':
    unittest.main() 