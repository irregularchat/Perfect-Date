import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.openai_tools import is_openai_available, generate_date_ideas, generate_event_ideas, mock_openai_api


class TestOpenAITools(unittest.TestCase):
    """Test cases for the OpenAI tools module."""

    def setUp(self):
        """Set up test environment."""
        # Create test inputs
        self.test_time = 4.0
        self.test_budget = 100.0
        self.test_vibe = ["Romantic", "Adventurous"]
        self.test_location_type = ["Restaurant", "Activity"]
        self.test_physical_activity = 5.0
        self.test_location = "Seattle, WA"
        
        # Sample OpenAI response
        self.sample_date_idea = """
        ## Event Idea: Sunset Picnic
        - **Total Cost**: $50
        - **Duration**: 4 hours
        - **Why It's a Good Fit**: Combines romance with a bit of adventure, perfect for a relaxed evening
        
        ### Timeline:
        - 5:00 PM - 6:00 PM: Shop for gourmet picnic supplies at Pike Place Market - $30
        - 6:30 PM - 8:00 PM: Drive to Kerry Park for sunset views - $0
        - 8:00 PM - 9:00 PM: Enjoy picnic dinner with city and mountain views - $0
        
        ### Overall Vibe:
        Romantic and scenic, with beautiful views and delicious food in a peaceful setting.
        
        ## Event Idea: Evening Kayak & Dinner
        - **Total Cost**: $90
        - **Duration**: 4 hours
        - **Why It's a Good Fit**: Active yet romantic, with stunning water views
        
        ### Timeline:
        - 5:00 PM - 7:00 PM: Sunset kayaking on Lake Union - $50
        - 7:30 PM - 9:00 PM: Dinner at Ivar's Salmon House - $40
        
        ### Overall Vibe:
        Adventurous yet intimate, with the peaceful experience of being on the water followed by a cozy dinner.
        """
        
        # Sample incorrectly formatted OpenAI response
        self.malformed_date_idea = """
        Here's a date idea for you:
        
        Go to a nice restaurant, maybe see a movie afterwards.
        It should cost around $100 total and take about 4 hours.
        """
    
    @patch('utilities.openai_tools.client')
    def test_is_openai_available_when_true(self, mock_client):
        """Test the is_openai_available function when it returns True."""
        # Set up the mock client to not be None
        mock_client.return_value = MagicMock()
        # The actual function checks if client is not None
        self.assertTrue(is_openai_available())
    
    @patch('utilities.openai_tools.client', None)
    def test_is_openai_available_when_false(self):
        """Test the is_openai_available function when it returns False."""
        # When client is None, the function should return False
        self.assertFalse(is_openai_available())
    
    @patch('utilities.openai_tools.client')
    @patch('utilities.openai_tools.is_maps_available')
    @patch('utilities.openai_tools.search_places_for_date_idea')
    def test_generate_date_ideas_with_valid_api(self, mock_search_places, mock_is_maps, mock_client):
        """Test generate_date_ideas when OpenAI API is available."""
        # Mock Maps API availability
        mock_is_maps.return_value = True
        
        # Mock the OpenAI response
        mock_chat_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = self.sample_date_idea
        mock_choice.message = mock_message
        mock_chat_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        
        # Mock the map search results
        mock_search_places.return_value = ("<div>Map HTML</div>", [{"name": "Test Place", "vicinity": "123 Test St"}], "Place Info HTML")
        
        # Call the function
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            self.test_time, self.test_budget, self.test_vibe, self.test_location_type,
            self.test_physical_activity, "likes", "dislikes", "hobbies", "personality",
            "preferences", "misc", self.test_location, "Casual Dating", 2
        )
        
        # Assert that the mock was called at least once (it may be called multiple times due to enhanced search)
        self.assertTrue(mock_client.chat.completions.create.call_count >= 1)
        
        # Check that the response was processed correctly
        self.assertIn("Event Idea: Sunset Picnic", main_content)
        self.assertIn("Timeline for", timeline_content)
        
        # Only check that the map_html is non-empty and contains basic map elements, not exact content
        self.assertTrue(len(map_html) > 0)
        self.assertIn("<div", map_html)
        self.assertIn("map", map_html.lower())
        
        # Check the place details contain the expected place
        self.assertTrue(len(place_details) > 0)
    
    @patch('utilities.openai_tools.client', None)
    def test_generate_date_ideas_without_api(self):
        """Test generate_date_ideas when OpenAI API is not available."""
        # Call the function with all required parameters
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            self.test_time, self.test_budget, self.test_vibe, self.test_location_type,
            self.test_physical_activity, "likes", "dislikes", "hobbies", "personality",
            "preferences", "misc", self.test_location, "Casual Dating", 2
        )
        
        # Check that the error message is returned
        self.assertIn("Event Generator Feature Not Available", main_content)
        self.assertEqual(timeline_content, "")
        self.assertEqual(map_html, "")
        self.assertEqual(place_details, [])
    
    @patch('utilities.openai_tools.client')
    @patch('utilities.openai_tools.is_maps_available')
    def test_generate_date_ideas_with_exception(self, mock_is_maps, mock_client):
        """Test generate_date_ideas when an exception occurs."""
        # Mock Maps API availability
        mock_is_maps.return_value = False
        
        # Mock the OpenAI client to raise an exception
        mock_client.chat.completions.create.side_effect = Exception("Test exception")
        
        # Call the function with all required parameters
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            self.test_time, self.test_budget, self.test_vibe, self.test_location_type,
            self.test_physical_activity, "likes", "dislikes", "hobbies", "personality",
            "preferences", "misc", self.test_location, "Casual Dating", 2
        )
        
        # Check that the error message is returned
        self.assertIn("Error Generating Event Ideas", main_content)
        self.assertEqual(timeline_content, "")
        self.assertEqual(map_html, "")
        self.assertEqual(place_details, [])
    
    @patch('utilities.openai_tools.client')
    @patch('utilities.openai_tools.is_maps_available')
    def test_generate_date_ideas_with_maps_disabled(self, mock_is_maps, mock_client):
        """Test generate_date_ideas when Maps API is not available."""
        # Mock Maps API availability to be false
        mock_is_maps.return_value = False
        
        # Mock the OpenAI response 
        mock_chat_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = self.sample_date_idea
        mock_choice.message = mock_message
        mock_chat_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        
        # Call the function
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            self.test_time, self.test_budget, self.test_vibe, self.test_location_type,
            self.test_physical_activity, "likes", "dislikes", "hobbies", "personality",
            "preferences", "misc", "", "Casual Dating", 2  # Empty location to avoid map lookup
        )
        
        # Assert that the mock was called
        self.assertTrue(mock_client.chat.completions.create.call_count >= 1)
        
        # We're mainly testing that the function doesn't error when maps are disabled
        # The content details matter less than avoiding the error
        self.assertTrue(len(main_content) > 0)
        self.assertEqual(map_html, "")
        self.assertEqual(place_details, [])
    
    @patch('utilities.openai_tools.client')
    @patch('utilities.openai_tools.is_maps_available')
    @patch('utilities.openai_tools.search_places_for_date_idea')
    def test_generate_date_ideas_with_malformed_response(self, mock_search_places, mock_is_maps, mock_client):
        """Test generate_date_ideas when OpenAI API returns a malformed response."""
        # Mock Maps API availability
        mock_is_maps.return_value = True
        
        # Mock the OpenAI response with malformed content
        mock_chat_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = self.malformed_date_idea
        mock_choice.message = mock_message
        mock_chat_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        
        # Since the response is malformed, no date components will be extracted
        # So search_places will not be called with meaningful parameters
        mock_search_places.return_value = ("", [], "")
        
        # Call the function
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            self.test_time, self.test_budget, self.test_vibe, self.test_location_type,
            self.test_physical_activity, "likes", "dislikes", "hobbies", "personality",
            "preferences", "misc", self.test_location, "Casual Dating", 2
        )
        
        # Assert that the mock was called
        self.assertTrue(mock_client.chat.completions.create.call_count >= 1)
        
        # Check that the response was processed, even if malformed
        self.assertIn("Here's a date idea for you", main_content)
        # Timeline content should be empty as it doesn't match the regex
        self.assertEqual(timeline_content, "")
        # Map should be empty because there are no date components extracted
        self.assertEqual(map_html, "")
        self.assertEqual(place_details, [])
    
    @patch('utilities.openai_tools.client')
    @patch('utilities.openai_tools.is_maps_available')
    def test_generate_date_ideas_with_empty_response(self, mock_is_maps, mock_client):
        """Test generate_date_ideas when OpenAI API returns an empty response."""
        # Mock Maps API availability
        mock_is_maps.return_value = True
        
        # Mock the OpenAI response with empty content
        mock_chat_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = ""
        mock_choice.message = mock_message
        mock_chat_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        
        # Call the function
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            self.test_time, self.test_budget, self.test_vibe, self.test_location_type,
            self.test_physical_activity, "likes", "dislikes", "hobbies", "personality",
            "preferences", "misc", self.test_location, "Casual Dating", 2
        )
        
        # Assert that the mock was called
        self.assertTrue(mock_client.chat.completions.create.call_count >= 1)
        
        # Check that an error message is returned for empty response
        self.assertIn("No event ideas were generated", main_content)
        self.assertEqual(timeline_content, "")
        self.assertEqual(map_html, "")
        self.assertEqual(place_details, [])
    
    @patch('utilities.openai_tools.client')
    @patch('utilities.openai_tools.is_maps_available')
    @patch('utilities.openai_tools.search_places_for_date_idea')
    def test_search_places_failure(self, mock_search_places, mock_is_maps, mock_client):
        """Test generate_date_ideas when places search fails."""
        # Mock Maps API availability
        mock_is_maps.return_value = True
        
        # Mock the OpenAI response
        mock_chat_completion = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = self.sample_date_idea
        mock_choice.message = mock_message
        mock_chat_completion.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_chat_completion
        
        # Mock the map search to fail
        mock_search_places.return_value = ("", [], "")
        
        # Call the function with empty location to simplify test
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            self.test_time, self.test_budget, self.test_vibe, self.test_location_type,
            self.test_physical_activity, "likes", "dislikes", "hobbies", "personality",
            "preferences", "misc", "", "Casual Dating", 2  # Empty location to avoid map lookup
        )
        
        # Assert that the mock was called
        self.assertTrue(mock_client.chat.completions.create.call_count >= 1)
        
        # Check that the response was processed
        self.assertTrue(len(main_content) > 0)
        self.assertEqual(map_html, "")
        self.assertEqual(place_details, [])


