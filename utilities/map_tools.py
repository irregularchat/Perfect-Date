import os
import folium
import googlemaps
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Google Maps client with fallback
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = None

if GOOGLE_MAPS_API_KEY:
    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    except Exception as e:
        print(f"Error initializing Google Maps client: {str(e)}")

def is_maps_available() -> bool:
    """Check if Google Maps API is available"""
    return gmaps is not None

def search_places(location: str, query: str, radius: int = 5000) -> List[Dict]:
    """
    Search for places based on location and query.
    
    Args:
        location (str): Location to search around (e.g., "Seattle, WA")
        query (str): Search query (e.g., "Italian restaurant")
        radius (int): Search radius in meters (default: 5000)
        
    Returns:
        List[Dict]: List of place results with basic information
    """
    if not is_maps_available():
        return []
        
    try:
        # First, geocode the location to get coordinates
        geocode_result = gmaps.geocode(location)
        
        if not geocode_result:
            return []
            
        # Get the latitude and longitude
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        
        # Search for places
        places_result = gmaps.places_nearby(
            location=(lat, lng),
            keyword=query,
            radius=radius,
            open_now=True  # Only return places that are open now
        )
        
        return places_result.get('results', [])
    except Exception as e:
        print(f"Error searching for places: {str(e)}")
        return []

def get_place_details(place_id: str) -> Dict:
    """
    Get detailed information about a place.
    
    Args:
        place_id (str): Google Place ID
        
    Returns:
        Dict: Place details including reviews, opening hours, etc.
    """
    if not is_maps_available():
        return {}
        
    try:
        place_details = gmaps.place(
            place_id=place_id,
            fields=['name', 'formatted_address', 'formatted_phone_number', 
                   'opening_hours', 'rating', 'reviews', 'website', 'price_level',
                   'geometry', 'photos']
        )
        
        return place_details.get('result', {})
    except Exception as e:
        print(f"Error getting place details: {str(e)}")
        return {}

def create_map(places: List[Dict], center_location: str = None) -> str:
    """
    Create an interactive map with markers for the given places.
    
    Args:
        places (List[Dict]): List of place dictionaries with location information
        center_location (str, optional): Location to center the map on
        
    Returns:
        str: HTML string of the map
    """
    try:
        # If no Google Maps API or no places, return simple message with default map
        if not is_maps_available() or (not places and not center_location):
            # Default to a view of the US
            map_center = [37.0902, -95.7129]
            zoom_start = 4
            m = folium.Map(location=map_center, zoom_start=zoom_start)
            return m._repr_html_()
            
        # If no places but we have a center location and maps API
        if not places and center_location and is_maps_available():
            geocode_result = gmaps.geocode(center_location)
            if geocode_result:
                lat = geocode_result[0]['geometry']['location']['lat']
                lng = geocode_result[0]['geometry']['location']['lng']
                map_center = [lat, lng]
                zoom_start = 12
            else:
                # Default to a view of the US if geocoding fails
                map_center = [37.0902, -95.7129]
                zoom_start = 4
        elif not places:
            # Default to a view of the US if no places and no center location
            map_center = [37.0902, -95.7129]
            zoom_start = 4
        else:
            # Center map on the first place
            lat = places[0]['geometry']['location']['lat']
            lng = places[0]['geometry']['location']['lng']
            map_center = [lat, lng]
            zoom_start = 13
        
        # Create a map
        m = folium.Map(location=map_center, zoom_start=zoom_start)
        
        # Add markers for each place
        for place in places:
            lat = place['geometry']['location']['lat']
            lng = place['geometry']['location']['lng']
            name = place.get('name', 'Unknown Place')
            rating = place.get('rating', 'No rating')
            address = place.get('vicinity', 'No address')
            
            # Create popup content
            popup_content = f"""
            <div style="width: 200px">
                <h4>{name}</h4>
                <p><strong>Rating:</strong> {rating}/5</p>
                <p><strong>Address:</strong> {address}</p>
            </div>
            """
            
            # Add marker to map
            folium.Marker(
                location=[lat, lng],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=name
            ).add_to(m)
        
        # Return the HTML representation of the map
        return m._repr_html_()
    except Exception as e:
        print(f"Error creating map: {str(e)}")
        return f"<div>Error creating map: {str(e)}</div>"

