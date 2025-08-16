"""
Enhanced Perfect Date Generator Backend
With Google Maps integration and dynamic location handling
"""

import os
import json
import sqlite3
import hashlib
import secrets
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import googlemaps
from datetime import datetime, timedelta

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system environment variables

import uvicorn

app = FastAPI(title="Perfect Date Generator")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Maps client
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY) if GOOGLE_MAPS_API_KEY else None

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Mount static files
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="static")

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), "shared_dates.db")

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shared_date_plans (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            activities TEXT NOT NULL,
            location TEXT NOT NULL,
            date_location TEXT,
            budget INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            vibes TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            view_count INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()

def generate_share_id() -> str:
    """Generate a unique short ID for sharing"""
    return secrets.token_urlsafe(8)[:8].lower()

def get_shared_date_plan(share_id: str) -> Optional[Dict]:
    """Retrieve a shared date plan by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if plan exists and hasn't expired
    cursor.execute("""
        SELECT id, title, activities, location, date_location, budget, 
               event_type, vibes, created_at, expires_at, view_count
        FROM shared_date_plans 
        WHERE id = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
    """, (share_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    return {
        "id": result[0],
        "title": result[1],
        "activities": json.loads(result[2]),
        "location": result[3],
        "date_location": result[4],
        "budget": result[5],
        "event_type": result[6],
        "vibes": json.loads(result[7]),
        "created_at": result[8],
        "expires_at": result[9],
        "view_count": result[10]
    }

def increment_view_count(share_id: str):
    """Increment view count for a shared date plan"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE shared_date_plans SET view_count = view_count + 1 WHERE id = ?", (share_id,))
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

class DateRequest(BaseModel):
    location: str
    budget: int
    event_type: str
    vibes: List[str]
    time_available: Optional[int] = 4

class PlaceDetails(BaseModel):
    name: str
    address: str
    rating: Optional[float]
    price_level: Optional[int]
    location: Dict[str, float]
    place_id: str

class ShareDateRequest(BaseModel):
    activities: List[Dict]
    location: str
    date_location: Optional[str] = None
    budget: int
    event_type: str
    vibes: List[str]
    title: Optional[str] = None
    expiry_hours: Optional[int] = 168  # 7 days default

