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
        # Test API connectivity with a simple geocode request
        test_result = gmaps.geocode("Seattle, WA")
        if test_result:
            print("Google Maps API connection successful")
        else:
            print("Google Maps API returned empty result - check permissions")
    except Exception as e:
        error_msg = str(e)
        print(f"Error initializing Google Maps client: {error_msg}")
        
        if "The provided API key is expired" in error_msg:
            print("\n===========================================================")
            print("YOUR GOOGLE MAPS API KEY HAS EXPIRED!")
            print("===========================================================")
            print("To fix this issue:")
            print("1. Visit https://console.cloud.google.com/apis/credentials")
            print("2. Find your expired key and create a new one or renew it")
            print("3. Update your .env file with the new key")
            print("4. Restart your application")
        else:
            print("\nPlease check if the following APIs are enabled in your Google Cloud Console:")
            print("- Places API")
            print("- Maps JavaScript API")
            print("- Geocoding API")
            print("- Directions API")
        
        print("\nFor more information, see: https://developers.google.com/maps/documentation/places/web-service/client-library")

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
        print(f"Maps API not available - check if Google Maps API key is set and gmaps client is initialized")
        return []
        
    try:
        # Add detailed logging
        print(f"Searching for '{query}' near '{location}' with radius {radius}m")
        
        # First, geocode the location to get coordinates
        geocode_result = gmaps.geocode(location)
        
        if not geocode_result:
            print(f"Geocoding failed for location: {location} - No results returned")
            return []
            
        # Get the latitude and longitude
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        
        print(f"Successfully geocoded {location} to coordinates: {lat}, {lng}")
        
        # Try using place search API which is more reliable
        try:
            places_result = gmaps.places(
                query=f"{query} in {location}",
                location=(lat, lng),
                radius=radius
            )
            
            results = places_result.get('results', [])
            if not results:
                # Fall back to nearby search if text search fails
                places_result = gmaps.places_nearby(
                    location=(lat, lng),
                    keyword=query,
                    radius=radius,
                    open_now=True  # Only return places that are open now
                )
                results = places_result.get('results', [])
                
            print(f"Found {len(results)} places matching '{query}' near '{location}'")
            return results
            
        except Exception as places_error:
            print(f"Error with places search: {str(places_error)}")
            
            # If Places API fails, try the older nearby search as fallback
            places_result = gmaps.places_nearby(
                location=(lat, lng),
                keyword=query,
                radius=radius
            )
            
            results = places_result.get('results', [])
            print(f"Found {len(results)} places using fallback search method")
            return results
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error searching for places: {error_msg}")
        
        # Add API-specific error handling
        if "REQUEST_DENIED" in error_msg:
            if "The provided API key is expired" in error_msg:
                print("\n===========================================================")
                print("API KEY EXPIRED! Please renew your Google Maps API key.")
                print("===========================================================")
                print("To fix this issue:")
                print("1. Visit https://console.cloud.google.com/apis/credentials")
                print("2. Find your expired key and create a new one or renew it")
                print("3. Update your .env file with the new key")
                print("4. Restart your application")
            else:
                print("\nAPI project not authorized - check if the following APIs are enabled:")
                print("- Places API")
                print("- Maps JavaScript API")
                print("- Geocoding API")
                print("Also ensure billing is set up for your Google Cloud project")
        elif "OVER_QUERY_LIMIT" in error_msg:
            print("API quota exceeded - check your usage limits in Google Cloud Console")
        elif "INVALID_REQUEST" in error_msg:
            print("Invalid request - check the parameters passed to the API")
        
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
        print("Maps API not available - cannot get place details")
        return {}
        
    try:
        print(f"Fetching details for place_id: {place_id}")
        
        place_details = gmaps.place(
            place_id=place_id,
            fields=['name', 'formatted_address', 'formatted_phone_number', 
                   'opening_hours', 'rating', 'reviews', 'website', 'price_level',
                   'geometry', 'photo', 'url', 'user_ratings_total', 
                   'current_opening_hours', 'business_status']
        )
        
        result = place_details.get('result', {})
        
        if result:
            print(f"Successfully retrieved details for {result.get('name', place_id)}")
        else:
            print(f"No details found for place_id: {place_id}")
        
        # Try to get popular times data if available
        try:
            # Note: This is a placeholder as the official API doesn't directly provide popular times
            # In a production app, you might use a third-party service or scraping (with proper permissions)
            if 'url' in result:
                result['maps_url'] = result['url']
        except Exception as e:
            print(f"Error getting popular times: {str(e)}")
        
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"Error getting place details: {error_msg}")
        
        if "REQUEST_DENIED" in error_msg:
            print("API project not authorized for Places API - check Google Cloud Console")
        
        return {}

