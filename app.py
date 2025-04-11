import os
import gradio as gr
from dotenv import load_dotenv
from utilities.openai_tools import generate_date_ideas

# Load environment variables
load_dotenv()

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "custom.css")
with open(css_path, "r") as f:
    custom_css = f.read()

# Define Gradio interface
with gr.Blocks(title="Perfect Date Generator", theme=gr.themes.Soft(), css=custom_css) as app:
    gr.Markdown("# 💕 Perfect Date Generator")
    gr.Markdown("Enter your preferences and get personalized date ideas!")
    
    with gr.Row():
        with gr.Column():
            # Input components
            time_available = gr.Radio(
                label="Time Available",
                choices=["2 hours", "4 hours", "All day"],
                value="4 hours"
            )
            
            budget = gr.Radio(
                label="Budget",
                choices=["$20", "$50", "$100+"],
                value="$50"
            )
            
            vibe = gr.Dropdown(
                label="Vibe",
                choices=["Chill", "Adventurous", "Romantic", "Nerdy", "Outdoorsy"],
                multiselect=True,
                value=["Romantic"]
            )
            
            location_type = gr.Dropdown(
                label="Location Type",
                choices=["Restaurant", "Activity", "Nature", "At-home"],
                multiselect=True,
                value=["Restaurant", "Activity"]
            )

            physical_activity = gr.Radio(
                label="Level of Physical Activity",
                choices=["Low", "Moderate", "High"],
                value="Moderate"
            )
            
            partner_questions = gr.Textbox(
                label="What does your partner enjoy? (Interests, activities they've mentioned, etc.)",
                placeholder="E.g., They love art, trying new foods, and being outdoors",
                lines=3
            )
            
            generate_button = gr.Button("Generate Date Ideas", variant="primary", elem_classes="generate-btn")
        
        with gr.Column():
            # Output component with custom class
            output = gr.Markdown(label="Your Perfect Date Ideas", elem_classes="output-container")
    
    # Set up the click event
    generate_button.click(
        fn=generate_date_ideas,
        inputs=[time_available, budget, vibe, location_type, physical_activity, partner_questions],
        outputs=output
    )
    
    gr.Markdown("### How to use")
    gr.Markdown("""
    1. Select your available time
    2. Choose your budget
    3. Pick the vibe(s) you're looking for
    4. Select preferred location type(s)
    5. Choose the level of physical activity
    6. Add information about your partner's preferences
    7. Click 'Generate Date Ideas' to get personalized recommendations
    """)
    
    # Add footer
    gr.HTML('<div class="footer">Perfect Date Generator - Created with ❤️</div>')

# Launch the app with server settings for Docker
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860) 