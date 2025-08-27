# Perfect Event Generator
This app is made for those situations where you can't decide what to do or don't know where to start planning for a date or event.

An open source web application that generates personalized event ideas based on time available, budget, and preferences for various occasions including dates, outings, meetups, and more.

## Features

- Select event type (First Date, Casual Dating, Married Date, Hookup, Night with the Girls/Boys, Family Outing, Afterwork Meetup)
- Choose time available (1-12 hours)
- Set flexible date/time preferences:
  - General timeframes (Today, Tomorrow, This weekend, Next weekend)
  - Specific dates (up to 3 date/time combinations)
- Adjust budget ($0-$500)
- Pick vibes (Romantic, Adventurous, Relaxed, Fun, Cultural, Intellectual, Sophisticated, Energetic)
- Select location types (Indoors, Outdoors, Urban, Nature, Beach, Mountains, Countryside)
- Choose level of physical activity (1-10 scale)
- Tailor participant preferences based on event type (automatically adjusts fields for partners, spouses, friends, colleagues, etc.)
- Generate top 3 event ideas with cost, time, and why they're a good fit
- View detailed timelines for each suggested event
- Interactive maps with place markers for recommended locations
- Clickable place recommendations with detailed information:
  - Business hours, ratings, and reviews
  - Direct links to Google Maps
  - Contact information and websites
  - Current open/closed status

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

4. Add your API keys to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
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
   docker compose up --build -d
   ```

2. Use the provided start script:
   ```
   ./start.sh
   ```
   This will:
   - Create a `.env` file if it doesn't exist
   - Build and start the Docker container
   - Display the URL to access the application

3. Edit the `.env` file to add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   ```

4. Access the application at http://localhost:7860 (or the port you specified in `.env`)

## Docker Commands

- Start the application: `docker compose up -d`
- Stop the application: `docker compose down`
- View logs: `docker compose logs -f`
- Rebuild and restart: `docker compose up --build -d`

## Google Maps API Setup

The date generator uses Google Maps API for location-based recommendations. To enable this feature:

1. **Create a Google Cloud project and API key:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or select an existing one)
   - Navigate to APIs & Services > Credentials
   - Create an API key

2. **Enable the required APIs:**
   - In your Google Cloud Console, go to APIs & Services > Library
   - Search for and enable ALL of these required APIs:
     - Places API (for searching and getting place details)
     - Maps JavaScript API (for displaying maps in the browser)
     - Geocoding API (for converting addresses to coordinates)
     - Directions API (for route planning)
   - For each API, click on it and press the "ENABLE" button
   - Wait for the enablement process to complete for each API

3. **Configure API key restrictions (optional but recommended):**
   - Go to APIs & Services > Credentials
   - Find your API key and click "EDIT"
   - Under "API restrictions":
     - Choose "Restrict key"
     - Select ALL of these APIs from the dropdown:
       - Places API
       - Maps JavaScript API
       - Geocoding API
       - Directions API
   - If you add restrictions but miss any required API, the application will show error messages
   - You can temporarily set to "Don't restrict key" for testing, then add proper restrictions later

4. **Set up billing:**
   - Even for free tier usage, you must have billing enabled
   - Go to Billing in Google Cloud Console
   - Link a billing account to your project
   - Note: Google offers a generous free tier that's sufficient for personal use
   - You can set up budget alerts to prevent unexpected charges

5. **Add the API key to your .env file:**
   ```
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   ```

6. **Test the API connectivity:**
   ```
   python test_gmaps_api.py
   ```
   - This will verify that all necessary APIs are accessible with your key
   - If you see any errors, check the troubleshooting section below

## How to Use the Perfect Event Generator

### 1. Choose Your Event Type

The application supports multiple event types, each with tailored recommendations:
- **First Date**: Low-pressure, public activities ideal for getting to know someone
- **Casual Dating**: Fun, engaging activities for early relationship stages
- **Married Date**: Options to break routine and rekindle romance
- **Hookup**: Suggestions for intimate, flirty settings
- **Night with the Girls/Boys**: Group-friendly activities for friends
- **Family Outing**: All-ages appropriate activities
- **Afterwork Meetup**: Professional and casual options for colleagues

