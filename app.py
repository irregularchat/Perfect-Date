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
                label="Your Location (Optional)",
                placeholder="E.g., Seattle, WA, USA",
                info="Enter your city, state, country for location-specific suggestions",
                elem_classes="mobile-friendly-input"
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
    
    # Timeline section (separate from the main output)
    with gr.Row(elem_classes="timeline-section"):
        gr.Markdown("### Timeline of Events")
        timeline_output = gr.Markdown(elem_classes="timeline-container")
    
    # Map and place info section
    with gr.Row(elem_classes="map-section") as map_row:
        map_section = gr.Markdown("### Map & Place Information")
        with gr.Column(scale=1):
            map_output = gr.HTML(label="Map", elem_classes="map-container")
        with gr.Column(scale=1):
            place_info = gr.HTML(label="Place Information", elem_classes="place-info-container")
    
    # Set up the click event
    def handle_generate(
        time_available, budget, vibe, location_type, physical_activity, 
        partner_likes, partner_dislikes, partner_hobbies, partner_personality,
        self_preferences, misc_input, location
    ):
        main_content, timeline_content, map_html, place_details = generate_date_ideas(
            time_available, budget, vibe, location_type, physical_activity, 
            partner_likes, partner_dislikes, partner_hobbies, partner_personality,
            self_preferences, misc_input, location
        )
        
        # Format place details for display
        place_info_html = ""
        if place_details:
            place_info_html = "<h3>Recommended Places</h3>"
            for place in place_details:
                name = place.get('name', 'Unknown Place')
                address = place.get('formatted_address', place.get('vicinity', 'No address available'))
                rating = place.get('rating', 'No rating')
                
                place_info_html += f"""
                <div style="margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                    <h4>{name}</h4>
                    <p><strong>Address:</strong> {address}</p>
                    <p><strong>Rating:</strong> {rating}/5</p>
                """
                
                # Add opening hours if available
                if 'opening_hours' in place and 'weekday_text' in place['opening_hours']:
                    place_info_html += "<p><strong>Opening Hours:</strong></p><ul>"
                    for day in place['opening_hours']['weekday_text']:
                        place_info_html += f"<li>{day}</li>"
                    place_info_html += "</ul>"
                
                place_info_html += "</div>"
        
        # Set map section visibility based on if we have map content
        map_section_visible = bool(location and map_html)
        
        return main_content, timeline_content, map_html, place_info_html
    
    generate_button.click(
        fn=handle_generate,
        inputs=[
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
    1. Adjust the slider for your available time (in hours)
    2. Set your budget using the slider (up to $500)
    3. Pick the vibe(s) you're looking for
    4. Select preferred location type(s)
    5. Set your preferred level of physical activity (1-10)
    6. Enter your location for area-specific suggestions (optional)
    7. Fill in the optional partner preference fields
    8. Add your own preferences (optional)
    9. Include any miscellaneous information if needed
    10. Click 'Generate Date Ideas' to get personalized recommendations with timeline and cost breakdown
    """)
    
    # Add footer
    gr.HTML('<div class="footer">Perfect Date Generator - Created with ❤️</div>')

# Launch the app with server settings for Docker
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860) 