def format_place_info(place: Dict) -> str:
    """
    Format place information for display in the app.
    
    Args:
        place (Dict): Place details dictionary
        
    Returns:
        str: Formatted HTML string with place information
    """
    try:
        name = place.get('name', 'Unknown Place')
        address = place.get('formatted_address', place.get('vicinity', 'No address available'))
        rating = place.get('rating', 'No rating')
        total_ratings = place.get('user_ratings_total', 0)
        
        # Format opening hours if available
        opening_hours_html = ""
        if 'opening_hours' in place and 'weekday_text' in place['opening_hours']:
            opening_hours_html = "<h4>Opening Hours:</h4><ul>"
            for day in place['opening_hours']['weekday_text']:
                opening_hours_html += f"<li>{day}</li>"
            opening_hours_html += "</ul>"
        
        # Format reviews if available
        reviews_html = ""
        if 'reviews' in place and place['reviews']:
            reviews_html = "<h4>Top Reviews:</h4>"
            for i, review in enumerate(place['reviews'][:3]):  # Show top 3 reviews
                author = review.get('author_name', 'Anonymous')
                review_rating = review.get('rating', 'No rating')
                text = review.get('text', 'No comment')
                time = review.get('relative_time_description', '')
                
                reviews_html += f"""
                <div style="margin-bottom: 10px; padding: 8px; border-left: 3px solid #ddd;">
                    <p><strong>{author}</strong> - {review_rating}/5 ({time})</p>
                    <p>{text}</p>
                </div>
                """
        
        # Format price level if available
        price_level = ""
        if 'price_level' in place:
            price_level = "$" * place['price_level'] if place['price_level'] else "Price information not available"
        
        # Compile all information
        place_html = f"""
        <div class="place-info">
            <h3>{name}</h3>
            <p><strong>Address:</strong> {address}</p>
            <p><strong>Rating:</strong> {rating}/5 ({total_ratings} reviews)</p>
            {f"<p><strong>Price Level:</strong> {price_level}</p>" if price_level else ""}
            {f"<p><strong>Website:</strong> <a href='{place.get('website', '#')}' target='_blank'>{place.get('website', 'Not available')}</a></p>" if place.get('website') else ""}
            {f"<p><strong>Phone:</strong> {place.get('formatted_phone_number', 'Not available')}</p>" if place.get('formatted_phone_number') else ""}
            {opening_hours_html}
            {reviews_html}
        </div>
        """
        
        return place_html
    except Exception as e:
        print(f"Error formatting place info: {str(e)}")
        return f"<div>Error formatting place information: {str(e)}</div>"

def search_places_for_date_idea(location: str, date_idea_components: List[str]) -> Tuple[str, List[Dict]]:
    """
    Search for places based on date idea components and return map and place information.
    
    Args:
        location (str): Location to search around
        date_idea_components (List[str]): List of components of the date idea to search for
        
    Returns:
        Tuple[str, List[Dict]]: HTML map and list of place details
    """
    # Return a friendly message if Google Maps API is not available
    if not is_maps_available():
        no_api_message = """
        <div style="padding: 20px; text-align: center; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
            <h3 style="color: #6c757d;">Maps Feature Not Available</h3>
            <p>The Google Maps API key is not configured. Location-based recommendations are disabled.</p>
            <p>To enable this feature, please add your Google Maps API key to the .env file.</p>
        </div>
        """
        return no_api_message, []
        
    if not location or not date_idea_components:
        return "<p>Please provide a location to see map and place recommendations.</p>", []
    
    all_places = []
    
    # Search for each component
    for component in date_idea_components:
        places = search_places(location, component)
        if places:
            # Get details for top 2 places for each component
            for place in places[:2]:
                place_id = place.get('place_id')
                if place_id:
                    place_details = get_place_details(place_id)
                    if place_details:
                        all_places.append(place_details)
    
    # Create map with all places
    map_html = create_map(all_places, location)
    
    # Format place information
    place_info_html = ""
    for place in all_places:
        place_info_html += format_place_info(place)
    
    return map_html, all_places
