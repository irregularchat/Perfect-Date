import os
from typing import Dict, Optional, Tuple

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_date_ideas(
    time_available: float,
    budget: float,
    vibe: list,
    location_type: list,
    physical_activity: float,
    partner_likes: str,
    partner_dislikes: str,
    partner_hobbies: str,
    partner_personality: str,
    self_preferences: str,
    misc_input: str
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

    Returns:
        tuple: (main_content, timeline_content) - Formatted text containing the date ideas and separate timeline content
    """
    try:
        # Construct the prompt for OpenAI
        prompt = f"""
        Generate 3 perfect date ideas based on the following preferences:
        
        Time Available: {time_available} hours
        Budget: ${budget}
        Vibe: {', '.join(vibe)}
        Location Type: {', '.join(location_type)}
        Physical Activity Level: {physical_activity}/10
        
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
        6. The date should be location-agnostic (can be done anywhere)
        
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
            
            return main_content, timeline_content
        
        # If no timeline sections found, return original content
        return content, ""
    except Exception as e:
        error_message = f"Error generating date ideas: {str(e)}"
        return error_message, ""