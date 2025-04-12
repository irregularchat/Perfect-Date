import os
import gradio as gr
from dotenv import load_dotenv
from utilities.openai_tools import generate_date_ideas, is_openai_available
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

# Define Gradio interface
with gr.Blocks(
    title="Perfect Date Generator", 
    theme=gr.themes.Soft(
        primary_hue="pink",
        secondary_hue="teal",
        neutral_hue="gray",
        text_size="lg"
    ), 
    css=custom_css
) as app:
    # Add the logo at the top
    logo_path = "static/images/logo.png"
    with gr.Row(elem_classes="logo-container-row"):
        gr.Image(value=logo_path, show_label=False, container=False, height=100, width=100, elem_classes="centered-logo")
    
    gr.Markdown("# 💕 Perfect Date Generator")
    gr.Markdown("Enter your preferences and get personalized date ideas!")
    
    # Add API key status notice
    api_status_html = ""
    if not is_openai_available():
        api_status_html += """
        <div style="padding: 15px; margin-bottom: 20px; background-color: #fff3f3; border-radius: 8px; border: 1px solid #ffcccb;">
            <h3 style="color: #d9534f; margin-top: 0;"><i class="fas fa-exclamation-triangle"></i> OpenAI API Key Missing</h3>
            <p>The OpenAI API key is not configured. Date generation will not work.</p>
            <p>Please add your OpenAI API key to the .env file to enable date generation.</p>
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
            relationship_type = gr.Dropdown(
                label="Type of Date",
                choices=["Casual Dating", "Married", "First Date", "Hook Up", "Night with the Girls", "Night with the Boys", "Afterwork"],
                value="Casual Dating",
                elem_classes="mobile-friendly-dropdown"
            )
            
            # Conditionally show number of participants for group activities
            participants = gr.Number(
                label="Number of Participants",
                value=2,
                minimum=1,
                maximum=20,
                step=1,
                visible=False,
                elem_classes="mobile-friendly-input"
            )
            
            time_available = gr.Slider(
                label="Time Available (hours)",
                minimum=1,
                maximum=12,
                value=4,
                step=1,
                info="Slide to select how many hours you have available",
                elem_classes="mobile-friendly-slider"
            )
            
            budget = gr.Slider(
                label="Budget ($)",
                minimum=20,
                maximum=500,
                value=50,
                step=10,
                info="Slide to select your budget in dollars",
                elem_classes="mobile-friendly-slider"
            )
            
            physical_activity = gr.Slider(
                label="Level of Physical Activity",
                minimum=1,
                maximum=10,
                value=5,
                step=1,
                info="1 = Very low, 10 = Very high",
                elem_classes="mobile-friendly-slider"
            )
            
            vibe = gr.Dropdown(
                label="Vibe",
                choices=["Chill", "Adventurous", "Romantic", "Nerdy", "Outdoorsy"],
                multiselect=True,
                value=["Romantic"],
                elem_classes="mobile-friendly-dropdown"
            )
            
            location_type = gr.Dropdown(
                label="Location Type",
                choices=["Restaurant", "Activity", "Nature", "At-home"],
                multiselect=True,
                value=["Restaurant", "Activity"],
                elem_classes="mobile-friendly-dropdown"
            )
            
            location = gr.Textbox(
                label="Your Location",
                placeholder="E.g., Seattle, WA, USA",
                info="Enter your city, state, country for location-specific suggestions and maps",
                elem_classes="mobile-friendly-input location-input"
            )
        
        # Second column - Partner preferences
        with gr.Column(scale=1):
            gr.Markdown("### Partner Preferences (Optional)")
            partner_likes = gr.Textbox(
                label="What does your partner like?",
                placeholder="E.g., Art, music, specific cuisines, sports...",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
            
            partner_dislikes = gr.Textbox(
                label="What does your partner dislike?",
                placeholder="E.g., Crowds, certain foods, activities they avoid...",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
            
            partner_hobbies = gr.Textbox(
                label="What are your partner's hobbies?",
                placeholder="E.g., Photography, hiking, cooking, gaming...",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
            
            partner_personality = gr.Textbox(
                label="Describe your partner's personality",
                placeholder="E.g., Introverted, adventurous, detail-oriented...",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
        
        # Third column - Your preferences and misc
        with gr.Column(scale=1):
            gr.Markdown("### Your Preferences (Optional)")
            self_preferences = gr.Textbox(
                label="What do you enjoy?",
                placeholder="E.g., Your interests, activities you'd like to try...",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
            
            misc_input = gr.Textbox(
                label="Anything else to consider?",
                placeholder="E.g., Special occasions, specific requirements, constraints...",
                lines=2,
                elem_classes="mobile-friendly-input"
            )
            
            # Add some spacing
            gr.Markdown("<br>")
            gr.Markdown("<br>")
            
            # Generate button at the bottom of the third column
            generate_button = gr.Button("Generate Date Ideas", variant="primary", elem_classes="generate-btn", size="lg")
    
    # Output section
    with gr.Row():
        output = gr.Markdown(label="Your Perfect Date Ideas", elem_classes="output-container")
    
    # Timeline section - making it widescreen
    with gr.Row(elem_classes="timeline-section full-width"):
        timeline_output = gr.HTML(elem_classes="timeline-container")
    
    # Map and place info section - full width with no unnecessary containers
    with gr.Row(elem_classes="map-section full-width") as map_row:
        gr.HTML("<h2 style='color:#ff6b6b; border-bottom:2px solid #ffe66d; padding-bottom:15px; margin-top:30px; margin-bottom:25px; font-size:24px; font-weight:bold; width:100%; text-align:left;'>Map & Place Information</h2>", elem_classes="full-width")
        
        # Map container with absolutely no label
        map_output = gr.HTML(elem_classes="map-container full-width", show_label=False)
        
        # Place info container with absolutely no label
        place_info = gr.HTML(elem_classes="place-info-container full-width", show_label=False)
    
    # Set up the click event
    def handle_generate(
        relationship_type, participants, time_available, budget, vibe, location_type, physical_activity, 
        partner_likes, partner_dislikes, partner_hobbies, partner_personality,
        self_preferences, misc_input, location
    ):
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            time_available, budget, vibe, location_type, physical_activity, 
            partner_likes, partner_dislikes, partner_hobbies, partner_personality,
            self_preferences, misc_input, location, relationship_type, participants
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
            relationship_type,
            participants,
            time_available, 
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
    1. Select the type of date (casual dating, married, first date, etc.)
    2. For group activities, specify the number of participants
    3. Adjust the slider for your available time (in hours)
    4. Set your budget using the slider (up to $500)
    5. Pick the vibe(s) you're looking for
    6. Select preferred location type(s)
    7. Set your preferred level of physical activity (1-10)
    8. **Enter your location for area-specific suggestions and interactive maps**
    9. Fill in the optional partner preference fields
    10. Add your own preferences (optional)
    11. Include any miscellaneous information if needed
    12. Click 'Generate Date Ideas' to get personalized recommendations with timeline and cost breakdown
    """)
    
    # Add footer
    gr.HTML('<div class="footer">Perfect Date Generator - Created with ❤️</div>')
    
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