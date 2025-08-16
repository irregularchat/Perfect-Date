"""
Enhanced Perfect Date Generator Backend
With Google Maps integration and dynamic location handling
"""

import os
import json
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import googlemaps
from datetime import datetime

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system environment variables

import uvicorn
import math

app = FastAPI(title="Perfect Date Generator")

# Geographic calculation utilities
def haversine_distance(coord1: tuple, coord2: tuple) -> float:
    """
    Calculate the great circle distance between two points on Earth in kilometers
    using the Haversine formula
    
    Args:
        coord1: (latitude, longitude) tuple for point 1
        coord2: (latitude, longitude) tuple for point 2
    
    Returns:
        Distance in kilometers
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers
    r = 6371
    
    return c * r

def calculate_midpoint_and_radius(location1: tuple, location2: tuple) -> tuple:
    """
    Calculate optimal meeting point and search radius for two locations
    
    Args:
        location1: (lat, lng) tuple for person 1
        location2: (lat, lng) tuple for person 2
    
    Returns:
        (midpoint, radius) where midpoint is (lat, lng) and radius is in meters
        
    Raises:
        ValueError: If the distance is too large for practical dating
    """
    if location1 == location2:
        # Same location, use small radius around that point
        return location1, 5000
    
    # Calculate distance first to validate practicality
    distance_km = haversine_distance(location1, location2)
    
    # Validate realistic dating distances
    if distance_km > 1000:  # More than 1000km (620 miles) apart
        raise ValueError(f"Distance too large for dating: {distance_km:.0f} km ({distance_km * 0.621371:.0f} miles). "
                        f"Two-location dating works best for people within 620 miles of each other. "
                        f"Consider using single-location mode instead.")
    
    if distance_km > 500:  # 500-1000km - warn but allow
        print(f"WARNING: Very long distance ({distance_km:.0f} km). Midpoint may be impractical.")
    
    # Calculate geographic midpoint using spherical geometry
    lat1, lon1 = map(math.radians, location1)
    lat2, lon2 = map(math.radians, location2)
    
    # Convert to cartesian coordinates
    x1 = math.cos(lat1) * math.cos(lon1)
    y1 = math.cos(lat1) * math.sin(lon1)
    z1 = math.sin(lat1)
    
    x2 = math.cos(lat2) * math.cos(lon2)
    y2 = math.cos(lat2) * math.sin(lon2)
    z2 = math.sin(lat2)
    
    # Average the cartesian coordinates
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    z = (z1 + z2) / 2
    
    # Convert back to spherical coordinates
    hyp = math.sqrt(x * x + y * y)
    midpoint_lat = math.atan2(z, hyp)
    midpoint_lon = math.atan2(y, x)
    
    # Convert back to degrees
    midpoint = (math.degrees(midpoint_lat), math.degrees(midpoint_lon))
    
    # Smart radius based on distance (from roadmap specifications)
    if distance_km < 8:      # Close by (< 5 miles)
        radius = min(4800, distance_km * 1000 * 0.6)  # 60%, max 3 miles
    elif distance_km < 32:   # Medium distance (< 20 miles)
        radius = min(16000, distance_km * 1000 * 0.4) # 40%, max 10 miles
    elif distance_km < 80:   # Long distance (< 50 miles)
        radius = min(24000, distance_km * 1000 * 0.3) # 30%, max 15 miles
    elif distance_km < 200:  # Very long distance (< 125 miles)
        radius = min(40000, distance_km * 1000 * 0.25) # 25%, max 25 miles
    else:                    # Extremely long distance
        radius = min(80000, distance_km * 1000 * 0.15) # 15%, max 50 miles
    
    print(f"Calculated midpoint {midpoint} with radius {radius}m for locations {distance_km:.1f}km apart")
    
    return midpoint, int(radius)

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

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

class DateRequest(BaseModel):
    location: str
    date_location: Optional[str] = None  # New field for date's location
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
    
    # Parse primary location to get coordinates
    lat1, lng1 = 35.0526, -78.8783  # Default to Fayetteville, NC
    
    if gmaps and request.location:
        try:
            geocode_result = gmaps.geocode(request.location)
            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                lat1, lng1 = location["lat"], location["lng"]
        except Exception as e:
            print(f"Geocoding error for location 1: {e}")
    
    # Handle two-location dating feature
    search_center = (lat1, lng1)
    search_radius = 8000  # Default 8km radius
    
    if request.date_location and request.date_location.strip():
        # Parse date's location
        lat2, lng2 = lat1, lng1  # Default to same location
        
        if gmaps:
            try:
                geocode_result = gmaps.geocode(request.date_location)
                if geocode_result:
                    location = geocode_result[0]["geometry"]["location"]
                    lat2, lng2 = location["lat"], location["lng"]
                    
                    # Calculate optimal midpoint and search radius
                    try:
                        search_center, search_radius = calculate_midpoint_and_radius(
                            (lat1, lng1), (lat2, lng2)
                        )
                        
                        print(f"Two-location mode: Person 1 at ({lat1:.4f}, {lng1:.4f}), Person 2 at ({lat2:.4f}, {lng2:.4f})")
                        print(f"Search center: ({search_center[0]:.4f}, {search_center[1]:.4f}), radius: {search_radius}m")
                        
                    except ValueError as e:
                        # Distance too large for practical dating
                        print(f"Distance validation failed: {e}")
                        return {
                            "success": False,
                            "error": "distance_too_large",
                            "message": str(e),
                            "suggestion": "Try using single-location mode, or choose locations closer together (within 620 miles).",
                            "distance_km": haversine_distance((lat1, lng1), (lat2, lng2))
                        }
                    
            except Exception as e:
                print(f"Geocoding error for date location: {e}")
    
    # Generate activities based on preferences
    activities = generate_activities(
        event_type=request.event_type,
        budget=request.budget,
        vibes=request.vibes,
        location=search_center,
        time_available=request.time_available
    )
    
    # Find real places if Google Maps is available
    if gmaps:
        activities = enhance_with_real_places(
            activities, 
            search_center, 
            request.vibes,
            custom_radius=search_radius
        )
    
    # Add travel information for two-location mode
    for activity in activities:
        if request.date_location and request.date_location.strip():
            # Calculate distances for both people
            venue_location = (activity["location"]["lat"], activity["location"]["lng"])
            
            distance1_km = haversine_distance((lat1, lng1), venue_location)
            distance2_km = haversine_distance((lat2, lng2), venue_location)
            
            activity["travel_person1"] = {
                "distance_km": round(distance1_km, 1),
                "distance_mi": round(distance1_km * 0.621371, 1)
            }
            activity["travel_person2"] = {
                "distance_km": round(distance2_km, 1), 
                "distance_mi": round(distance2_km * 0.621371, 1)
            }
            
            # Calculate fairness score (0-100, where 100 is perfectly fair)
            max_distance = max(distance1_km, distance2_km)
            min_distance = min(distance1_km, distance2_km)
            if max_distance > 0:
                fairness_score = (min_distance / max_distance) * 100
            else:
                fairness_score = 100
            activity["fairness_score"] = round(fairness_score, 1)
    
    return {
        "success": True,
        "center": {"lat": search_center[0], "lng": search_center[1]},
        "two_location_mode": bool(request.date_location and request.date_location.strip()),
        "search_radius_km": search_radius / 1000,
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

def enhance_with_real_places(activities: List[Dict], center: tuple, vibes: List[str] = None, custom_radius: int = None) -> List[Dict]:
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
                # Use custom radius if provided, otherwise use 8km default
                search_radius = custom_radius if custom_radius is not None else 8000
                try:
                    places_result = gmaps.places_nearby(
                        location=center,
                        radius=search_radius,
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