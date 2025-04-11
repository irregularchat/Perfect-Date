import os
from typing import Dict, Optional

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_date_ideas(
    time_available: str,
    budget: str,
    vibe: list,
    location_type: list,
    physical_activity: str,
    partner_questions: str
) -> str:
    """
    Generate personalized date ideas based on user preferences.

    Args:
        time_available (str): Time available for the date
        budget (str): Budget for the date
        vibe (list): List of vibes for the date
        location_type (list): List of location types for the date
        physical_activity (str): Level of physical activity
        partner_questions (str): Partner's preferences

    Returns:
        str: Formatted text containing the date ideas
    """
    try:
        # Construct the prompt for OpenAI
        prompt = f"""
        Generate 3 perfect date ideas based on the following preferences:
        
        Time Available: {time_available}
        Budget: {budget}
        Vibe: {', '.join(vibe)}
        Location Type: {', '.join(location_type)}
        Physical Activity Level: {physical_activity}
        Partner Preferences: {partner_questions}
        
        For each date idea, provide:
        1. A descriptive title
        2. Estimated cost range
        3. Estimated time commitment
        4. A brief explanation of why it's a good fit
        5. The date should be location-agnostic (can be done anywhere)
        
        Format each date idea as follows:
        
        ## Date Idea: [Title]
        - **Cost**: [Estimated Cost Range]
        - **Time**: [Estimated Time Commitment]
        - **Why It's a Good Fit**: [Brief explanation]
        
        [Brief description of the date idea with specific activities]
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
                    Make sure the physical activity level is appropriate for the date idea.
                    Focus on creating experiences that are memorable and tailored to the couple's interests.
                    Don't include things that are not possible to do in the location or time of the date.
                    Include sliders instead of buttons for the user to select time available and budget.
                    For vibe and Location Type, put all the options as buttons for the user to select and include an "I don't know" option.
                    """
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract and return the response
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating date ideas: {str(e)}" 