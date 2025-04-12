import os
import unittest
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.map_tools import is_maps_available
from utilities.openai_tools import is_openai_available


class TestEnvironmentVariables(unittest.TestCase):
    """Test cases for checking environment variables."""

    def test_google_maps_api_key(self):
        """Test that Google Maps API key is set in environment."""
        google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.assertIsNotNone(google_maps_key, "GOOGLE_MAPS_API_KEY environment variable is not set")
        
        # Check if the API is actually available through the function
        if google_maps_key:
            print(f"GOOGLE_MAPS_API_KEY length: {len(google_maps_key)}")
            # If API key is really available, maps should be available
            availability = is_maps_available()
            self.assertTrue(availability, "Maps API key is set but the API client couldn't be initialized")

    def test_openai_api_key(self):
        """Test that OpenAI API key is set in environment."""
        openai_key = os.getenv("OPENAI_API_KEY")
        self.assertIsNotNone(openai_key, "OPENAI_API_KEY environment variable is not set")
        
        # Check if the API is actually available through the function
        if openai_key:
            print(f"OPENAI_API_KEY length: {len(openai_key)}")
            # If API key is really available, OpenAI should be available
            availability = is_openai_available()
            self.assertTrue(availability, "OpenAI API key is set but the API client couldn't be initialized")


if __name__ == '__main__':
    unittest.main() 