class SharedDatePlan(BaseModel):
    id: str
    title: str
    activities: List[Dict]
    location: str
    date_location: Optional[str]
    budget: int
    event_type: str
    vibes: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    view_count: int = 0

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the enhanced UI"""
    enhanced_path = os.path.join(STATIC_DIR, "enhanced-ui.html")
    if os.path.exists(enhanced_path):
        return FileResponse(enhanced_path)
    return HTMLResponse("<h1>Perfect Date Generator</h1><p>Enhanced UI not found</p>")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "google_maps": gmaps is not None,
        "api_key_configured": bool(GOOGLE_MAPS_API_KEY)
    }

@app.post("/api/geocode")
async def geocode_location(location: LocationRequest):
    """Convert coordinates to address"""
    if not gmaps:
        # Fallback to OpenStreetMap Nominatim
        return {
            "address": f"{location.latitude}, {location.longitude}",
            "formatted": "Location services not configured"
        }
    
    try:
        result = gmaps.reverse_geocode((location.latitude, location.longitude))
        if result:
            return {
                "address": result[0].get("formatted_address", "Unknown location"),
                "components": result[0].get("address_components", [])
            }
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    return {"address": f"{location.latitude}, {location.longitude}"}

@app.post("/api/generate-date")
async def generate_date(request: DateRequest):
    """Generate date ideas based on location and preferences"""
    
    # Parse location to get coordinates
    lat, lng = 36.8529, -75.9780  # Default to Virginia Beach
    
    if gmaps and request.location:
        try:
            geocode_result = gmaps.geocode(request.location)
            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                lat, lng = location["lat"], location["lng"]
        except Exception as e:
            print(f"Geocoding error: {e}")
    
    # Generate activities based on preferences
    activities = generate_activities(
        event_type=request.event_type,
        budget=request.budget,
        vibes=request.vibes,
        location=(lat, lng),
        time_available=request.time_available
    )
    
    # Find real places if Google Maps is available
    if gmaps:
        activities = enhance_with_real_places(activities, (lat, lng), request.vibes)
    
    return {
        "success": True,
        "center": {"lat": lat, "lng": lng},
        "activities": activities
    }

def generate_activities(event_type: str, budget: int, vibes: List[str], 
                        location: tuple, time_available: int) -> List[Dict]:
    """Generate activity timeline based on preferences"""
    
    base_activities = {
        "first_date": [
            {"time": "6:00 PM", "activity": "Coffee & Conversation", "type": "cafe", "duration": 1.5},
            {"time": "7:30 PM", "activity": "Mini Golf Fun", "type": "entertainment", "duration": 1.5},
            {"time": "9:00 PM", "activity": "Dessert & Walk", "type": "restaurant", "duration": 1}
        ],
        "casual_dating": [
            {"time": "2:00 PM", "activity": "Lunch Together", "type": "restaurant", "duration": 1.5},
            {"time": "3:30 PM", "activity": "Activity Time", "type": "entertainment", "duration": 2},
            {"time": "5:30 PM", "activity": "Drinks & Appetizers", "type": "bar", "duration": 1.5},
            {"time": "7:00 PM", "activity": "Live Entertainment", "type": "entertainment", "duration": 2}
        ],
        "married_date": [
            {"time": "5:00 PM", "activity": "Couples Spa", "type": "spa", "duration": 2},
            {"time": "7:00 PM", "activity": "Fine Dining", "type": "restaurant", "duration": 2},
            {"time": "9:00 PM", "activity": "Dancing & Drinks", "type": "night_club", "duration": 2}
        ],
        "friends_night": [
            {"time": "6:00 PM", "activity": "Group Activity", "type": "bowling_alley", "duration": 2},
            {"time": "8:00 PM", "activity": "Dinner & Drinks", "type": "bar", "duration": 2},
            {"time": "10:00 PM", "activity": "Late Night Fun", "type": "night_club", "duration": 2}
        ],
        "family_outing": [
            {"time": "11:00 AM", "activity": "Family Activity", "type": "museum", "duration": 2},
            {"time": "1:00 PM", "activity": "Lunch Together", "type": "restaurant", "duration": 1.5},
            {"time": "2:30 PM", "activity": "Outdoor Fun", "type": "park", "duration": 2},
            {"time": "4:30 PM", "activity": "Treats & Relaxation", "type": "cafe", "duration": 1}
        ]
    }
    
    activities = base_activities.get(event_type, base_activities["casual_dating"])
    
    # Adjust for vibes
    if "romantic" in vibes:
        activities[0]["activity"] = "🌹 " + activities[0]["activity"]
    if "adventurous" in vibes and len(activities) > 2:
        activities[2]["type"] = "tourist_attraction"
        activities[2]["activity"] = "🎯 Adventure Activity"
    if "cultural" in vibes and len(activities) > 1:
        activities[1]["type"] = "art_gallery"
        activities[1]["activity"] = "🎨 Cultural Experience"
    
    # Adjust for budget
    cost_per_activity = budget / len(activities) if activities else 50
    for i, activity in enumerate(activities):
        activity["estimated_cost"] = min(int(cost_per_activity * (1.2 if i == 1 else 1)), budget // 2)
        activity["location"] = {
            "lat": location[0] + (i * 0.005),  # Slightly offset each location
            "lng": location[1] + (i * 0.005)
        }
    
    # Trim to time available
    max_activities = max(1, time_available // 2)
    activities = activities[:max_activities]
    
    return activities

def generate_smart_search_query(activity_name: str, activity_type: str, vibes: List[str] = None) -> str:
    """Generate intelligent search queries based on activity context and vibes"""
    vibes = vibes or []
    
    # Context-aware search mapping
    search_queries = {
        # Dining activities
        "Lunch Together": ["upscale casual restaurant", "bistro", "farm-to-table restaurant", "local favorite restaurant"],
        "Fine Dining": ["fine dining restaurant", "upscale restaurant", "romantic restaurant", "michelin restaurant"],
        "Coffee & Conversation": ["specialty coffee shop", "local coffee roastery", "artisan coffee", "cozy cafe"],
        "Dessert & Walk": ["dessert shop", "ice cream parlor", "bakery cafe", "gelato shop"],
        "Drinks & Appetizers": ["craft cocktail bar", "wine bar", "gastropub", "rooftop bar"],
        
        # Entertainment activities  
        "Mini Golf Fun": ["mini golf", "family entertainment center", "adventure golf", "putt putt"],
        "Activity Time": ["entertainment venue", "arcade", "bowling alley", "escape room"],
        "Live Entertainment": ["live music venue", "jazz club", "concert hall", "theater"],
        "Dancing & Drinks": ["dance club", "salsa club", "nightclub with dancing", "live music bar"],
        
        # Wellness activities
        "Couples Spa": ["couples spa", "day spa", "wellness center", "massage therapy"],
        
        # Default fallbacks
        "restaurant": ["restaurant", "dining"],
        "entertainment": ["entertainment", "activities"], 
        "bar": ["bar", "pub"],
        "spa": ["spa", "wellness"]
    }
    
    # Get base queries for this activity
    base_queries = search_queries.get(activity_name, search_queries.get(activity_type, ["restaurant"]))
    
    # Modify based on vibes
    if "romantic" in vibes:
        if activity_type == "restaurant":
            base_queries = ["romantic restaurant", "intimate dining", "date night restaurant"]
        elif activity_type == "bar":
            base_queries = ["romantic bar", "wine bar", "intimate lounge"]
        elif activity_type == "entertainment":
            base_queries = ["romantic activities", "couples entertainment", "date night activities"]
    
    if "adventurous" in vibes:
        if activity_type == "entertainment":
            base_queries = ["adventure activities", "escape room", "rock climbing", "unique experiences"]
        
    if "cultural" in vibes:
        if activity_type == "entertainment":
            base_queries = ["art gallery", "museum", "cultural center", "theater"]
            
    # Return a random query from the options for variety
    import random
    return random.choice(base_queries)

def enhance_with_real_places(activities: List[Dict], center: tuple, vibes: List[str] = None) -> List[Dict]:
    """Enhance activities with real Google Places data using intelligent search"""
    if not gmaps:
        return activities
    
    # Get location name for better text search targeting
    location_name = "Fayetteville NC"  # Default
    try:
        reverse_geocode = gmaps.reverse_geocode(center)
        if reverse_geocode:
            city = None
            state = None
            # Extract city and state from the first result
            for component in reverse_geocode[0].get("address_components", []):
                if "locality" in component.get("types", []):
                    city = component["long_name"]
                elif "administrative_area_level_1" in component.get("types", []):
                    state = component["short_name"]
            if city and state:
                location_name = f"{city} {state}"
    except Exception as e:
        print(f"Reverse geocoding failed: {e}")
    
    print(f"Using location: {location_name} at coordinates {center}")
    
    enhanced = []
    used_place_ids = set()  # Track used places to ensure diversity
    
    for activity in activities:
        try:
            # Generate intelligent search query
            search_query = generate_smart_search_query(
                activity.get("activity", ""), 
                activity.get("type", ""), 
                vibes
            )
            
            print(f"Searching for: '{search_query}' for activity '{activity.get('activity')}'")
            
            # Try places_nearby first for location accuracy, then fallback to text search
            places_result = None
            
            # Map search queries to Google Places types for nearby search
            type_mapping = {
                "restaurant": "restaurant",
                "fine dining": "restaurant", 
                "romantic restaurant": "restaurant",
                "upscale restaurant": "restaurant",
                "date night restaurant": "restaurant",
                "bistro": "restaurant",
                "cafe": "cafe",
                "coffee": "cafe",
                "specialty coffee": "cafe",
                "spa": "spa",
                "day spa": "spa",
                "couples spa": "spa",
                "wellness": "spa",
                "bar": "bar",
                "wine bar": "bar",
                "cocktail bar": "bar",
                "dance club": "night_club",
                "nightclub": "night_club",
                "entertainment": "amusement_park",
                "arcade": "amusement_park",
                "bowling": "bowling_alley",
                "mini golf": "amusement_park"
            }
            
            # Get Google Places type from search query
            places_type = None
            for key, ptype in type_mapping.items():
                if key in search_query.lower():
                    places_type = ptype
                    break
            
            # First try nearby search for location accuracy
            if places_type:
                try:
                    places_result = gmaps.places_nearby(
                        location=center,
                        radius=8000,  # 8km radius
                        type=places_type,
                        language="en"
                    )
                    print(f"Nearby search for type '{places_type}' returned {len(places_result.get('results', []))} results")
                except Exception as e:
                    print(f"Nearby search failed: {e}")
            
            # Fallback to text search if nearby didn't work or no results
            if not places_result or not places_result.get("results"):
                try:
                    # Include location in the query text for better targeting
                    places_result = gmaps.places(
                        query=f"{search_query} in {location_name}",
                        language="en"
                    )
                    print(f"Text search for '{search_query} in {location_name}' returned {len(places_result.get('results', []))} results")
                except Exception as e:
                    print(f"Text search failed: {e}")
            
            # Find the first place that hasn't been used yet
            selected_place = None
            if places_result.get("results"):
                for place in places_result["results"]:
                    if place["place_id"] not in used_place_ids:
                        selected_place = place
                        used_place_ids.add(place["place_id"])
                        break
                
                # If all places were used, use the first one anyway
                if not selected_place and places_result["results"]:
                    selected_place = places_result["results"][0]
            
            if selected_place:
                # Get detailed place info
                place_details = gmaps.place(
                    place_id=selected_place["place_id"],
                    fields=["name", "formatted_address", "rating", "price_level", 
                           "geometry", "opening_hours", "website", "formatted_phone_number"]
                )
                
                if place_details.get("result"):
                    detail = place_details["result"]
                    activity["place_name"] = detail.get("name", activity["activity"])
                    activity["address"] = detail.get("formatted_address", "")
                    activity["rating"] = detail.get("rating", 0)
                    activity["price_level"] = detail.get("price_level", 2)
                    activity["location"] = {
                        "lat": detail["geometry"]["location"]["lat"],
                        "lng": detail["geometry"]["location"]["lng"]
                    }
                    activity["place_id"] = selected_place["place_id"]
                    activity["website"] = detail.get("website", "")
                    activity["phone"] = detail.get("formatted_phone_number", "")
                    
                    # Check if currently open
                    if detail.get("opening_hours"):
                        activity["open_now"] = detail["opening_hours"].get("open_now", None)
                        
                    # Set appropriate estimated cost based on rating and price level
                    price_level = activity.get("price_level", 2)
                    base_cost = 20 + (price_level * 20)  # $20-$100 range
                    activity["estimated_cost"] = base_cost
                    
                    print(f"Found: {activity['place_name']} - {activity['address']}")
                else:
                    print(f"Could not get details for place: {selected_place.get('name')}")
            else:
                print(f"No places found for query: {search_query}")
                
        except Exception as e:
            print(f"Error enhancing place: {e}")
        
        enhanced.append(activity)
    
    return enhanced

@app.get("/api/search-places")
async def search_places(query: str, location: str, radius: int = 5000):
    """Search for places near a location"""
    if not gmaps:
        return {"places": [], "error": "Maps service not configured"}
    
    try:
        # Geocode the location first
        geocode_result = gmaps.geocode(location)
        if not geocode_result:
            return {"places": [], "error": "Location not found"}
        
        center = geocode_result[0]["geometry"]["location"]
        
        # Search for places
        places_result = gmaps.places(
            query=query,
            location=(center["lat"], center["lng"]),
            radius=radius
        )
        
        places = []
        for place in places_result.get("results", [])[:5]:
            places.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating"),
                "place_id": place.get("place_id"),
                "location": place.get("geometry", {}).get("location", {})
            })
        
        return {"places": places}
    except Exception as e:
        return {"places": [], "error": str(e)}

@app.post("/api/share-date")
async def create_shared_date(request: ShareDateRequest):
    """Create a shareable link for a date plan"""
    try:
        # Generate unique ID
        share_id = generate_share_id()
        
        # Ensure ID is unique
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        while True:
            cursor.execute("SELECT id FROM shared_date_plans WHERE id = ?", (share_id,))
            if not cursor.fetchone():
                break
            share_id = generate_share_id()
        
        # Calculate expiry time
        expires_at = None
        if request.expiry_hours and request.expiry_hours > 0:
            expires_at = datetime.now() + timedelta(hours=request.expiry_hours)
        
        # Generate title if not provided
        title = request.title
        if not title:
            location_name = request.location
            if request.date_location and request.date_location != request.location:
                location_name = f"{request.location} & {request.date_location}"
            title = f"{request.event_type.replace('_', ' ').title()} in {location_name}"
        
        # Store in database
        cursor.execute("""
            INSERT INTO shared_date_plans 
            (id, title, activities, location, date_location, budget, event_type, vibes, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            share_id,
            title,
            json.dumps(request.activities),
            request.location,
            request.date_location,
            request.budget,
            request.event_type,
            json.dumps(request.vibes),
            expires_at.isoformat() if expires_at else None
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "share_id": share_id,
            "share_url": f"/shared/{share_id}",
            "expires_at": expires_at.isoformat() if expires_at else None,
            "title": title
        }
        
    except Exception as e:
        print(f"Error creating shared date: {e}")
        raise HTTPException(status_code=500, detail="Failed to create shareable link")

