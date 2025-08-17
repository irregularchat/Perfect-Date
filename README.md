# 🌟 Perfect Date Generator

**AI-powered date planning with intelligent two-location support and global destination recommendations**

Transform your dating life with the most intelligent, location-aware date planning application. Using real-world data and advanced algorithms, Perfect Date Generator creates personalized experiences that work for singles, couples, and long-distance relationships.

## ✨ Features

### 🎯 **Core Date Planning**
- **Real Venue Discovery**: Powered by Google Places API with actual ratings, hours, and contact info
- **Intelligent Activity Timeline**: Context-aware suggestions based on event type and vibes
- **Budget-Aware Recommendations**: Filters venues and activities within your price range
- **Interactive Maps**: Real-time visualization with venue markers and directions
- **Multiple Date Types**: First dates, casual dating, married dates, family outings, and more

### 💕 **Two-Location Dating** *(v0.2)*
- **Smart Midpoint Calculation**: Uses spherical geometry to find optimal meeting points
- **Distance-Based Search**: Automatically adjusts search radius (20-60% of total distance)
- **Travel Fairness Scoring**: Shows how equitable each venue is for both people
- **Real-Time Distance Display**: See travel time and distance for both locations
- **Interactive Visualization**: Maps show both starting points, midpoint, and search area

### ✈️ **Global Destination Dating** *(v0.2)*
- **50+ Major Cities**: Worldwide destinations including airline hubs and romantic cities
- **Intelligent Hub Selection**: Prioritizes major airports (Reykjavik, Dubai, London, etc.)
- **Smart Routing**: Special handling for trans-Atlantic routes (NYC-London → Reykjavik)
- **Clickable Destinations**: Select any recommended city to generate real date ideas
- **Fairness Algorithm**: Balances travel distance, connectivity, and geographic positioning

### 🔗 **Enhanced Sharing** *(v0.2)*
- **Unique Shareable Links**: Generate secure short URLs for easy sharing
- **Rich Social Previews**: Beautiful Open Graph cards for SMS, email, and social media
- **Dynamic Preview Images**: Custom-generated images with date details
- **Comprehensive Reports**: Full venue information, travel details, and itineraries
- **Flexible Expiration**: Configurable link expiration (24h, 7d, 30d, permanent)
- **View Analytics**: Track engagement and plan success

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/irregularchat/Perfect-Date.git
cd Perfect-Date
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your Google Maps API key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### 4. Run the Application
```bash
python backend.py
```

### 5. Open in Browser
Visit `http://localhost:1090` to start planning perfect dates!

## 🎯 Usage Examples

### Single Location Dating
```
Location: "San Francisco, CA"
Budget: $150  
Vibes: Romantic, Cultural
→ Generates real SF venues with timeline
```

### Two-Location Dating
```
Your Location: "New York, NY"
Date's Location: "Boston, MA"
→ Finds optimal venues around Hartford, CT
→ Shows: You: 115mi, Date: 105mi (91% fair)
```

### Destination Dating
```
Your Location: "Los Angeles, CA"  
Date's Location: "Tokyo, Japan"
→ Suggests: Honolulu, Vancouver, Seattle
→ Click any city for real date ideas there
```

## 🗺️ Google Maps API Setup

Perfect Date Generator requires Google Maps API for real venue data and location services.

### Required APIs
Enable these APIs in [Google Cloud Console](https://console.cloud.google.com/apis/library):
- **Places API** - For venue search and details
- **Geocoding API** - For address/coordinate conversion  
- **Maps JavaScript API** - For interactive maps *(optional)*

### Quick Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to **APIs & Services > Credentials**
4. Click **Create Credentials > API key**
5. Enable the required APIs listed above
6. Add the API key to your `.env` file:
   ```bash
   GOOGLE_MAPS_API_KEY=your_api_key_here
   ```

### Free Tier
Google provides generous free quotas:
- **100,000 requests/month** for Places API
- **40,000 requests/month** for Geocoding API
- Perfect for personal use and testing

## 📱 How to Use

### 1. **Choose Your Mode**
- **Wizard Mode**: Step-by-step guided experience  
- **Classic Mode**: Quick one-page form

### 2. **Set Your Location(s)**
- **Single Location**: Enter your city for local date ideas
- **Two Locations**: Add your date's location for optimal midpoint
- **Long Distance**: Get destination city recommendations

### 3. **Configure Preferences**
- **Event Type**: First date, casual dating, married date, family outing, etc.
- **Budget**: Set your spending limit
- **Vibes**: Romantic, adventurous, relaxed, fun, cultural
- **Time Available**: How many hours you have

### 4. **Get Personalized Results**
- **Activity Timeline**: Detailed schedule with real venues
- **Venue Information**: Ratings, hours, contact details, websites
- **Interactive Maps**: Visual location display with directions
- **Travel Information**: Distance and fairness scores for two-location dates

### 5. **Share Your Plans**
- **Create Shareable Links**: Generate unique URLs for easy sharing
- **Rich Previews**: Beautiful social media cards with date details
- **Collaborative Planning**: Share with your date for input and approval

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.7+** - Core programming language
- **SQLite** - Lightweight database for shared date plans
- **Pydantic** - Data validation and serialization

### APIs & Services  
- **Google Places API** - Real venue data, ratings, and details
- **Google Geocoding API** - Address to coordinate conversion
- **Google Maps JavaScript API** - Interactive map visualization *(optional)*

### Frontend
- **Modern HTML5/CSS3** - Responsive, mobile-first design
- **Vanilla JavaScript** - No framework dependencies
- **Tailwind CSS** - Utility-first styling via CDN
- **Leaflet.js** - Interactive maps and geolocation

### Key Features
- **Advanced Algorithms**: Haversine distance calculation, spherical geometry
- **Real-Time Data**: Live venue information and status updates  
- **Intelligent Routing**: Smart midpoint calculation and destination selection
- **Social Integration**: Rich Open Graph previews and sharing capabilities

## 🤝 Contributing

We welcome contributions! This project follows a clear roadmap with planned features:

- **v0.3**: Advanced personalization engine with user preference learning
- **v0.4**: Real-time features with live availability and traffic data
- **v0.5**: Advanced social features and collaborative planning

See [ROADMAP.md](./ROADMAP.md) for detailed specifications.

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🔮 Future Plans

Perfect Date Generator is evolving into a comprehensive dating platform. Upcoming features include:

- **AI-Powered Personalization** - Learn from user preferences and success rates
- **Real-Time Integration** - Live venue availability, wait times, and traffic
- **Advanced Social Features** - Collaborative planning and community galleries  
- **Mobile App** - Native iOS and Android applications
- **Global Expansion** - Multi-language support and cultural preferences

---

**🎉 Ready to plan your perfect date? [Get started now!](http://localhost:1090)**