The interface will dynamically adjust based on your selection, changing terminology from "partner" to "spouse," "friends," "family," etc.

### 2. Set Time and Date Preferences

- **Time Available**: Use the slider to specify how many hours you have (1-12 hours)
- **Date/Time Preferences**: Click the dropdown to choose from options like:
  - "Anytime" (default)
  - "Today"
  - "Tomorrow"
  - "This weekend"
  - "Next weekend"
  - "Anytime in the next 7 days"
  - "Specific dates"
- If you select "Specific dates," you can enter up to three specific date/time combinations
  - Example: "Friday, April 19" and "Evening" or "Saturday, April 20" and "2-5 PM"

### 3. Configure Additional Parameters

- **Budget**: Set your spending limit (up to $500)
- **Vibe**: Select multiple options like Romantic, Fun, Cultural, etc.
- **Location Type**: Choose settings such as Indoors, Outdoors, Urban, Nature, etc.
- **Physical Activity Level**: Set from 1 (very low) to 10 (very high)
- **Location**: Enter your city/location for place-specific recommendations

### 4. Customize Participant Preferences

Based on your event type, fill in relevant preferences:
- What they like/dislike
- Interests/hobbies
- Personality traits
- Your own preferences and any additional information

### 5. Generate and Explore Recommendations

After clicking "Generate Event Ideas," you'll receive:

- **Three Event Ideas**: Each with a descriptive title, estimated cost, duration, and explanation
- **Interactive Timelines**: Detailed breakdown of each recommendation with times and activities
- **Map View**: If you provided a location, you'll see a map with markers for recommended places
- **Place Details**: Click on place names to view:
  - Business information (hours, contact info, website)
  - Ratings and reviews
  - Current open/closed status
  - Direct links to view on Google Maps

### 6. Interacting with Place Recommendations

- **Click Place Names**: In the timeline view, place names are clickable links
- **View Details**: See ratings, reviews, operating hours, and contact information
- **Map Integration**: Click "View on Google Maps" to get directions or save locations
- **Website Links**: Direct access to official websites when available

By providing specific dates/times and location information, you'll receive highly tailored recommendations that consider factors like operating hours, seasonal activities, and local options.

## Troubleshooting API Keys

### Google Maps API Key Expired

If you see the error `REQUEST_DENIED (The provided API key is expired.)`, follow these steps:

1. Go to [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials)
2. Find your expired key and create a new one or renew it
3. Update your `.env` file with the new key
4. Restart your application

### API Not Authorized

If you see `REQUEST_DENIED (This API project is not authorized to use this API)`, this means one or more required APIs are not enabled:

1. Go to [Google Cloud Console APIs Dashboard](https://console.cloud.google.com/apis/dashboard)
2. Check which APIs are enabled for your project
3. Go to [API Library](https://console.cloud.google.com/apis/library)
4. Search for and enable any missing APIs from this list:
   - Places API
   - Maps JavaScript API
   - Geocoding API
   - Directions API
5. Wait a few minutes for the changes to propagate
6. Restart your application and try again

### API Restrictions Issues

If you have restricted your API key to specific APIs but forgot to include all required ones:

1. Go to [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials)
2. Find your API key and click "EDIT"
3. Under "API restrictions":
   - Either select "Don't restrict key" temporarily for testing
   - Or make sure ALL required APIs are selected (Places, Maps JavaScript, Geocoding, Directions)
4. Save your changes
5. Allow a few minutes for changes to take effect
6. Restart your application

### Billing Issues

If you see quota-related errors:

1. Go to [Google Cloud Console Billing](https://console.cloud.google.com/billing)
2. Verify your billing account is properly linked to your project
3. Check if you've exceeded any quotas or limits
4. Consider upgrading your billing plan if needed

## Technologies Used

- Python
- Gradio (for the web interface)
- OpenAI API (for generating date ideas)
- Google Maps API (for location recommendations)
- Folium (for interactive maps)
- python-dotenv (for environment variable management)
- Docker (for containerization)