@app.get("/api/shared/{share_id}")
async def get_shared_date(share_id: str):
    """Get a shared date plan by ID"""
    try:
        plan = get_shared_date_plan(share_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Date plan not found or expired")
        
        # Increment view count
        increment_view_count(share_id)
        
        return {
            "success": True,
            "plan": plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving shared date: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve date plan")

@app.get("/shared/{share_id}", response_class=HTMLResponse)
async def view_shared_date(share_id: str):
    """View a shared date plan in the browser"""
    try:
        plan = get_shared_date_plan(share_id)
        if not plan:
            return HTMLResponse(
                content="<h1>Date Plan Not Found</h1><p>This date plan may have expired or doesn't exist.</p>",
                status_code=404
            )
        
        # Increment view count
        increment_view_count(share_id)
        
        # Return the main app with the shared plan data and Open Graph meta tags
        enhanced_path = os.path.join(STATIC_DIR, "enhanced-ui.html")
        if os.path.exists(enhanced_path):
            with open(enhanced_path, 'r') as f:
                html_content = f.read()
            
            # Generate Open Graph meta tags
            og_meta_tags = generate_open_graph_tags(plan, share_id)
            
            # Inject Open Graph meta tags
            html_content = html_content.replace(
                '<title>Perfect Date Generator - Enhanced UI</title>',
                f'<title>{plan["title"]} - Perfect Date Generator</title>\n{og_meta_tags}'
            )
            
            # Inject the shared plan data into the HTML
            plan_json = json.dumps(plan).replace('"', '&quot;')
            html_content = html_content.replace(
                '<body>',
                f'<body data-shared-plan="{plan_json}">'
            )
            
            return HTMLResponse(content=html_content)
        
        return HTMLResponse("<h1>Date Plan Viewer</h1><p>Shared date plan interface not available</p>")
        
    except Exception as e:
        print(f"Error viewing shared date: {e}")
        return HTMLResponse(
            content="<h1>Error</h1><p>Failed to load date plan</p>",
            status_code=500
        )

def generate_open_graph_tags(plan: Dict, share_id: str) -> str:
    """Generate Open Graph meta tags for rich link previews"""
    
    # Extract key information
    title = plan["title"]
    location_text = plan["location"]
    if plan.get("date_location") and plan["date_location"] != plan["location"]:
        location_text = f"{plan['location']} & {plan['date_location']}"
    
    activity_count = len(plan["activities"])
    budget = plan["budget"]
    event_type = plan["event_type"].replace("_", " ").title()
    
    # Generate description
    description = f"{event_type} with {activity_count} activities in {location_text}. Budget: ${budget}."
    if plan["vibes"]:
        description += f" Vibes: {', '.join(plan['vibes'])}."
    
    # Current domain (should be configurable in production)
    domain = "localhost:1090"  # This should be read from environment or config
    share_url = f"http://{domain}/shared/{share_id}"
    
    # Generate activity summary for rich preview
    activity_summary = ""
    if plan["activities"]:
        top_activities = plan["activities"][:3]  # Show first 3 activities
        activity_list = [f"• {activity.get('activity', activity.get('place_name', 'Activity'))}" for activity in top_activities]
        activity_summary = "\n".join(activity_list)
        if len(plan["activities"]) > 3:
            activity_summary += f"\n...and {len(plan['activities']) - 3} more"
    
    # Meta tags for rich previews
    meta_tags = f"""
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{share_url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="http://{domain}/api/og-image/{share_id}">
    <meta property="og:site_name" content="Perfect Date Generator">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{share_url}">
    <meta property="twitter:title" content="{title}">
    <meta property="twitter:description" content="{description}">
    <meta property="twitter:image" content="http://{domain}/api/og-image/{share_id}">
    
    <!-- Additional Meta -->
    <meta name="description" content="{description}">
    <meta property="article:author" content="Perfect Date Generator">
    <meta property="article:section" content="Date Planning">
    """
    
    return meta_tags

@app.get("/api/og-image/{share_id}")
async def generate_og_image(share_id: str):
    """Generate Open Graph image for shared date plan"""
    try:
        plan = get_shared_date_plan(share_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Date plan not found")
        
        # For now, return a simple SVG image with plan details
        # In production, you might want to use PIL or another image library
        svg_content = generate_og_svg(plan)
        
        return HTMLResponse(
            content=svg_content,
            headers={"Content-Type": "image/svg+xml"}
        )
        
    except Exception as e:
        print(f"Error generating OG image: {e}")
        # Return a default image
        default_svg = """
        <svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#6366f1"/>
            <text x="600" y="315" text-anchor="middle" fill="white" font-size="48" font-family="Arial">
                Perfect Date Generator
            </text>
        </svg>
        """
        return HTMLResponse(
            content=default_svg,
            headers={"Content-Type": "image/svg+xml"}
        )

def generate_og_svg(plan: Dict) -> str:
    """Generate SVG image for Open Graph preview"""
    title = plan["title"]
    location = plan["location"]
    if plan.get("date_location") and plan["date_location"] != plan["location"]:
        location = f"{plan['location']} & {plan['date_location']}"
    
    activity_count = len(plan["activities"])
    budget = plan["budget"]
    
    # Get first few activities for display
    activities_text = ""
    if plan["activities"]:
        top_3 = plan["activities"][:3]
        for i, activity in enumerate(top_3):
            activity_name = activity.get("activity", activity.get("place_name", "Activity"))
            activities_text += f"<text x='60' y='{400 + i * 40}' fill='white' font-size='24' font-family='Arial'>{i+1}. {activity_name}</text>"
    
    svg = f"""
    <svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
        <!-- Background gradient -->
        <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#6366f1;stop-opacity:1" />
                <stop offset="50%" style="stop-color:#8b5cf6;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#ec4899;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#grad1)"/>
        
        <!-- Content -->
        <text x="60" y="120" fill="white" font-size="48" font-weight="bold" font-family="Arial">{title}</text>
        <text x="60" y="180" fill="white" font-size="32" font-family="Arial">📍 {location}</text>
        <text x="60" y="230" fill="white" font-size="28" font-family="Arial">💰 ${budget} Budget • {activity_count} Activities</text>
        
        <!-- Activities -->
        <text x="60" y="320" fill="white" font-size="32" font-weight="bold" font-family="Arial">Itinerary:</text>
        {activities_text}
        
        <!-- Branding -->
        <text x="1140" y="600" text-anchor="end" fill="white" font-size="20" font-family="Arial">Perfect Date Generator</text>
    </svg>
    """
    
    return svg

if __name__ == "__main__":
    # Check for API key
    if not GOOGLE_MAPS_API_KEY:
        print("⚠️  WARNING: GOOGLE_MAPS_API_KEY not set in environment")
        print("   Location features will be limited")
    else:
        print("✅ Google Maps API configured")
    
    print(f"🚀 Starting server at http://localhost:1090")
    print(f"📁 Serving static files from {STATIC_DIR}")
    
    uvicorn.run(app, host="0.0.0.0", port=1090)