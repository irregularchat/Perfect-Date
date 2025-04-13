import os
import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.openai_tools import is_openai_available, generate_date_ideas, generate_event_ideas, mock_openai_api


class TestOpenAITools(unittest.TestCase):
    """Test cases for the OpenAI tools module."""

    def setUp(self):
        """Set up test environment."""
        # Create test inputs
        self.test_time = 4
        self.test_budget = 100
        self.test_vibe = ["Romantic", "Adventurous"]
        self.test_location_type = ["Restaurant", "Activity"]
        self.test_physical_activity = 5
        self.test_location = "Seattle, WA"
        
        # Sample OpenAI response
        self.sample_date_idea = """
        ## Date Idea: Sunset Picnic and Stargazing
        - **Total Cost**: $75
        - **Duration**: 4 hours
        - **Why It's a Good Fit**: Combines romance and adventure without being too physically demanding.
        
        ### Timeline:
        - 5:00 PM - 6:30 PM: Shop for gourmet picnic supplies at Pike Place Market - $40
        - 6:30 PM - 7:00 PM: Drive to Kerry Park for sunset views - $0
        - 7:00 PM - 8:30 PM: Enjoy picnic dinner with city and mountain views - $0
        - 8:30 PM - 9:00 PM: Drive to nearby stargazing spot - $5 (parking)
        - 9:00 PM - 10:00 PM: Stargazing with thermos of hot chocolate - $0
        
        ### Overall Vibe:
        The atmosphere during this date will be relaxed, cozy, and intimate. Starting with the bustle of Pike Place Market allows you to select items together, then transitioning to a peaceful picnic creates a romantic setting. The stargazing portion adds a sense of adventure and wonder, perfect for deep conversations under the night sky.
        
        For an extra special touch, bring a portable speaker for some quiet background music during your picnic, and download a stargazing app to identify constellations together.
        """
        
        # Sample incorrectly formatted OpenAI response
        self.malformed_date_idea = """
        Here's a date idea for you:
        
        A nice dinner at a local restaurant followed by a walk in the park.
        It should cost about $100 and take 3 hours.
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
        
        # Assert that the mock was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that the response was processed correctly
        self.assertIn("Date Idea: Sunset Picnic", main_content)
        self.assertIn("Timeline for Sunset Picnic", timeline_content)
        self.assertEqual(map_html, "<div>Map HTML</div>")
        self.assertEqual(place_details, [{"name": "Test Place", "vicinity": "123 Test St"}])
    
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
        self.assertIn("Date Generator Feature Not Available", main_content)
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
        self.assertIn("Error Generating Date Ideas", main_content)
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
            "preferences", "misc", self.test_location, "Casual Dating", 2
        )
        
        # Assert that the mock was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that the response was processed correctly but without map content
        self.assertIn("Date Idea: Sunset Picnic", main_content)
        self.assertIn("Timeline for Sunset Picnic", timeline_content)
        # Map should be empty when maps API is disabled
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
        mock_client.chat.completions.create.assert_called_once()
        
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
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that an error message is returned for empty response
        self.assertIn("No date ideas were generated", main_content)
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
        
        # Call the function
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            self.test_time, self.test_budget, self.test_vibe, self.test_location_type,
            self.test_physical_activity, "likes", "dislikes", "hobbies", "personality",
            "preferences", "misc", self.test_location, "Casual Dating", 2
        )
        
        # Assert that the mock was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that the response was processed correctly
        self.assertIn("Date Idea: Sunset Picnic", main_content)
        self.assertIn("Timeline for Sunset Picnic", timeline_content)
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
    
    # Check that mock content was returned
    assert "Date Idea:" in main_content
    assert "Timeline" in timeline_content
    assert map_html != ""
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
    assert "Event Idea:" in main_content
    assert "Timeline" in timeline_content
    assert map_html != ""
    assert len(place_details) > 0
    
    # Reset mock mode
    mock_openai_api(False)


if __name__ == '__main__':
    unittest.main() 