# Perfect Date Generator

A web application that generates personalized date ideas based on time available, budget, and preferences.

## Features

- Select time available (2 hours, 4 hours, all day)
- Choose budget ($20, $50, $100+)
- Pick vibes (chill, adventurous, romantic, nerdy, outdoorsy)
- Select location types (restaurant, activity, nature, at-home)
- Provide partner preferences
- Generate top 3 date ideas with cost, time, and why they're a good fit

## Installation

1. Clone this repository:
   ```
   git clone [repository-url]
   cd perfect-date-generator
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the example:
   ```
   cp .env.example .env
   ```

4. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Open the URL displayed in the terminal (usually http://127.0.0.1:7860).

3. Enter your preferences and click "Generate Date Ideas".

4. Enjoy your perfect date ideas!

## Technologies Used

- Python
- Gradio (for the web interface)
- OpenAI API (for generating date ideas)
- python-dotenv (for environment variable management)