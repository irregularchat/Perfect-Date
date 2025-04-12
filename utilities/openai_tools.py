import os
import re
from typing import Dict, List, Optional, Tuple

from openai import OpenAI
from dotenv import load_dotenv
from utilities.map_tools import search_places_for_date_idea, is_maps_available, get_busy_status, search_places, get_place_details, create_map

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
        
        # Check for empty content
        if not content or content.strip() == "":
            error_message = """
            <div style="padding: 20px; text-align: center; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
                <h3 style="color: #6c757d;">No date ideas were generated</h3>
                <p>The AI could not generate any date ideas. Please try again with different preferences.</p>
            </div>
            """
            return error_message, "", "", []
        
        # Extract timeline sections
        timeline_sections = []
        
        # Find all timeline sections
        timeline_pattern = r'### Timeline:(.*?)(?=###|$)'
        timeline_matches = re.findall(timeline_pattern, content, re.DOTALL)
        
        # Extract date components for map search
        date_components = []
        place_names = []
        if location:
            # Extract activities from timeline
            activity_pattern = r'(?:- \d+:\d+ [AP]M - \d+:\d+ [AP]M: )([^-]+)(?:- \$\d+)'
            
            # Enhanced pattern to extract places with more context
            place_patterns = [
                r'(?:at|in|to|through|visit|explore) ([\w\s\',&-]+)(?:[\s,.-]|$)',  # Standard patterns
                r'(?:the|a) ([\w\s\',&-]+ (?:Park|Garden|Museum|Gallery|Restaurant|Café|Cafe|Theatre|Theater|Studio|Shop|Market|Bar|Mall|Center|Plaza))',  # Places with type
                r'([\w\s\',&-]+ (?:Park|Garden|Museum|Gallery|Restaurant|Café|Cafe|Theatre|Theater|Studio|Shop|Market|Bar|Mall|Center|Plaza))',  # Just place types
            ]
            
            # Track already processed places to avoid duplicates
            processed_place_ids = set()
            place_details_list = []  # Collect all unique place details
            activities_list = []     # Collect activities for context
            place_names = []         # Store unique place names
            
            # Track which places belong to which timeline
            timeline_places = []
            
            for timeline in timeline_matches:
                # Track places for this specific timeline
                current_timeline_places = []
                
                # Extract activities with full context
                activities = re.findall(activity_pattern, timeline)
                cleaned_activities = [activity.strip() for activity in activities if activity.strip()]
                activities_list.extend(cleaned_activities)
                
                # Find place names using multiple patterns for better coverage
                all_matches = []
                for pattern in place_patterns:
                    matches = re.findall(pattern, timeline, re.IGNORECASE)
                    all_matches.extend(matches)
                
                # Process and clean up the matches
                for place in all_matches:
                    place_name = place.strip()
                    # Filter out small words and common false positives
                    if (len(place_name) > 3 and 
                        place_name.lower() not in ["this", "that", "then", "there", "home", "free", "lunch", "dinner"] and
                        place_name not in place_names):
                        place_names.append(place_name)
                        current_timeline_places.append(place_name)
                
                # Add the current timeline's places to our tracking list
                timeline_places.append(current_timeline_places)
            
            # Add the place names to the search components
            date_components = []
            date_components.extend(activities_list)
            date_components.extend(place_names)
        
        # Search for place details if we have a location
        if location and is_maps_available() and place_names:
            # Track used place IDs to avoid duplicates
            unique_place_ids = set()
            place_info_by_name = {}  # Initialize dictionary to store place info by name
            
            # Use GPT to enhance the search queries for better context matching
            enhanced_queries = {}
            if len(place_names) > 0 and is_openai_available():
                try:
                    # Create a prompt for GPT to improve search queries with activity context
                    context_prompt = f"""
                    I need to search for these places in {location} for date ideas. 
                    
                    Places mentioned:
                    {", ".join(place_names)}
                    
                    Activities in the date plan:
                    {", ".join(activities_list)}
                    
                    For each place, generate an improved search query that will help find the most relevant location in Google Maps.
                    Use the context from the activities to understand what type of place it likely is (e.g., restaurant, park, museum, etc.).
                    
                    For example, if the place is "Joe's" and the activities mention "coffee", the improved query might be "Joe's Coffee Shop in {location}".
                    
                    Return the results in this format:
                    Place name: Improved search query
                    """
                    
                    # Call GPT to generate improved search queries
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",  # Using a smaller model for efficiency
                        messages=[
                            {"role": "system", "content": "You help improve search queries for Google Maps API by adding relevant context to place names."},
                            {"role": "user", "content": context_prompt}
                        ]
                    )
                    
                    # Parse the improved queries from GPT's response
                    improved_queries_text = response.choices[0].message.content
                    
                    # Process each line to extract place name and improved query
                    for line in improved_queries_text.strip().split('\n'):
                        if ':' in line:
                            parts = line.split(':', 1)
                            place_name = parts[0].strip()
                            improved_query = parts[1].strip()
                            
                            # Match to our original place names (case insensitive)
                            for original_name in place_names:
                                if original_name.lower() in place_name.lower() or place_name.lower() in original_name.lower():
                                    enhanced_queries[original_name] = improved_query
                    
                    print(f"Enhanced search queries: {enhanced_queries}")
                except Exception as e:
                    print(f"Error generating enhanced queries: {str(e)}")
            
            # Search for each place with improved queries when available
            for place_name in place_names:
                # Skip small words that are likely not actual place names
                if len(place_name) <= 3:
                    continue
                
                # Use the enhanced query if available, otherwise use the original name
                search_query = enhanced_queries.get(place_name, f"{place_name} in {location}")
                print(f"Searching for place: {search_query}")
                
                # Search with the improved query
                search_results = search_places(location, search_query)
                
                # If no results, try a more generic search as fallback
                if not search_results or len(search_results) == 0:
                    print(f"No results found for '{search_query}', trying fallback search")
                    
                    # Try with just the place name if it contains multiple words
                    if len(place_name.split()) > 1:
                        search_results = search_places(location, place_name)
                    
                    # If still no results, try searching for the place type if we can extract it
                    if (not search_results or len(search_results) == 0) and any(type_word in place_name.lower() for type_word in ["restaurant", "café", "cafe", "park", "garden", "museum", "theater", "theatre", "gallery"]):
                        for type_word in ["restaurant", "café", "cafe", "park", "garden", "museum", "theater", "theatre", "gallery"]:
                            if type_word in place_name.lower():
                                search_results = search_places(location, type_word)
                                if search_results and len(search_results) > 0:
                                    print(f"Found results using type: {type_word}")
                                    break
                
                if search_results and len(search_results) > 0:
                    # Get details for the most relevant result
                    result = search_results[0]
                    place_id = result.get('place_id')
                    
                    # Skip if we've already seen this place ID
                    if place_id in unique_place_ids:
                        print(f"Skipping duplicate place: {place_name}")
                        continue
                    
                    # Add to tracking set
                    unique_place_ids.add(place_id)
                    
                    # Get detailed place information
                    place_details = get_place_details(place_id)
                    if place_details:
                        # Store by lowercase name for case-insensitive matching
                        place_key = place_name.lower()
                        place_info_by_name[place_key] = place_details
                        
                        # Also add to our list of place details for the map
                        place_details_list.append(place_details)
        
        # Search for places if location is provided and maps are available
        map_html = ""
        if location and is_maps_available():
            # Generate map with the place details we've already collected
            if place_details_list:
                map_html, _, _ = create_map(place_details_list, location)
        
        # Format timeline content
        timeline_content = ""
        if timeline_matches:
            # Use pure HTML with no markdown that might confuse the Gradio Markdown component
            timeline_content = "<div class='timelines-wrapper'>"
            timeline_content += "<h2 style='color: #ff6b6b; border-bottom: 2px solid #ffe66d; padding-bottom: 10px; margin-top: 0; margin-bottom: 20px; font-size: 24px; font-weight: bold; display: block; width: 100%;'>Timelines for Date Packages</h2>"
            
            # Extract date idea titles
            title_pattern = r'## Date Idea: (.*?)[\r\n]'
            titles = re.findall(title_pattern, content)
            
            # Combine titles with their respective timelines
            for i, timeline in enumerate(timeline_matches):
                title = titles[i] if i < len(titles) else f"Date Idea {i+1}"
                
                # Get the places specific to this timeline
                current_timeline_places = timeline_places[i] if i < len(timeline_places) else []
                
                # Process the timeline to make place names clickable
                processed_timeline = timeline
                
                # Look for mentions of place names - but only ones relevant to this timeline
                for place_name in current_timeline_places:
                    place_key = place_name.lower()
                    if place_key in place_info_by_name:
                        # Create a regex pattern to find the place name with word boundaries
                        place_pattern = re.compile(r'\b' + re.escape(place_name) + r'\b')
                        
                        # Create clickable span with data attributes
                        place_id = f"place_{i}_{place_names.index(place_name)}"
                        
                        # Create clickable span with data attributes
                        place_html = f'<span class="clickable-place" data-place-id="{place_id}">{place_name}</span>'
                        processed_timeline = place_pattern.sub(place_html, processed_timeline)
                
                # Format the timeline with proper HTML
                formatted_timeline = ""
                for line in processed_timeline.strip().split('\n'):
                    line = line.strip()
                    if line.startswith('-'):
                        # Format time entries with better styling
                        line = line.replace('-', '•', 1).strip()
                        formatted_timeline += f"<p style='margin-bottom:8px; padding-left:10px;'>{line}</p>"
                    else:
                        formatted_timeline += f"<p>{line}</p>"
                
                timeline_content += f"<h3 style='color: #4ecdc4; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-top: 20px; margin-bottom: 15px; font-size: 20px; font-weight: bold;'>Timeline for {title}</h3>"
                timeline_content += f"<div class='timeline-content'>{formatted_timeline}</div>"
                
                # If we have place details, add hidden place information blocks - but only for places mentioned in this timeline
                if current_timeline_places and place_info_by_name:
                    for place_name in current_timeline_places:
                        place_key = place_name.lower()
                        if place_key in place_info_by_name:
                            place = place_info_by_name[place_key]
                            place_id = f"place_{i}_{place_names.index(place_name)}"
                            
                            # Create hidden div with place details - without any markdown syntax
                            place_info = f"""
                            <div id="{place_id}" class="place-details">
                                <h4 style="color:#ff6b6b; margin-top:0; margin-bottom:10px; font-size:18px; font-weight:bold;">{place.get('name', 'Unknown Place')}</h4>
                                <p><strong>Address:</strong> {place.get('formatted_address', place.get('vicinity', 'Address not available'))}</p>
                                <p><strong>Rating:</strong> {place.get('rating', 'Not rated')}/5 ({place.get('user_ratings_total', 0)} reviews)</p>
                                {f'<p><strong>Status:</strong> {get_busy_status(place)}</p>' if 'opening_hours' in place else ''}
                                <p><a href="{place.get('url', '#')}" target="_blank" style="display:inline-block; padding:6px 12px; background-color:#4285F4; color:white; border-radius:4px; text-decoration:none; font-weight:600; margin-top:8px;">View on Google Maps</a></p>
                            </div>
                            """
                            # Strip markdown-like syntax that might be causing display issues
                            place_info = place_info.replace('###', '').replace('```', '')
                            timeline_content += place_info
                
                # Add a placeholder for the script instead of directly embedding JavaScript
                if i == len(timeline_matches) - 1 and place_names:
                    timeline_content += """
                    <div id="place-detail-container" data-has-places="true"></div>
                    """
            
            # Close the timelines wrapper div
            timeline_content += "</div>"
            
            # Remove timeline sections from main content to avoid duplication
            main_content = re.sub(timeline_pattern, '', content)
        else:
            # If no timeline is found, just use the entire content as main_content
            main_content = content
        
        return main_content, timeline_content, map_html, place_details_list
        
    except Exception as e:
        print(f"Error generating date ideas: {str(e)}")
        error_message = f"""
        <div style="padding: 20px; text-align: center; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
            <h3 style="color: #6c757d;">Error Generating Date Ideas</h3>
            <p>An error occurred while generating date ideas: {str(e)}</p>
            <p>Please try again later or with different parameters.</p>
        </div>
        """
        return error_message, "", "", []