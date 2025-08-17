"""
Enhanced Perfect Date Generator Backend
With Google Maps integration and dynamic location handling
"""

import os
import json
import sqlite3
import hashlib
import secrets
import math
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
import math
from typing import Tuple, List

app = FastAPI(title="Perfect Date Generator")

# Major cities and airports for long-distance midpoint dating
MAJOR_DESTINATIONS = {
    # North America
    "New York, NY": (40.7128, -74.0060),
    "Los Angeles, CA": (34.0522, -118.2437),
    "Chicago, IL": (41.8781, -87.6298),
    "Toronto, ON": (43.6532, -79.3832),
    "Vancouver, BC": (49.2827, -123.1207),
    "Miami, FL": (25.7617, -80.1918),
    "Las Vegas, NV": (36.1699, -115.1398),
    "San Francisco, CA": (37.7749, -122.4194),
    "Denver, CO": (39.7392, -104.9903),
    "Seattle, WA": (47.6062, -122.3321),
    "Atlanta, GA": (33.7490, -84.3880),
    "Dallas, TX": (32.7767, -96.7970),
    "Phoenix, AZ": (33.4484, -112.0740),
    "Boston, MA": (42.3601, -71.0589),
    "Washington, DC": (38.9072, -77.0369),
    
    # Europe
    "London, UK": (51.5074, -0.1278),
    "Paris, France": (48.8566, 2.3522),
    "Amsterdam, Netherlands": (52.3676, 4.9041),
    "Rome, Italy": (41.9028, 12.4964),
    "Barcelona, Spain": (41.3851, 2.1734),
    "Berlin, Germany": (52.5200, 13.4050),
    "Vienna, Austria": (48.2082, 16.3738),
    "Zurich, Switzerland": (47.3769, 8.5417),
    "Stockholm, Sweden": (59.3293, 18.0686),
    "Copenhagen, Denmark": (55.6761, 12.5683),
    
    # Asia-Pacific
    "Tokyo, Japan": (35.6762, 139.6503),
    "Seoul, South Korea": (37.5665, 126.9780),
    "Shanghai, China": (31.2304, 121.4737),
    "Beijing, China": (39.9042, 116.4074),
    "Hong Kong": (22.3193, 114.1694),
    "Singapore": (1.3521, 103.8198),
    "Sydney, Australia": (-33.8688, 151.2093),
    "Melbourne, Australia": (-37.8136, 144.9631),
    "Bangkok, Thailand": (13.7563, 100.5018),
    "Mumbai, India": (19.0760, 72.8777),
    "Delhi, India": (28.7041, 77.1025),
    
    # Key Airports/Hubs
    "Reykjavik, Iceland": (64.1466, -21.9426),  # Great for US-Europe
    "Anchorage, AK": (61.2181, -149.9003),     # Great for US-Asia via polar route
    "Honolulu, HI": (21.3099, -157.8581),      # Pacific hub
    "Panama City, Panama": (8.9824, -79.5199), # Central America hub
    "Dubai, UAE": (25.2048, 55.2708),          # Middle East hub
}

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

def find_destination_cities(location1: tuple, location2: tuple, num_suggestions: int = 3) -> List[dict]:
    """
    Find major cities/airports that make good meeting destinations for long-distance dating
    
    Args:
        location1: (lat, lng) tuple for person 1
        location2: (lat, lng) tuple for person 2
        num_suggestions: Number of destination suggestions to return
    
    Returns:
        List of destination dictionaries with city info and travel distances
    """
    actual_midpoint_lat, actual_midpoint_lng = calculate_geographic_midpoint(location1, location2)
    total_distance = haversine_distance(location1, location2)
    
    destination_scores = []
    
    for city_name, city_coords in MAJOR_DESTINATIONS.items():
        # Calculate distances from each person to this destination
        dist1 = haversine_distance(location1, city_coords)
        dist2 = haversine_distance(location2, city_coords)
        
        # Calculate fairness score (prefer cities where both people travel similar distances)
        max_dist = max(dist1, dist2)
        min_dist = min(dist1, dist2)
        fairness_score = (min_dist / max_dist) * 100 if max_dist > 0 else 100
        
        # Calculate distance from actual geographic midpoint (prefer cities closer to true midpoint)
        midpoint_distance = haversine_distance((actual_midpoint_lat, actual_midpoint_lng), city_coords)
        midpoint_score = max(0, 100 - (midpoint_distance / 100))  # Penalty for being far from midpoint
        
        # Calculate total travel burden (prefer destinations that minimize total travel)
        total_travel = dist1 + dist2
        travel_efficiency = max(0, 100 - ((total_travel - total_distance) / total_distance * 100))
        
        # Combined score: fairness (40%), midpoint proximity (30%), travel efficiency (30%)
        combined_score = (fairness_score * 0.4) + (midpoint_score * 0.3) + (travel_efficiency * 0.3)
        
        # Bonus for major airline hubs for international travel
        hub_bonus = 0
        if "UK" in city_name or "Iceland" in city_name or "AK" in city_name or "Dubai" in city_name:
            hub_bonus = 10
        
        destination_scores.append({
            "city": city_name,
            "coordinates": city_coords,
            "distance_person1_km": dist1,
            "distance_person1_mi": dist1 * 0.621371,
            "distance_person2_km": dist2,
            "distance_person2_mi": dist2 * 0.621371,
            "fairness_score": fairness_score,
            "total_travel_km": total_travel,
            "total_travel_mi": total_travel * 0.621371,
            "score": combined_score + hub_bonus,
            "is_hub": hub_bonus > 0
        })
    
    # Sort by score and return top suggestions
    destination_scores.sort(key=lambda x: x["score"], reverse=True)
    return destination_scores[:num_suggestions]

