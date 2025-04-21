import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

class TestItinerary(unittest.TestCase):
    """Test cases for the itinerary functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Sample event item for the itinerary
        self.event_item = {
            "type": "event",
            "id": "event_0",
            "title": "Romantic Dinner and Movie",
            "timeline": "- 6:00 PM - 8:00 PM: Dinner at Italian Restaurant - $80\n- 8:30 PM - 10:30 PM: Watch a movie - $30",
            "cost": "110",
            "fit": "Perfect for a casual date night"
        }
        
        # Sample place item for the itinerary
        self.place_item = {
            "type": "place",
            "id": "place_0",
            "name": "Italian Restaurant",
            "address": "123 Main St, Anytown, USA",
            "rating": "4.5",
            "url": "https://maps.google.com/..."
        }
        
        # Sample itinerary with both items
        self.sample_itinerary = [self.event_item, self.place_item]
    
    def test_render_empty_itinerary(self):
        """Test rendering an empty itinerary."""
        html = app.render_itinerary([])
        self.assertIn("Your itinerary is empty", html)
        self.assertIn("itinerary-empty", html)
    
    def test_render_itinerary_with_items(self):
        """Test rendering an itinerary with items."""
        html = app.render_itinerary(self.sample_itinerary)
        
        # Check that both items are in the rendered HTML
        self.assertIn(self.event_item["title"], html)
        self.assertIn(self.place_item["name"], html)
        self.assertIn(self.event_item["cost"], html)
        self.assertIn(self.place_item["address"], html)
        
        # Check for remove buttons
        self.assertIn(f"removeFromItinerary('{self.event_item['id']}')", html)
        self.assertIn(f"removeFromItinerary('{self.place_item['id']}')", html)
    
    def test_add_to_itinerary(self):
        """Test adding an item to the itinerary."""
        # Start with an empty itinerary
        itinerary_state = []
        
        # Add an event item
        event_json = json.dumps(self.event_item)
        html, updated_state = app.add_to_itinerary(itinerary_state, event_json)
        
        # Check that the item was added
        self.assertEqual(len(updated_state), 1)
        self.assertEqual(updated_state[0]["id"], self.event_item["id"])
        
        # Add a place item
        place_json = json.dumps(self.place_item)
        html, updated_state = app.add_to_itinerary(updated_state, place_json)
        
        # Check that the item was added
        self.assertEqual(len(updated_state), 2)
        self.assertEqual(updated_state[1]["id"], self.place_item["id"])
        
        # Try adding a duplicate item (should not be added)
        html, updated_state = app.add_to_itinerary(updated_state, event_json)
        self.assertEqual(len(updated_state), 2)
    
    def test_remove_from_itinerary(self):
        """Test removing an item from the itinerary."""
        # Start with a populated itinerary
        itinerary_state = self.sample_itinerary.copy()
        
        # Remove the event item
        html, updated_state = app.remove_from_itinerary(itinerary_state, self.event_item["id"])
        
        # Check that the item was removed
        self.assertEqual(len(updated_state), 1)
        self.assertEqual(updated_state[0]["id"], self.place_item["id"])
        
        # Remove the place item
        html, updated_state = app.remove_from_itinerary(updated_state, self.place_item["id"])
        
        # Check that the item was removed
        self.assertEqual(len(updated_state), 0)
    
    def test_export_itinerary_as_pdf(self):
        """Test exporting the itinerary as PDF."""
        # Test with an empty itinerary
        result = app.export_itinerary_as_pdf([])
        self.assertIn("Your itinerary is empty", result)
        
        # Test with a populated itinerary
        html = app.export_itinerary_as_pdf(self.sample_itinerary)
        
        # Check that the HTML contains the expected elements
        self.assertIn("Your Perfect Event Itinerary", html)
        self.assertIn(self.event_item["title"], html)
        self.assertIn(self.place_item["name"], html)
        self.assertIn(f"Total Cost: ${self.event_item['cost']}", html)
    
    def test_share_itinerary(self):
        """Test sharing the itinerary."""
        # Test with an empty itinerary
        result = app.share_itinerary([])
        self.assertIn("Your itinerary is empty", result)
        
        # Test with a populated itinerary
        html = app.share_itinerary(self.sample_itinerary)
        
        # Check that the HTML contains the expected elements
        self.assertIn("Share Your Itinerary", html)
        self.assertIn("Copy the link below", html)
        self.assertIn("https://perfectevent.example/share/", html)
    
    @patch('app.generate_event_ideas')
    def test_regenerate_recommendations(self, mock_generate):
        """Test regenerating recommendations."""
        # Mock the generate_event_ideas function
        mock_generate.return_value = (
            "## Event Idea: New Event\n**Total Cost**: $100\n**Why It's a Good Fit**: Test\n### Timeline:\n- 6:00 PM - 8:00 PM: Test activity - $100",
            "<div>Timeline content</div>",
            "<div>Map HTML</div>",
            [{"name": "Test Place", "vicinity": "123 Test St", "rating": 4.5}]
        )
        
        # Create a sample current_recommendations object
        current_recommendations = {
            "inputs": {
                "event_type": "Casual Dating",
                "time_available": 4,
                "budget": 100,
                "vibe": ["Fun", "Relaxed"],
                "location_type": ["Indoors", "Outdoors"],
                "physical_activity": 5,
                "partner_likes": "Italian food",
                "partner_dislikes": "Crowds",
                "partner_hobbies": "Reading",
                "partner_personality": "Introverted",
                "self_preferences": "Casual settings",
                "misc_input": "None",
                "location": "Seattle, WA"
            }
        }
        
        # Call the function
        main_content, timeline, map_html, place_info, new_recommendations = app.regenerate_recommendations(
            current_recommendations, []
        )
        
        # Check that generate_event_ideas was called with the correct parameters
        mock_generate.assert_called_once_with(
            4, 100, ["Fun", "Relaxed"], ["Indoors", "Outdoors"], 5,
            "Italian food", "Crowds", "Reading", "Introverted",
            "Casual settings", "None", "Seattle, WA", "Casual Dating"
        )
        
        # Check that the function returned the expected values
        self.assertIn("New Event", main_content)
        self.assertEqual(timeline, "<div>Timeline content</div>")
        self.assertEqual(map_html, "<div>Map HTML</div>")
        self.assertIsInstance(new_recommendations, dict)

    def test_update_item_time(self):
        """Test updating the time for an item in the itinerary."""
        # Start with a populated itinerary
        itinerary_state = self.sample_itinerary.copy()
        
        # Update time for a place item
        update_data = json.dumps({
            "id": self.place_item["id"],
            "timeType": "start",
            "value": "5:00 PM"
        })
        
        html, updated_state = app.update_item_time(itinerary_state, update_data)
        
        # Check that the time was updated
        self.assertEqual(updated_state[1]["start_time"], "5:00 PM")
        
        # Update end time
        update_data = json.dumps({
            "id": self.place_item["id"],
            "timeType": "end",
            "value": "7:00 PM"
        })
        
        html, updated_state = app.update_item_time(updated_state, update_data)
        
        # Check that the time was updated
        self.assertEqual(updated_state[1]["end_time"], "7:00 PM")
        
        # Check that the HTML contains the updated times
        self.assertIn("5:00 PM", html)
        self.assertIn("7:00 PM", html)

    def test_update_itinerary_order(self):
        """Test updating the order of items in the itinerary."""
        # Start with a populated itinerary
        itinerary_state = self.sample_itinerary.copy()
        
        # Reverse the order
        new_order = json.dumps([self.place_item["id"], self.event_item["id"]])
        
        html, updated_state = app.update_itinerary_order(itinerary_state, new_order)
        
        # Check that the order was updated
        self.assertEqual(updated_state[0]["id"], self.place_item["id"])
        self.assertEqual(updated_state[1]["id"], self.event_item["id"])
        
        # Check that the HTML contains the items in the correct order
        place_index = html.find(self.place_item["name"])
        event_index = html.find(self.event_item["title"])
        self.assertLess(place_index, event_index)

    @patch('app.generate_event_ideas')
    @patch('utilities.map_tools.search_places')
    @patch('utilities.map_tools.get_place_details')
    def test_regenerate_place(self, mock_get_place_details, mock_search_places, mock_generate):
        """Test regenerating a place in the itinerary."""
        # Mock the generate_event_ideas function
        mock_generate.return_value = (
            "## Event Idea: New Event\n**Total Cost**: $100\n**Why It's a Good Fit**: Test\n### Timeline:\n- 6:00 PM - 8:00 PM: Test activity - $100",
            "<div>Timeline content</div>",
            "<div>Map HTML</div>",
            [{"name": "Test Place", "vicinity": "123 Test St", "rating": 4.5}]
        )
        
        # Mock the search_places function
        mock_search_places.return_value = [{"place_id": "new_place_id"}]
        
        # Mock the get_place_details function
        mock_get_place_details.return_value = {
            "name": "New Italian Restaurant",
            "formatted_address": "456 Main St, Anytown, USA",
            "rating": 4.8,
            "url": "https://maps.google.com/..."
        }
        
        # Create a sample current_recommendations object
        current_recommendations = {
            "inputs": {
                "event_type": "Casual Dating",
                "time_available": 4,
                "budget": 100,
                "vibe": ["Fun", "Relaxed"],
                "location_type": ["Indoors", "Outdoors"],
                "physical_activity": 5,
                "partner_likes": "Italian food",
                "partner_dislikes": "Crowds",
                "partner_hobbies": "Reading",
                "partner_personality": "Introverted",
                "self_preferences": "Casual settings",
                "misc_input": "None",
                "location": "Seattle, WA"
            }
        }
        
        # Start with a populated itinerary
        itinerary_state = self.sample_itinerary.copy()
        
        # Test regenerating a place
        main_content, timeline, map_html, place_info, itinerary_html, updated_state = app.regenerate_place(
            itinerary_state, current_recommendations, self.place_item["id"]
        )
        
        # Check that the place was updated
        self.assertEqual(updated_state[1]["name"], "New Italian Restaurant")
        self.assertEqual(updated_state[1]["address"], "456 Main St, Anytown, USA")
        self.assertEqual(updated_state[1]["rating"], 4.8)
        
        # Check that the HTML contains the new place
        self.assertIn("New Italian Restaurant", itinerary_html)
        self.assertIn("456 Main St, Anytown, USA", itinerary_html)
        
        # Test regenerating an event
        main_content, timeline, map_html, place_info, itinerary_html, updated_state = app.regenerate_place(
            itinerary_state, current_recommendations, self.event_item["id"]
        )
        
        # Check that generate_event_ideas was called
        mock_generate.assert_called_with(
            4, 100, ["Fun", "Relaxed"], ["Indoors", "Outdoors"], 5,
            "Italian food", "Crowds", "Reading", "Introverted",
            "Casual settings", "None", "Seattle, WA", "Casual Dating"
        )
        
        # Check that the event was updated
        self.assertEqual(updated_state[0]["title"], "New Event")

if __name__ == '__main__':
    unittest.main()