def get_busy_status(place: Dict) -> str:
    """
    Get a human-readable busy status for a place.
    
    Args:
        place (Dict): Place details dictionary
        
    Returns:
        str: Description of how busy the place is likely to be
    """
    # This is a simplified implementation since the official API doesn't provide real-time busy data
    # In a real app, you might use historical data or third-party services
    
    if not place:
        return ""
    
    # Check if the place is currently open
    is_open = False
    if 'opening_hours' in place and 'open_now' in place['opening_hours']:
        is_open = place['opening_hours']['open_now']
    
    if not is_open:
        return "Currently closed"
    
    # Get current day and hour
    now = datetime.now()
    day_of_week = now.weekday()  # 0 = Monday, 6 = Sunday
    hour = now.hour
    
    # Simple heuristic for busy times (this is a placeholder)
    busy_times = {
        # Weekdays
        0: [12, 13, 17, 18, 19],  # Monday lunch and dinner
        1: [12, 13, 17, 18, 19],  # Tuesday lunch and dinner
        2: [12, 13, 17, 18, 19],  # Wednesday lunch and dinner
        3: [12, 13, 17, 18, 19],  # Thursday lunch and dinner
        4: [12, 13, 17, 18, 19, 20],  # Friday lunch and dinner + evening
        # Weekend
        5: [10, 11, 12, 13, 14, 18, 19, 20],  # Saturday brunch, lunch, dinner
        6: [10, 11, 12, 13, 14, 17, 18]  # Sunday brunch, lunch, early dinner
    }
    
    # Check rating and popularity
    rating = place.get('rating', 0)
    total_ratings = place.get('user_ratings_total', 0)
    
    if hour in busy_times.get(day_of_week, []):
        if rating > 4.5 and total_ratings > 100:
            return "Likely very busy right now"
        elif rating > 4.0:
            return "Might be busy right now"
        else:
            return "Moderately busy right now"
    else:
        return "Likely not too busy right now"

