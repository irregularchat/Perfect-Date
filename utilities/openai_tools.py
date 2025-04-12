import os
import re
from typing import Dict, List, Optional, Tuple

from openai import OpenAI
from dotenv import load_dotenv
from utilities.map_tools import search_places_for_date_idea, is_maps_available

# Load environment variables
load_dotenv()

# Initialize OpenAI client with fallback
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None

if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"Error initializing OpenAI client: {str(e)}")

def is_openai_available() -> bool:
    """Check if OpenAI API is available"""
    return client is not None

def generate_date_ideas(
    time_available: float,
    budget: float,
    vibe: list,
    location_type: list,
    physical_activity: float,
    partner_likes: str = "",
    partner_dislikes: str = "",
    partner_hobbies: str = "",
    partner_personality: str = "",
    self_preferences: str = "",
    misc_input: str = "",
    location: str = ""
) -> tuple:
    """
    Generate personalized date ideas based on user preferences.

    Args:
        time_available (float): Time available for the date in hours
        budget (float): Budget for the date in dollars
        vibe (list): List of vibes for the date
        location_type (list): List of location types for the date
        physical_activity (float): Level of physical activity (1-10 scale)
        partner_likes (str): Things the partner likes
        partner_dislikes (str): Things the partner dislikes
        partner_hobbies (str): Partner's hobbies
        partner_personality (str): Partner's personality traits
        self_preferences (str): User's own preferences
        misc_input (str): Miscellaneous information to consider
        location (str, optional): User's location (city, state, country)

    Returns:
        tuple: (main_content, timeline_content, map_html, place_details) - Formatted text containing the date ideas, timeline content, map HTML, and place details
    """
    # Check if OpenAI API is available
    if not is_openai_available():
        error_message = """
        <div style="padding: 20px; text-align: center; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
            <h3 style="color: #6c757d;">Date Generator Feature Not Available</h3>
            <p>The OpenAI API key is not configured. Date generation is disabled.</p>
            <p>To enable this feature, please add your OpenAI API key to the .env file.</p>
        </div>
        """
        return error_message, "", "", []
        
    try:
        # Construct the prompt for OpenAI
        prompt = f"""
        Generate 3 perfect date ideas based on the following preferences:
        
        Time Available: {time_available} hours
        Budget: ${budget}
        Vibe: {', '.join(vibe) if vibe else "Not specified"}
        Location Type: {', '.join(location_type) if location_type else "Not specified"}
        Physical Activity Level: {physical_activity}/10
        Location: {location if location else "Not specified (provide location-agnostic ideas)"}
        
        Partner Preferences:
        - Likes: {partner_likes if partner_likes else "Not specified"}
        - Dislikes: {partner_dislikes if partner_dislikes else "Not specified"}
        - Hobbies: {partner_hobbies if partner_hobbies else "Not specified"}
        - Personality: {partner_personality if partner_personality else "Not specified"}
        
        Your Preferences: {self_preferences if self_preferences else "Not specified"}
        
        Additional Information: {misc_input if misc_input else "None"}
        
        For each date idea, provide:
        1. A descriptive title
        2. A timeline of events with specific time allocations
        3. A detailed cost breakdown for each activity/component
        4. The overall vibe and atmosphere
        5. A brief explanation of why it's a good fit
        6. If location is provided, include location-specific suggestions; otherwise, provide location-agnostic ideas
        
        Format each date idea as follows:
        
        ## Date Idea: [Title]
        - **Total Cost**: [Estimated Total Cost]
        - **Duration**: [Total Time]
        - **Why It's a Good Fit**: [Brief explanation]
        
        ### Timeline:
        - [Start Time] - [End Time]: [Activity] - $[Cost]
        - [Start Time] - [End Time]: [Activity] - $[Cost]
        ...
        
        ### Overall Vibe:
        [Description of the atmosphere and experience]
        
        [Additional details and suggestions to make the date special]
        
        IMPORTANT: Make sure to clearly mark the timeline section with the exact heading "### Timeline:" for each date idea.
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a helpful assistant that generates personalized date ideas based on user preferences.
                    Generate creative, detailed, and practical date ideas that match the specified time, budget, preferences, and physical activity level.
                    
                    For each date idea:
                    1. Create a detailed timeline breaking down activities by time
                    2. Provide specific cost estimates for each component of the date
                    3. Ensure the total cost stays within the specified budget
                    4. Make sure the physical activity level is appropriate (1 = very low, 10 = very high)
                    5. Focus on creating experiences that are memorable and tailored to the couple's interests
                    6. Don't include things that are not possible to do in the allocated time
                    7. If a location is provided, tailor the suggestions to that specific area with local attractions and venues
                    8. If no location is provided, keep the suggestions general and applicable anywhere
                    
                    The output should be well-formatted with clear sections for timeline, costs, and overall experience.
                    """
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract and return the response
        content = response.choices[0].message.content
        
        # Extract timeline sections
        import re
        timeline_sections = []
        
        # Find all timeline sections
        timeline_pattern = r'### Timeline:(.*?)(?=###|$)'
        timeline_matches = re.findall(timeline_pattern, content, re.DOTALL)
        
        # Extract date components for map search
        date_components = []
        if location:
            # Extract activities from timeline
            activity_pattern = r'(?:- \d+:\d+ [AP]M - \d+:\d+ [AP]M: )([^-]+)(?:- \$\d+)'
            for timeline in timeline_matches:
                activities = re.findall(activity_pattern, timeline)
                date_components.extend([activity.strip() for activity in activities if activity.strip()])
        
        # Search for places if location is provided and maps are available
        map_html = ""
        place_details = []
        if location and date_components and is_maps_available():
            map_html, place_details = search_places_for_date_idea(location, date_components)
        elif location and date_components and not is_maps_available():
            map_html = """
            <div style="padding: 20px; text-align: center; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                <h3 style="color: #6c757d;">Maps Feature Not Available</h3>
                <p>The Google Maps API key is not configured. Location-based recommendations are disabled.</p>
                <p>To enable this feature, please add your Google Maps API key to the .env file.</p>
            </div>
            """
        
        if timeline_matches:
            timeline_content = "## Timelines for Date Packages\n\n"
            
            # Extract date idea titles
            title_pattern = r'## Date Idea: (.*?)[\r\n]'
            titles = re.findall(title_pattern, content)
            
            # Combine titles with their respective timelines
            for i, timeline in enumerate(timeline_matches):
                if i < len(titles):
                    timeline_content += f"### Timeline for {titles[i]}\n{timeline.strip()}\n\n"
                else:
                    timeline_content += f"### Timeline for Date Idea {i+1}\n{timeline.strip()}\n\n"
            
            # Remove timeline sections from main content to avoid duplication
            main_content = re.sub(timeline_pattern, '', content)
            
            return main_content, timeline_content, map_html, place_details
        
        # If no timeline sections found, return original content
        return content, "", map_html, place_details
    except Exception as e:
        error_message = f"""
        <div style="padding: 20px; text-align: center; background-color: #fff3f3; border-radius: 8px; border: 1px solid #ffcccb;">
            <h3 style="color: #d9534f;">Error Generating Date Ideas</h3>
            <p>{str(e)}</p>
            <p>Please try again with different inputs or check your API key configuration.</p>
        </div>
        """
        return error_message, "", "", []