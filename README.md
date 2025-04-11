# Perfect Date Generator

A web application that generates personalized date ideas based on time available, budget, and preferences.

## Features

- Select time available (2 hours, 4 hours, all day)
- Choose budget ($20, $50, $100+)
- Pick vibes (chill, adventurous, romantic, nerdy, outdoorsy)
- Select location types (restaurant, activity, nature, at-home)
- Choose level of physical activity (low, moderate, high)
- Provide partner preferences
- Generate top 3 date ideas with cost, time, and why they're a good fit

## Standard Installation

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

5. Run the application:
   ```
   python app.py
   ```

6. Open the URL displayed in the terminal (usually http://127.0.0.1:7860).

## Docker Installation

1. Clone this repository:
   ```
   git clone [repository-url]
   cd perfect-date-generator
   ```

2. Use the provided start script:
   ```
   ./start.sh
   ```
   This will:
   - Create a `.env` file if it doesn't exist
   - Build and start the Docker container
   - Display the URL to access the application

3. Edit the `.env` file to add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. Access the application at http://localhost:7860 (or the port you specified in `.env`)

## Docker Commands

- Start the application: `docker-compose up -d`
- Stop the application: `docker-compose down`
- View logs: `docker-compose logs -f`
- Rebuild and restart: `docker-compose up --build -d`

## Technologies Used

- Python
- Gradio (for the web interface)
- OpenAI API (for generating date ideas)
- python-dotenv (for environment variable management)
- Docker (for containerization)