def create_map(places: List[Dict], center_location: str = None) -> Tuple[str, List[Dict], str]:
    """
    Create an interactive map with markers for the given places.
    
    Args:
        places (List[Dict]): List of place dictionaries with location information
        center_location (str, optional): Location to center the map on
        
    Returns:
        Tuple[str, List[Dict], str]: HTML map, filtered places list, and HTML table of place information
    """
    try:
        # If no Google Maps API or no places, return simple message with default map
        if not is_maps_available() or (not places and not center_location):
            print("No maps API or places - creating default empty map view")
            # Default to a view of the US
            map_center = [37.0902, -95.7129]
            zoom_start = 4
            m = folium.Map(location=map_center, zoom_start=zoom_start)
            map_html = m._repr_html_()
            # Ensure the map is full width and height
            map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
            map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
            return map_html, [], ""
            
        # If no places but we have a center location and maps API
        if not places and center_location and is_maps_available():
            print(f"No places provided, but have center location: {center_location}")
            try:
                geocode_result = gmaps.geocode(center_location)
                if geocode_result:
                    lat = geocode_result[0]['geometry']['location']['lat']
                    lng = geocode_result[0]['geometry']['location']['lng']
                    map_center = [lat, lng]
                    zoom_start = 12
                    
                    m = folium.Map(location=map_center, zoom_start=zoom_start)
                    
                    # Add a marker for the center location
                    folium.Marker(
                        location=map_center,
                        popup=center_location,
                        tooltip=center_location
                    ).add_to(m)
                    
                    map_html = m._repr_html_()
                    # Ensure the map is full width and height
                    map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
                    map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
                    return map_html, [], ""
                else:
                    print(f"Geocoding failed for center location: {center_location}")
                    map_center = [37.0902, -95.7129]
                    zoom_start = 4
                    m = folium.Map(location=map_center, zoom_start=zoom_start)
                    map_html = m._repr_html_()
                    # Ensure the map is full width and height
                    map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
                    map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
                    return map_html, [], ""
            except Exception as e:
                print(f"Error geocoding center location: {str(e)}")
                map_center = [37.0902, -95.7129]
                zoom_start = 4
                m = folium.Map(location=map_center, zoom_start=zoom_start)
                map_html = m._repr_html_()
                # Ensure the map is full width and height
                map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
                map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
                return map_html, [], ""
        elif not places:
            # Default to a view of the US if no places and no center location
            print("No places or center location provided - creating default map")
            map_center = [37.0902, -95.7129]
            zoom_start = 4
            m = folium.Map(location=map_center, zoom_start=zoom_start)
            map_html = m._repr_html_()
            # Ensure the map is full width and height
            map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
            map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
            return map_html, [], ""
            
        # Filter out places with missing geometry or location data
        valid_places = []
        for place in places:
            if 'geometry' in place and 'location' in place['geometry']:
                if 'lat' in place['geometry']['location'] and 'lng' in place['geometry']['location']:
                    valid_places.append(place)
                else:
                    print(f"Skipping place {place.get('name', 'unknown')} - missing lat/lng in location")
            else:
                print(f"Skipping place {place.get('name', 'unknown')} - missing geometry or location")
        
        if not valid_places:
            print("No valid places with location data found")
            map_center = [37.0902, -95.7129]
            zoom_start = 4
            m = folium.Map(location=map_center, zoom_start=zoom_start)
            map_html = m._repr_html_()
            # Ensure the map is full width and height
            map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
            map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
            return map_html, [], ""
        
        # Center map on the first valid place
        lat = valid_places[0]['geometry']['location']['lat']
        lng = valid_places[0]['geometry']['location']['lng']
        map_center = [lat, lng]
        zoom_start = 13
        
        # Create a map
        m = folium.Map(location=map_center, zoom_start=zoom_start)
        
        # Create place info table HTML
        table_html = """
        <div class="place-table">
            <h3>Places Details</h3>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Address</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add markers for each place
        for place in valid_places:
            try:
                lat = place['geometry']['location']['lat']
                lng = place['geometry']['location']['lng']
                name = place.get('name', 'Unknown Place')
                rating = place.get('rating', 'No rating')
                address = place.get('vicinity', place.get('formatted_address', 'No address'))
                
                # Get Google Maps URL
                maps_url = place.get('url', place.get('maps_url', '#'))
                
                # Get busy status
                busy_status = get_busy_status(place)
                
                # Create popup content with link to Google Maps
                popup_content = f"""
                <div style="width: 220px">
                    <h4>{name}</h4>
                    <p><strong>Rating:</strong> {rating}/5</p>
                    <p><strong>Address:</strong> {address}</p>
                    {f"<p><strong>Status:</strong> {busy_status}</p>" if busy_status else ""}
                    <p><a href="{maps_url}" target="_blank" style="color: #4285F4; font-weight: bold;">View on Google Maps</a></p>
                </div>
                """
                
                # Add marker to map
                folium.Marker(
                    location=[lat, lng],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=name
                ).add_to(m)
                
                # Add to table HTML
                table_html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{address}</td>
                    <td>{rating}/5</td>
                </tr>
                """
            except Exception as e:
                print(f"Error adding marker for place {place.get('name', 'unknown')}: {str(e)}")
        
        # Complete table HTML
        table_html += """
                </tbody>
            </table>
        </div>
        """
        
        # Return the HTML representation of the map
        map_html = m._repr_html_()
        # Ensure the map is full width and height
        map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
        map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
        return map_html, valid_places, table_html
    except Exception as e:
        print(f"Error creating map: {str(e)}")
        map_center = [37.0902, -95.7129]
        zoom_start = 4
        m = folium.Map(location=map_center, zoom_start=zoom_start)
        map_html = m._repr_html_()
        # Ensure the map is full width and height
        map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
        map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
        return map_html, [], f"<div>Error creating map: {str(e)}</div>"

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
        
        # Get Google Maps URL
        maps_url = place.get('url', place.get('maps_url', '#'))
        
        # Get busy status
        busy_status = get_busy_status(place)
        
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
            {f"<p><strong>Busy Status:</strong> <span style='color: {'#d9534f' if 'busy' in busy_status.lower() else '#5cb85c'};'>{busy_status}</span></p>" if busy_status else ""}
            {f"<p><strong>Website:</strong> <a href='{place.get('website', '#')}' target='_blank'>{place.get('website', 'Not available')}</a></p>" if place.get('website') else ""}
            {f"<p><strong>Phone:</strong> {place.get('formatted_phone_number', 'Not available')}</p>" if place.get('formatted_phone_number') else ""}
            <p><strong>View on Google Maps:</strong> <a href='{maps_url}' target='_blank'>Open in Google Maps</a></p>
            {opening_hours_html}
            {reviews_html}
        </div>
        """
        
        return place_html
    except Exception as e:
        print(f"Error formatting place info: {str(e)}")
        return f"<div>Error formatting place information: {str(e)}</div>"

def search_places_for_date_idea(location: str, date_idea_components: List[str]) -> Tuple[str, List[Dict], str]:
    """
    Search for places based on date idea components and return map and place information.
    
    Args:
        location (str): Location to search around
        date_idea_components (List[str]): List of components of the date idea to search for
        
    Returns:
        Tuple[str, List[Dict], str]: HTML map, list of place details, and formatted place info HTML
    """
    # Return a friendly message if Google Maps API is not available
    if not is_maps_available():
        print("Maps API not available - returning error message to user interface")
        # Create a default map even if API is not available
        map_center = [37.0902, -95.7129]  # Default US center
        zoom_start = 4
        m = folium.Map(location=map_center, zoom_start=zoom_start)
        map_html = m._repr_html_()
        # Ensure the map is full width and height
        map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
        map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
        
        no_api_message = """
        <div style="padding: 20px; text-align: center; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
            <h3 style="color: #6c757d;">Maps Feature Not Available</h3>
            <p>The Google Maps API key is not configured or services are not enabled.</p>
            <p>To enable this feature, please check:</p>
            <ol style="text-align: left; display: inline-block;">
                <li>Your Google Maps API key is in the .env file</li>
                <li>The following APIs are enabled in Google Cloud Console:
                    <ul>
                        <li>Places API</li>
                        <li>Maps JavaScript API</li>
                        <li>Geocoding API</li>
                    </ul>
                </li>
                <li>Billing is set up for your Google Cloud project</li>
            </ol>
        </div>
        """
        return map_html, [], no_api_message
        
    if not location or not date_idea_components:
        print("Missing location or date idea components - cannot search for places")
        # Create a default map even if location is missing
        map_center = [37.0902, -95.7129]  # Default US center
        zoom_start = 4
        m = folium.Map(location=map_center, zoom_start=zoom_start)
        map_html = m._repr_html_()
        # Ensure the map is full width and height
        map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
        map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
        return map_html, [], "<p>Please provide a location to see map and place recommendations.</p>"
    
    all_places = []
    search_errors = False
    
    print(f"Searching for {len(date_idea_components)} components in {location}")
    
    # Search for each component
    for component in date_idea_components:
        try:
            # Clean up the component to improve search results
            cleaned_component = component.split('-')[0].strip() if '-' in component else component.strip()
            # Remove any parentheses content
            cleaned_component = cleaned_component.split('(')[0].strip()
            
            print(f"Searching for component: '{cleaned_component}'")
            places = search_places(location, cleaned_component)
            
            if places:
                # Get details for top 2 places for each component
                for place in places[:2]:
                    place_id = place.get('place_id')
                    if place_id:
                        place_details = get_place_details(place_id)
                        if place_details:
                            all_places.append(place_details)
            else:
                print(f"No places found for component: '{cleaned_component}'")
        except Exception as e:
            print(f"Error searching for component '{component}': {str(e)}")
            search_errors = True
    
    # Create fallback content if we have errors but some results
    if search_errors and all_places:
        print("Some search errors occurred, but found partial results")
    
    # If no places found, provide a default message with information about using external maps
    if not all_places:
        no_results_message = """
        <div style="padding: 20px; text-align: center; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
            <h3 style="color: #6c757d;">No Places Found</h3>
            <p>We couldn't find specific places for your date idea components in {0}.</p>
            <p>Try searching for these locations directly in <a href="https://www.google.com/maps/search/{1}" target="_blank">Google Maps</a>.</p>
        </div>
        """.format(location, "+".join(date_idea_components).replace(" ", "+"))
        
        # Create a static map showing the general location
        try:
            # Generate a simple static map centered on the location
            map_center = None
            geocode_result = gmaps.geocode(location) if is_maps_available() else None
            if geocode_result:
                lat = geocode_result[0]['geometry']['location']['lat']
                lng = geocode_result[0]['geometry']['location']['lng']
                map_center = [lat, lng]
                
                # Create a simple map centered on the location
                m = folium.Map(location=map_center, zoom_start=13)
                folium.Marker(
                    location=map_center,
                    popup=location,
                    tooltip=location
                ).add_to(m)
                
                map_html = m._repr_html_()
                # Ensure the map is full width and height
                map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
                map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
                return map_html, [], no_results_message
            else:
                # Default map if geocoding fails
                map_center = [37.0902, -95.7129]
                zoom_start = 4
                m = folium.Map(location=map_center, zoom_start=zoom_start)
                map_html = m._repr_html_()
                # Ensure the map is full width and height
                map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
                map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
                return map_html, [], no_results_message
        except Exception as e:
            print(f"Error creating fallback map: {str(e)}")
            # Default map if any error occurs
            map_center = [37.0902, -95.7129]
            zoom_start = 4
            m = folium.Map(location=map_center, zoom_start=zoom_start)
            map_html = m._repr_html_()
            # Ensure the map is full width and height
            map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
            map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
            return map_html, [], no_results_message
    
    print(f"Found {len(all_places)} place details - creating map")
    
    # Create map with all places
    filtered_places = []
    try:
        map_html, filtered_places, table_html = create_map(all_places, location)
    except Exception as e:
        print(f"Error creating map with places: {str(e)}")
        # Create fallback map
        map_center = [37.0902, -95.7129]
        zoom_start = 4
        m = folium.Map(location=map_center, zoom_start=zoom_start)
        map_html = m._repr_html_()
        # Ensure the map is full width and height
        map_html = map_html.replace('width: 100%;', 'width: 100% !important;')
        map_html = map_html.replace('height: 100.0%;', 'height: 400px !important;')
        
        fallback_html = """
        <div style="padding: 20px; text-align: center; background-color: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6;">
            <h3 style="color: #6c757d;">Map Creation Error</h3>
            <p>We found places but couldn't create an interactive map.</p>
            <p>Details are still available below.</p>
        </div>
        """
        filtered_places = all_places
    
    # Format place information
    place_info_html = ""
    for place in filtered_places:
        try:
            place_info_html += format_place_info(place)
        except Exception as e:
            print(f"Error formatting place info for {place.get('name', 'unknown place')}: {str(e)}")
            # Add basic info as fallback
            place_info_html += f"""
            <div class="place-info">
                <h3>{place.get('name', 'Unknown Place')}</h3>
                <p><strong>Address:</strong> {place.get('formatted_address', place.get('vicinity', 'Address not available'))}</p>
                <p><a href="{place.get('url', '#')}" target="_blank">View on Google Maps</a></p>
            </div>
            """
    
    return map_html, filtered_places, place_info_html