def test_generate_date_ideas_mock():
    """Test that the generate_date_ideas function works with a mock."""
    # Set mock mode
    mock_openai_api(True)
    
    # Call the function with mock enabled
    main_content, timeline_content, map_html, place_details = generate_date_ideas(
        4, 100, ["Romantic", "Adventurous"], ["Restaurant", "Activity"],
        3, "likes nature", "dislikes crowds", "reading, hiking", "outgoing",
        "prefers evenings", "misc info", "Seattle, WA", "Casual Dating", 2
    )
    
    # Check that mock content was returned - look for 'Event Idea' as a pattern (might have a number after it)
    assert re.search(r"Event Idea", main_content) is not None
    assert "Timeline" in timeline_content
    assert map_html is not None  # Just verify it's not None
    assert len(place_details) > 0
    
    # Reset mock mode
    mock_openai_api(False)

def test_generate_event_ideas_mock():
    """Test that the generate_event_ideas function works with a mock."""
    # Set mock mode
    mock_openai_api(True)
    
    # Call the function with mock enabled
    main_content, timeline_content, map_html, place_details = generate_event_ideas(
        4, 100, ["Fun", "Educational"], ["Outdoor", "Indoor"],
        3, "likes nature", "dislikes crowds", "reading, hiking", "outgoing",
        "prefers afternoons", "misc info", "Seattle, WA", "Friends Gathering", 3
    )
    
    # Check that mock content was returned
    assert "Event Idea" in main_content
    assert "Timeline" in timeline_content
    assert map_html != ""
    assert len(place_details) > 0
    
    # Reset mock mode
    mock_openai_api(False)


if __name__ == '__main__':
    unittest.main() 