def calculate_geographic_midpoint(location1: tuple, location2: tuple) -> tuple:
    """Calculate the pure geographic midpoint (used for destination scoring)"""
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
    
    return (math.degrees(midpoint_lat), math.degrees(midpoint_lon))

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

def haversine_distance(coord1: tuple, coord2: tuple) -> float:
    """Calculate the great-circle distance between two points on Earth"""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Earth radius in kilometers
    return c * r

def calculate_midpoint_and_radius(location1: tuple, location2: tuple) -> tuple:
    """Calculate optimal meeting point and search radius for two locations"""
    # Distance validation with 620-mile practical limit
    distance_km = haversine_distance(location1, location2)
    if distance_km > 1000:  # ~620 miles
        raise ValueError(f"Distance too large for practical dating: {distance_km:.0f} km. Consider destination dating instead.")
    
    # Geographic midpoint using spherical geometry
    lat1, lon1 = map(math.radians, location1)
    lat2, lon2 = map(math.radians, location2)
    
    # Convert to cartesian coordinates
    x1, y1, z1 = math.cos(lat1) * math.cos(lon1), math.cos(lat1) * math.sin(lon1), math.sin(lat1)
    x2, y2, z2 = math.cos(lat2) * math.cos(lon2), math.cos(lat2) * math.sin(lon2), math.sin(lat2)
    
    # Average coordinates
    x, y, z = (x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2
    
    # Convert back to lat/lng
    lon = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat = math.atan2(z, hyp)
    
    midpoint = (math.degrees(lat), math.degrees(lon))
    
    # Smart radius based on distance between locations
    if distance_km < 8:      # Close by (< 5 miles)
        radius = min(4800, distance_km * 1000 * 0.6)  # 60%, max 3 miles
    elif distance_km < 32:   # Medium distance (< 20 miles)
        radius = min(16000, distance_km * 1000 * 0.4) # 40%, max 10 miles  
    elif distance_km < 80:   # Long distance (< 50 miles)
        radius = min(24000, distance_km * 1000 * 0.3) # 30%, max 15 miles
    else:                    # Very long distance
        radius = min(40000, distance_km * 1000 * 0.2) # 20%, max 25 miles
    
    return midpoint, int(radius), distance_km

# Destination cities for long-distance dating
DESTINATION_CITIES = [
    {"name": "New York, NY", "lat": 40.7128, "lng": -74.0060},
    {"name": "Los Angeles, CA", "lat": 34.0522, "lng": -118.2437},
    {"name": "Chicago, IL", "lat": 41.8781, "lng": -87.6298},
    {"name": "Miami, FL", "lat": 25.7617, "lng": -80.1918},
    {"name": "Las Vegas, NV", "lat": 36.1699, "lng": -115.1398},
    {"name": "San Francisco, CA", "lat": 37.7749, "lng": -122.4194},
    {"name": "Seattle, WA", "lat": 47.6062, "lng": -122.3321},
    {"name": "Nashville, TN", "lat": 36.1627, "lng": -86.7816},
    {"name": "Austin, TX", "lat": 30.2672, "lng": -97.7431},
    {"name": "Denver, CO", "lat": 39.7392, "lng": -104.9903},
    {"name": "Boston, MA", "lat": 42.3601, "lng": -71.0589},
    {"name": "Atlanta, GA", "lat": 33.7490, "lng": -84.3880},
    {"name": "Phoenix, AZ", "lat": 33.4484, "lng": -112.0740},
    {"name": "Portland, OR", "lat": 45.5152, "lng": -122.6784},
    {"name": "San Diego, CA", "lat": 32.7157, "lng": -117.1611},
    {"name": "Washington, DC", "lat": 38.9072, "lng": -77.0369},
    {"name": "Philadelphia, PA", "lat": 39.9526, "lng": -75.1652},
    {"name": "New Orleans, LA", "lat": 29.9511, "lng": -90.0715},
    {"name": "Charleston, SC", "lat": 32.7765, "lng": -79.9311},
    {"name": "Savannah, GA", "lat": 32.0835, "lng": -81.0998}
]

def find_destination_cities(location1: tuple, location2: tuple, count: int = 5) -> List[Dict]:
    """Find destination cities for long-distance dating"""
    suggestions = []
    
    for city in DESTINATION_CITIES:
        city_coord = (city["lat"], city["lng"])
        dist1 = haversine_distance(location1, city_coord)
        dist2 = haversine_distance(location2, city_coord)
        total_dist = dist1 + dist2
        fairness = abs(dist1 - dist2) / max(dist1, dist2)  # Lower is more fair
        
        # Score based on total distance and fairness
        score = 1000 / total_dist - fairness * 100
        
        suggestions.append({
            "name": city["name"],
            "lat": city["lat"],
            "lng": city["lng"],
            "distance_person1": round(dist1, 1),
            "distance_person2": round(dist2, 1),
            "total_distance": round(total_dist, 1),
            "fairness_score": round((1 - fairness) * 100, 1),
            "score": round(score, 2)
        })
    
    # Sort by score and return top suggestions
    suggestions.sort(key=lambda x: x["score"], reverse=True)
    return suggestions[:count]

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
    is_two_location = False
    distance_info = None
    destination_suggestions = None
    
    if request.date_location and request.date_location.strip():
        # Parse date's location
        lat2, lng2 = lat1, lng1  # Default to same location
        
        if gmaps:
            try:
                geocode_result = gmaps.geocode(request.date_location)
                if geocode_result:
                    location = geocode_result[0]["geometry"]["location"]
                    lat2, lng2 = location["lat"], location["lng"]
                    
                    # Calculate distance first
                    distance_km = haversine_distance((lat1, lng1), (lat2, lng2))
                    
                    if distance_km > 1000:  # ~620 miles - too far for midpoint
                        # Suggest destination cities instead
                        destination_suggestions = find_destination_cities((lat1, lng1), (lat2, lng2))
                        return {
                            "success": True,
                            "two_location": True,
                            "long_distance": True,
                            "distance_km": round(distance_km, 1),
                            "destination_suggestions": destination_suggestions,
                            "message": f"The distance ({distance_km:.0f} km) is too large for midpoint dating. Here are some great destination cities for your date!"
                        }
                    else:
                        # Calculate optimal midpoint and search radius
                        try:
                            search_center, search_radius, distance_km = calculate_midpoint_and_radius(
                                (lat1, lng1), (lat2, lng2)
                            )
                            is_two_location = True
                            
                            print(f"Two-location mode: Person 1 at ({lat1:.4f}, {lng1:.4f}), Person 2 at ({lat2:.4f}, {lng2:.4f})")
                            print(f"Search center: ({search_center[0]:.4f}, {search_center[1]:.4f}), radius: {search_radius}m")
                            
                            # Calculate travel distances
                            midpoint_to_location1 = haversine_distance(search_center, (lat1, lng1))
                            midpoint_to_location2 = haversine_distance(search_center, (lat2, lng2))
                            
                            distance_info = {
                                "total_distance_km": round(distance_km, 1),
                                "person1_travel_km": round(midpoint_to_location1, 1),
                                "person2_travel_km": round(midpoint_to_location2, 1),
                                "fairness_score": round(100 - (abs(midpoint_to_location1 - midpoint_to_location2) / max(midpoint_to_location1, midpoint_to_location2)) * 100, 1),
                                "search_radius_km": round(search_radius / 1000, 1)
                            }
                            
                        except ValueError as e:
                            print(f"Distance validation failed: {e}")
                            # Fall back to single location
                            is_two_location = False
                    
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
    if is_two_location:
        for activity in activities:
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
    
    response = {
        "success": True,
        "center": {"lat": search_center[0], "lng": search_center[1]},
        "activities": activities,
        "two_location": is_two_location,
        "two_location_mode": is_two_location,
        "search_radius_km": search_radius / 1000
    }
    
    if distance_info:
        response["distance_info"] = distance_info
    
    if is_two_location:
        response["message"] = f"Perfect! Found the optimal midpoint for both locations ({distance_info['total_distance_km']} km apart)"
    
    return response

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