import os
import gradio as gr
from dotenv import load_dotenv
from utilities.openai_tools import generate_date_ideas, is_openai_available, generate_event_ideas
from utilities.map_tools import is_maps_available

# Load environment variables
load_dotenv()

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "custom.css")
with open(css_path, "r") as f:
    custom_css = f.read()

# Add additional CSS for location input
custom_css += """
.location-input label {
    color: var(--primary-color) !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
}

.location-input textarea, .location-input input {
    border: 2px solid var(--primary-color) !important;
    background-color: #fff9f9 !important;
}
"""

# Add custom CSS for better rendering
css = """
.timeline-output h2 {
    color: #4f46e5;
    border-bottom: 2px solid #818cf8;
    padding-bottom: 10px;
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 24px;
    font-weight: bold;
    display: block;
    width: 100%;
}

.timeline-item {
    margin-bottom: 30px;
}

.timeline-content {
    background-color: #f9fafb;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}

.timeline-entry {
    margin-bottom: 12px;
    padding-left: 15px;
    border-left: 3px solid #4f46e5;
}

.map-output {
    width: 100%;
    height: 400px;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;
}

.place-info {
    padding: 20px;
    background-color: #f9fafb;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
}
"""

# Define Gradio interface
with gr.Blocks(
    title="Perfect Event Generator", 
    theme=gr.themes.Default(
        primary_hue="indigo",
        secondary_hue="blue",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    ), 
    css=custom_css
) as app:
    # Add the logo at the top
    # logo_path = "static/images/logo.png"
    # with gr.Row(elem_classes="logo-container-row"):
    #     gr.Image(value=logo_path, show_label=False, container=False, height=100, width=100, elem_classes="centered-logo")
    
    gr.Markdown("# Perfect Event Generator")
    gr.Markdown("Enter your preferences and get personalized event ideas!")
    
    # Add API key status notice
    api_status_html = ""
    if not is_openai_available():
        api_status_html += """
        <div style="padding: 15px; margin-bottom: 20px; background-color: #fff3f3; border-radius: 8px; border: 1px solid #ffcccb;">
            <h3 style="color: #d9534f; margin-top: 0;"><i class="fas fa-exclamation-triangle"></i> OpenAI API Key Missing</h3>
            <p>The OpenAI API key is not configured. Event generation will not work.</p>
            <p>Please add your OpenAI API key to the .env file to enable event generation.</p>
        </div>
        """
    if not is_maps_available():
        api_status_html += """
        <div style="padding: 15px; margin-bottom: 20px; background-color: #fff3f3; border-radius: 8px; border: 1px solid #ffcccb;">
            <h3 style="color: #d9534f; margin-top: 0;"><i class="fas fa-exclamation-triangle"></i> Google Maps API Key Missing</h3>
            <p>The Google Maps API key is not configured. Location-based recommendations will not work.</p>
            <p>Please add your Google Maps API key to the .env file to enable location features.</p>
        </div>
        """
    
    if api_status_html:
        gr.HTML(api_status_html)
    
    # Main input section with 3 columns
    with gr.Row():
        # First column - Basic preferences
        with gr.Column(scale=1):
            gr.Markdown("### Basic Preferences")
            
            # Add event type selection
            event_type = gr.Dropdown(
                label="Event Type",
                choices=[
                    "First Date", 
                    "Casual Dating", 
                    "Married Date", 
                    "Night with the Girls", 
                    "Night with the Boys",
                    "Family Outing",
                    "Afterwork Meetup",
                    "Hookup"
                ],
                value="Casual Dating",
                elem_classes="mobile-friendly-dropdown"
            )
            
            time_available = gr.Slider(
                label="Time Available (hours)",
                minimum=1,
                maximum=12,
                value=4,
                step=0.5,
                info="Slide to select how many hours you have available",
                elem_classes="mobile-friendly-slider"
            )
            
            # Add date and time preference options
            with gr.Accordion("Specific Date/Time Preferences (Optional)", open=False):
                time_preference = gr.Dropdown(
                    label="When would you like to go?",
                    choices=[
                        "Anytime",
                        "Today",
                        "Tomorrow", 
                        "This weekend",
                        "Next weekend",
                        "Anytime in the next 7 days",
                        "Anytime in the next 30 days",
                        "Specific dates"
                    ],
                    value="Anytime",
                    elem_classes="mobile-friendly-dropdown"
                )
                
                with gr.Group(visible=False) as specific_dates_group:
                    specific_date1 = gr.Textbox(
                        label="Date Option 1",
                        placeholder="e.g., Friday, April 19",
                        elem_classes="mobile-friendly-input"
                    )
                    specific_time1 = gr.Textbox(
                        label="Time Option 1",
                        placeholder="e.g., Evening, 7 PM, Afternoon",
                        elem_classes="mobile-friendly-input"
                    )
                    
                    specific_date2 = gr.Textbox(
                        label="Date Option 2 (Optional)",
                        placeholder="e.g., Saturday, April 20",
                        elem_classes="mobile-friendly-input"
                    )
                    specific_time2 = gr.Textbox(
                        label="Time Option 2 (Optional)",
                        placeholder="e.g., Morning, All day, 1-5 PM",
                        elem_classes="mobile-friendly-input"
                    )
                    
                    specific_date3 = gr.Textbox(
                        label="Date Option 3 (Optional)",
                        placeholder="e.g., Sunday, April 21",
                        elem_classes="mobile-friendly-input"
                    )
                    specific_time3 = gr.Textbox(
                        label="Time Option 3 (Optional)",
                        placeholder="e.g., Lunch time, 2-4 PM",
                        elem_classes="mobile-friendly-input"
                    )
                
                # Add JavaScript handler to show/hide specific dates based on dropdown
                time_preference.change(
                    fn=lambda x: {"visible": x == "Specific dates"},
                    inputs=[time_preference],
                    outputs=[specific_dates_group]
                )
            
            budget = gr.Slider(
                label="Budget ($)",
                minimum=0,
                maximum=500,
                value=100,
                step=10,
                info="Slide to select your budget in dollars",
                elem_classes="mobile-friendly-slider"
            )
            
            physical_activity = gr.Slider(
                label="Physical Activity Level (1-10)",
                minimum=1,
                maximum=10,
                value=5,
                step=1,
                info="1 = Very low, 10 = Very high",
                elem_classes="mobile-friendly-slider"
            )
            
            vibe = gr.Dropdown(
                label="Desired Vibe (select multiple)",
                choices=["Romantic", "Adventurous", "Relaxed", "Fun", "Cultural", "Intellectual", "Sophisticated", "Energetic"],
                multiselect=True,
                value=["Fun", "Relaxed"],
                elem_classes="mobile-friendly-dropdown"
            )
            
            location_type = gr.Dropdown(
                label="Location Type (select multiple)",
                choices=["Indoors", "Outdoors", "Urban", "Nature", "Beach", "Mountains", "Countryside"],
                multiselect=True,
                value=["Indoors", "Outdoors"],
                elem_classes="mobile-friendly-dropdown"
            )
            
            location = gr.Textbox(
                label="Your Location (optional, for place recommendations)",
                placeholder="e.g., San Francisco, CA",
                info="Enter your city, state, country for location-specific suggestions and maps",
                elem_classes="mobile-friendly-input location-input"
            )
        
        # Second column - Partner preferences (dynamic label based on event type)
        with gr.Column(scale=1, elem_id="partner-preferences-column"):
            partner_prefs_markdown = gr.Markdown("### Participant Preferences", elem_id="prefs_header")
            
            partner_likes = gr.Textbox(
                label="What do they like?",
                placeholder="e.g., Italian food, live music, art galleries",
                lines=2,
                elem_classes="mobile-friendly-input",
                elem_id="likes_field"
            )
            
            partner_dislikes = gr.Textbox(
                label="What do they dislike?",
                placeholder="e.g., crowds, spicy food, horror movies",
                lines=2,
                elem_classes="mobile-friendly-input",
                elem_id="dislikes_field"
            )
            
            partner_hobbies = gr.Textbox(
                label="Interests/Hobbies",
                placeholder="e.g., hiking, photography, board games",
                lines=2,
                elem_classes="mobile-friendly-input",
                elem_id="hobbies_field"
            )
            
            partner_personality = gr.Textbox(
                label="Personality traits",
                placeholder="e.g., introverted, adventurous, analytical",
                lines=2,
                elem_classes="mobile-friendly-input",
                elem_id="personality_field"
            )
        
        # Third column - Your preferences and misc
        with gr.Column(scale=1):
            gr.Markdown("### Your Preferences & Additional Info")
            self_preferences = gr.Textbox(
                label="Your Preferences (optional)",
                placeholder="e.g., I prefer casual settings, would like to avoid loud places",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
            
            misc_input = gr.Textbox(
                label="Any Other Details (optional)",
                placeholder="e.g., special occasion, accessibility requirements, etc.",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
            
            # Add some spacing
            gr.Markdown("<br>")
            gr.Markdown("<br>")
            
            # Generate button at the bottom of the third column
            generate_button = gr.Button("Generate Event Ideas", variant="primary", elem_classes="generate-btn", size="lg")
    
    # Create the layout for outputs
    with gr.Row() as output_container:
        # Main content on the left (2/3 width)
        with gr.Column(scale=2):
            output = gr.Markdown(elem_classes=["output-text"], visible=True)
        
        # Timeline on the right (1/3 width)
        with gr.Column(scale=1):
            timeline_output = gr.HTML(elem_classes=["timeline-output"])
    
    # Map in full width
    with gr.Row() as map_container:
        map_output = gr.HTML(elem_classes=["map-output"])
    
    # Place details in full width
    with gr.Row() as place_container:
        place_info = gr.HTML(elem_classes=["place-info"], show_label=False)
    
    # Add the CSS to the page
    gr.HTML(f"<style>{css}</style>")
    
    # Add the JavaScript
    gr.HTML(f"""<script>
    function updateUIForEventType(eventType) {{
        // Get elements
        const partnerColumn = document.getElementById('partner-preferences-column');
        const partnerHeader = document.getElementById('prefs_header');
        const partnerLikes = document.getElementById('likes_field');
        const partnerDislikes = document.getElementById('dislikes_field');
        const partnerHobbies = document.getElementById('hobbies_field');
        const partnerPersonality = document.getElementById('personality_field');
        
        // Update headers and placeholders based on event type
        if (eventType === "Family Outing") {{
            partnerHeader.textContent = "Family Preferences";
            partnerLikes.querySelector('label').textContent = "What does your family like?";
            partnerDislikes.querySelector('label').textContent = "What does your family dislike?";
            partnerHobbies.querySelector('label').textContent = "Family interests/activities";
            partnerPersonality.querySelector('label').textContent = "Family dynamic";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Parks, family-friendly restaurants...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Long wait times, very noisy places...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Board games, movie nights, hiking...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Kids ages, energy levels, interests...";
        }} 
        else if (eventType === "Night with the Girls" || eventType === "Night with the Boys") {{
            partnerHeader.textContent = "Group Preferences";
            partnerLikes.querySelector('label').textContent = "What do your friends like?";
            partnerDislikes.querySelector('label').textContent = "What do your friends dislike?";
            partnerHobbies.querySelector('label').textContent = "Group interests/activities";
            partnerPersonality.querySelector('label').textContent = "Group dynamic";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Wine, spa days, shopping...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Noisy venues, long walks...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Yoga, book clubs, cooking...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Creative, social, energetic...";
        }}
        else if (eventType === "Afterwork Meetup") {{
            partnerHeader.textContent = "Colleague Preferences";
            partnerLikes.querySelector('label').textContent = "What do your colleagues like?";
            partnerDislikes.querySelector('label').textContent = "What do your colleagues dislike?";
            partnerHobbies.querySelector('label').textContent = "Group interests/activities";
            partnerPersonality.querySelector('label').textContent = "Work relationships";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Happy hours, casual dining...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Work talk, formal settings...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Networking, team sports...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Mix of personalities, department culture...";
        }}
        else if (eventType === "Married Date") {{
            partnerHeader.textContent = "Spouse Preferences";
            partnerLikes.querySelector('label').textContent = "What does your spouse like?";
            partnerDislikes.querySelector('label').textContent = "What does your spouse dislike?";
            partnerHobbies.querySelector('label').textContent = "Spouse's interests/hobbies";
            partnerPersonality.querySelector('label').textContent = "Spouse's personality traits";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Fine dining, quiet evenings...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Over-planned activities, crowds...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Gardening, reading, crafts...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Thoughtful, intellectual, homebody...";
        }}
        else if (eventType === "Hookup") {{
            partnerHeader.textContent = "Partner Preferences";
            partnerLikes.querySelector('label').textContent = "What do they like?";
            partnerDislikes.querySelector('label').textContent = "What do they dislike?";
            partnerHobbies.querySelector('label').textContent = "Interests/Turn-ons";
            partnerPersonality.querySelector('label').textContent = "Personality/Vibe";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Dancing, specific drinks, music...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Small talk, crowded venues...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Spontaneity, confidence, physical touch...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Flirty, laid-back, adventurous...";
        }}
        else {{
            // Default for casual dating, first date
            partnerHeader.textContent = "Partner Preferences";
            partnerLikes.querySelector('label').textContent = "What does your partner like?";
            partnerDislikes.querySelector('label').textContent = "What does your partner dislike?";
            partnerHobbies.querySelector('label').textContent = "Partner's interests/hobbies";
            partnerPersonality.querySelector('label').textContent = "Partner's personality traits";
            
            partnerLikes.querySelector('textarea').placeholder = "E.g., Art, music, specific cuisines, sports...";
            partnerDislikes.querySelector('textarea').placeholder = "E.g., Crowds, certain foods, activities they avoid...";
            partnerHobbies.querySelector('textarea').placeholder = "E.g., Photography, hiking, cooking, gaming...";
            partnerPersonality.querySelector('textarea').placeholder = "E.g., Introverted, adventurous, detail-oriented...";
        }}
    }}
    
    // Set up the event listener once the DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {{
        setTimeout(function() {{
            const dropdown = document.querySelector('select[data-testid="dropdown"]');
            if (dropdown) {{
                dropdown.addEventListener('change', function() {{
                    updateUIForEventType(this.value);
                }});
                // Initial update
                updateUIForEventType("Casual Dating");
            }}
        }}, 1000);
    }});
    </script>""")
    
    # Set up event handler for event type changes without the problematic _js parameter
    event_type.change(
        fn=lambda x: None,  # Dummy function that doesn't do anything in Python
        inputs=[event_type],
        outputs=[]
    )
    
    # Set up the click event
    def handle_generate(
        event_type, time_available, time_preference, specific_date1, specific_time1, 
        specific_date2, specific_time2, specific_date3, specific_time3,
        budget, vibe, location_type, physical_activity, 
        partner_likes, partner_dislikes, partner_hobbies, partner_personality,
        self_preferences, misc_input, location
    ):
        # Process date/time preferences
        date_time_info = ""
        if time_preference != "Anytime":
            date_time_info = f"Time Preference: {time_preference}\n"
            
            if time_preference == "Specific dates":
                date_time_info += "Preferred Dates:\n"
                
                if specific_date1 and specific_time1:
                    date_time_info += f"- {specific_date1} at {specific_time1}\n"
                
                if specific_date2 and specific_time2:
                    date_time_info += f"- {specific_date2} at {specific_time2}\n"
                    
                if specific_date3 and specific_time3:
                    date_time_info += f"- {specific_date3} at {specific_time3}\n"
        
        # If user provided date/time preferences, add to misc_input
        if date_time_info:
            if misc_input:
                misc_input += "\n\n" + date_time_info
            else:
                misc_input = date_time_info
        
        main_content, timeline_content, map_html, place_details = generate_event_ideas(
            time_available, budget, vibe, location_type, physical_activity, 
            partner_likes, partner_dislikes, partner_hobbies, partner_personality,
            self_preferences, misc_input, location, event_type
        )
        
        # Format place details for display
        place_info_html = ""
        if place_details:
            place_info_html = """
            <h3 style="color:#ff6b6b; font-size:22px; font-weight:bold; border-bottom:1px solid #eee; padding-bottom:10px; margin-top:0; margin-bottom:20px;">Recommended Places</h3>
            """
            
            for place in place_details:
                name = place.get('name', 'Unknown Place')
                address = place.get('formatted_address', place.get('vicinity', 'No address available'))
                rating = place.get('rating', 'No rating')
                maps_url = place.get('url', place.get('maps_url', '#'))
                
                # Get busy status if available
                busy_status = ""
                if 'opening_hours' in place:
                    if place['opening_hours'].get('open_now', False):
                        busy_status = "Currently open"
                    else:
                        busy_status = "Currently closed"
                
                place_info_html += f"""
                <div style="margin-bottom:25px; padding:20px; border:1px solid #eee; border-radius:8px; background-color:#f9f9f9; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <h4 style="color:#ff6b6b; margin-top:0; margin-bottom:15px; font-size:18px; font-weight:bold;">{name}</h4>
                    <p><strong>Address:</strong> {address}</p>
                    <p><strong>Rating:</strong> {rating}/5</p>
                    {f"<p><strong>Status:</strong> {busy_status}</p>" if busy_status else ""}
                    <p><a href="{maps_url}" target="_blank" style="display:inline-block; padding:6px 12px; background-color:#4285F4; color:white; border-radius:4px; text-decoration:none; font-weight:600; margin-top:8px;">View on Google Maps</a></p>
                """
                
                # Add website if available
                if place.get('website'):
                    place_info_html += f"""
                    <p><strong>Website:</strong> <a href="{place['website']}" target="_blank" style="color:#4285F4; text-decoration:none; font-weight:600;">{place['website']}</a></p>
                    """
                
                # Add phone if available
                if place.get('formatted_phone_number'):
                    place_info_html += f"""
                    <p><strong>Phone:</strong> {place['formatted_phone_number']}</p>
                    """
                
                # Add opening hours if available
                if 'opening_hours' in place and 'weekday_text' in place['opening_hours']:
                    place_info_html += "<p><strong>Opening Hours:</strong></p><ul style='margin-left:20px; margin-bottom:15px;'>"
                    for day in place['opening_hours']['weekday_text']:
                        place_info_html += f"<li style='margin-bottom:5px;'>{day}</li>"
                    place_info_html += "</ul>"
                
                # Add reviews if available
                if 'reviews' in place and place['reviews']:
                    place_info_html += "<p><strong>Top Review:</strong></p>"
                    review = place['reviews'][0]
                    author = review.get('author_name', 'Anonymous')
                    review_rating = review.get('rating', 'No rating')
                    text = review.get('text', 'No comment')
                    time = review.get('relative_time_description', '')
                    
                    place_info_html += f"""
                    <div style="margin-bottom:10px; padding:12px; border-left:3px solid #ddd; background-color:#f5f5f5; border-radius:0 4px 4px 0;">
                        <p><strong>{author}</strong> - {review_rating}/5 ({time})</p>
                        <p style="margin-bottom:0;">{text}</p>
                    </div>
                    """
                
                place_info_html += "</div>"
        
        # Set map section visibility based on if we have map content
        map_section_visible = bool(location and map_html)
        
        return main_content, timeline_content, map_html, place_info_html
    
    generate_button.click(
        fn=handle_generate,
        inputs=[
            event_type,
            time_available, 
            time_preference,
            specific_date1,
            specific_time1,
            specific_date2,
            specific_time2,
            specific_date3,
            specific_time3,
            budget, 
            vibe, 
            location_type, 
            physical_activity, 
            partner_likes,
            partner_dislikes,
            partner_hobbies,
            partner_personality,
            self_preferences,
            misc_input,
            location
        ],
        outputs=[output, timeline_output, map_output, place_info]
    )
    
    gr.Markdown("### How to use")
    gr.Markdown("""
    1. Select the type of event (casual dating, married, first date, etc.)
    2. Adjust the slider for your available time (in hours)
    3. **[OPTIONAL] Specify date and time preferences:**
       - Choose a general time frame like "This weekend" or "Next weekend"
       - OR select "Specific dates" to enter up to 3 exact date and time options
    4. Set your budget using the slider (up to $500)
    5. Pick the vibe(s) you're looking for
    6. Select preferred location type(s)
    7. Set your preferred level of physical activity (1-10)
    8. **Enter your location for area-specific suggestions and interactive maps**
    9. Fill in the optional partner preference fields
    10. Add your own preferences (optional)
    11. Include any miscellaneous information if needed
    12. Click 'Generate Event Ideas' to get personalized recommendations with timeline and cost breakdown
    """)
    
    # Add footer
    gr.HTML('<div class="footer">Perfect Event Generator - Created with ❤️</div>')
    
    # Add JavaScript to handle conditional visibility of participants field
    gr.HTML("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Set up the relationship type change handler
        setupRelationshipTypeHandler();
        observeRelationshipTypeChanges();
    });
    
    function setupRelationshipTypeHandler() {
        const relationshipDropdown = document.querySelector('select[data-testid="dropdown"]');
        if (relationshipDropdown) {
            relationshipDropdown.addEventListener('change', function() {
                toggleParticipantsVisibility(this.value);
            });
            
            // Initial check
            toggleParticipantsVisibility(relationshipDropdown.value);
        }
    }
    
    function toggleParticipantsVisibility(value) {
        const participantsContainer = document.querySelector('input[aria-label="Number of Participants"]').closest('.gradio-container');
        
        if (value === "Night with the Girls" || value === "Night with the Boys" || value === "Afterwork") {
            participantsContainer.style.display = 'block';
        } else {
            participantsContainer.style.display = 'none';
        }
    }
    
    function observeRelationshipTypeChanges() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    for (let i = 0; i < mutation.addedNodes.length; i++) {
                        const node = mutation.addedNodes[i];
                        if (node.querySelector && node.querySelector('select[data-testid="dropdown"]')) {
                            setupRelationshipTypeHandler();
                            break;
                        }
                    }
                }
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }
    </script>
    """)
    
    # Add JavaScript to handle clickable places
    gr.HTML("""
    <script>
    // Wait for DOM to be fully loaded and then set up observers
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM fully loaded');
        setupPlaceClickHandlers();
        observeDOMChanges();
    });
    
    // Function to set up click handlers for clickable places
    function setupPlaceClickHandlers() {
        console.log('Setting up click handlers');
        const placeElements = document.querySelectorAll('.clickable-place');
        console.log('Found ' + placeElements.length + ' clickable places');
        
        placeElements.forEach(element => {
            // Remove any existing click handlers first
            element.removeEventListener('click', togglePlaceDetails);
            // Add new click handler
            element.addEventListener('click', togglePlaceDetails);
        });
    }
    
    // Toggle place details visibility
    function togglePlaceDetails(e) {
        e.preventDefault();
        const placeId = this.getAttribute('data-place-id');
        const placeDetails = document.getElementById(placeId);
        
        if (!placeDetails) {
            console.error('Place details not found for ID: ' + placeId);
            return;
        }
        
        // Toggle visibility
        if (placeDetails.style.display === 'none' || !placeDetails.style.display) {
            placeDetails.style.display = 'block';
        } else {
            placeDetails.style.display = 'none';
        }
    }
    
    // Observe DOM changes to set up handlers for dynamically added elements
    function observeDOMChanges() {
        console.log('Setting up MutationObserver');
        const observer = new MutationObserver(function(mutations) {
            let shouldSetupHandlers = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    for (let i = 0; i < mutation.addedNodes.length; i++) {
                        const node = mutation.addedNodes[i];
                        if (node.classList && 
                            (node.classList.contains('timeline-container') || 
                             node.querySelector && node.querySelector('.clickable-place'))) {
                            shouldSetupHandlers = true;
                            break;
                        }
                    }
                }
            });
            
            if (shouldSetupHandlers) {
                console.log('Found new content with clickable places');
                setupPlaceClickHandlers();
            }
        });
        
        // Start observing the document with the configured parameters
        observer.observe(document.body, { childList: true, subtree: true });
    }
    </script>
    """)

# Launch the app with server settings for Docker
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860) 