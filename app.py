import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_date_ideas(time_available, budget, vibe, location_type, partner_questions):
    """Generate date ideas based on user inputs."""
    
    # Construct the prompt for OpenAI
    prompt = f"""
    Generate 3 perfect date ideas based on the following preferences:
    
    Time Available: {time_available}
    Budget: {budget}
    Vibe: {vibe}
    Location Type: {location_type}
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
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful date planning assistant that creates personalized date ideas."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract and return the response
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating date ideas: {str(e)}"

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
        inputs=[time_available, budget, vibe, location_type, partner_questions],
        outputs=output
    )
    
    gr.Markdown("### How to use")
    gr.Markdown("""
    1. Select your available time
    2. Choose your budget
    3. Pick the vibe(s) you're looking for
    4. Select preferred location type(s)
    5. Add information about your partner's preferences
    6. Click 'Generate Date Ideas' to get personalized recommendations
    """)
    
    # Add footer
    gr.HTML('<div class="footer">Perfect Date Generator - Created with ❤️</div>')

# Launch the app
if __name__ == "__main__":
    app.launch() 