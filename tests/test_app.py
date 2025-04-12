import os
import unittest
from unittest.mock import patch, MagicMock
import sys
import gradio as gr
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app


class TestApp(unittest.TestCase):
    """Test cases for the main app module."""
    
    @patch('app.is_openai_available')
    @patch('app.is_maps_available')
    def test_app_warnings_with_missing_apis(self, mock_is_maps, mock_is_openai):
        """Test that app shows warnings when APIs are not available."""
        # Mock both APIs as unavailable
        mock_is_openai.return_value = False
        mock_is_maps.return_value = False
        
        # Create a mock Gradio HTML component 
        with patch('gradio.HTML') as mock_html:
            # Create a function to capture the HTML content passed to gr.HTML
            def capture_html(content, **kwargs):
                # Store the content for later assertion
                self.api_warning_content = content
                return MagicMock()  # Return a mock gr.HTML component
                
            mock_html.side_effect = capture_html
            
            # Recreate the app setup to test warning display
            with patch('app.gr.Row'):
                with patch('app.gr.Column'):
                    with patch('app.gr.Markdown'):
                        # Import the app again to trigger the warning HTML creation
                        import importlib
                        importlib.reload(app)
            
            # Check that the captured HTML contains the expected warnings
            self.assertIn("OpenAI API Key Missing", self.api_warning_content)
            self.assertIn("Google Maps API Key Missing", self.api_warning_content)

    @patch('utilities.openai_tools.generate_date_ideas')
    def test_handle_generate(self, mock_generate_date_ideas):
        """Test the handle_generate function."""
        # Mock the generate_date_ideas function
        mock_generate_date_ideas.return_value = (
            "Main Content", 
            "Timeline Content", 
            "<div>Map HTML</div>", 
            [{"name": "Test Place", "vicinity": "123 Test St", "rating": 4.5}]
        )
        
        # Call the function
        main_content, timeline_content, map_html, place_info_html = app.handle_generate(
            "4 hours",
            "$100",
            ["Romantic", "Adventurous"],
            ["Restaurant", "Activity"],
            5,
            "likes",
            "dislikes",
            "hobbies",
            "personality",
            "preferences",
            "misc",
            "Seattle, WA"
        )
        
        # Assert that the mock was called
        mock_generate_date_ideas.assert_called_once()
        
        # Check the outputs
        self.assertEqual(main_content, "Main Content")
        self.assertEqual(timeline_content, "Timeline Content")
        self.assertEqual(map_html, "<div>Map HTML</div>")
        self.assertIn("Test Place", place_info_html)
        self.assertIn("123 Test St", place_info_html)


if __name__ == '__main__':
    unittest.main() 