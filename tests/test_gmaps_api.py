#!/usr/bin/env python3
"""
Google Maps API Test Script

This script tests the connectivity to various Google Maps APIs
to verify that your API key is properly configured and the
necessary services are enabled.
"""

import os
import sys
from dotenv import load_dotenv
import googlemaps
from datetime import datetime

# Load environment variables
load_dotenv()

# Get API key from environment or command line
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY and len(sys.argv) > 1:
    API_KEY = sys.argv[1]

if not API_KEY:
    print("Error: No Google Maps API key found.")
    print("Please provide it as an environment variable GOOGLE_MAPS_API_KEY or as a command-line argument.")
    sys.exit(1)

print(f"Using Google Maps API Key: {API_KEY[:5]}...{API_KEY[-5:]}")

# Initialize the client
try:
    gmaps = googlemaps.Client(key=API_KEY)
    print("✅ Successfully initialized Google Maps client")
except Exception as e:
    error_msg = str(e)
    print(f"❌ Error initializing Google Maps client: {error_msg}")
    
    if "The provided API key is expired" in error_msg:
        print("\n===========================================================")
        print("YOUR API KEY HAS EXPIRED!")
        print("===========================================================")
        print("To fix this issue:")
        print("1. Visit https://console.cloud.google.com/apis/credentials")
        print("2. Find your expired key and create a new one or renew it")
        print("3. Update your .env file with the new key")
        print("4. Restart your application")
        print("\nFor more information, see: https://developers.google.com/maps/documentation/places/web-service/client-library")
    
    sys.exit(1)

# Test each API and track results
test_results = {
    "Geocoding": False,
    "Places": False,
    "Place Details": False,
    "Directions": False
}

# Test Geocoding API
print("\nTesting Geocoding API...")
try:
    geocode_result = gmaps.geocode("1600 Amphitheatre Parkway, Mountain View, CA")
    if geocode_result:
        print(f"✅ Geocoding API working")
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        print(f"   Address geocoded to: {lat}, {lng}")
        test_results["Geocoding"] = True
    else:
        print("❌ Geocoding API returned empty results")
except Exception as e:
    error_msg = str(e)
    print(f"❌ Geocoding API error: {error_msg}")
    if "The provided API key is expired" in error_msg:
        print("   YOUR API KEY HAS EXPIRED!")
    elif "REQUEST_DENIED" in error_msg:
        print("   This API needs to be enabled in your Google Cloud Console.")

# Test Places API (both methods)
print("\nTesting Places API (text search)...")
try:
    text_search_result = gmaps.places(
        query="restaurants near Google HQ",
    )
    if 'results' in text_search_result and text_search_result['results']:
        print(f"✅ Places API (text search) working")
        print(f"   Found {len(text_search_result['results'])} places")
        test_results["Places"] = True
    else:
        print("❌ Places API (text search) returned empty results")
        
        # Try nearby search as fallback
        print("\nTesting Places API (nearby search)...")
        nearby_search_result = gmaps.places_nearby(
            location=(37.4224428, -122.0842467),  # Google HQ
            keyword="restaurant",
            radius=1000
        )
        if 'results' in nearby_search_result and nearby_search_result['results']:
            print(f"✅ Places API (nearby search) working")
            print(f"   Found {len(nearby_search_result['results'])} places nearby")
            test_results["Places"] = True
        else:
            print("❌ Places API (nearby search) returned empty results")
except Exception as e:
    error_msg = str(e)
    print(f"❌ Places API error: {error_msg}")
    if "The provided API key is expired" in error_msg:
        print("   YOUR API KEY HAS EXPIRED!")
    elif "REQUEST_DENIED" in error_msg:
        print("   This API needs to be enabled in your Google Cloud Console.")

# Test Place Details API
print("\nTesting Place Details API...")
try:
    place_id = "ChIJj61dQgK6j4AR4GeTYWZsKWw"  # Google HQ
    place_result = gmaps.place(
        place_id=place_id,
        fields=['name', 'formatted_address', 'geometry']
    )
    if 'result' in place_result and place_result['result']:
        print(f"✅ Place Details API working")
        print(f"   Place name: {place_result['result'].get('name')}")
        test_results["Place Details"] = True
    else:
        print("❌ Place Details API returned empty results")
except Exception as e:
    error_msg = str(e)
    print(f"❌ Place Details API error: {error_msg}")
    if "The provided API key is expired" in error_msg:
        print("   YOUR API KEY HAS EXPIRED!")
    elif "REQUEST_DENIED" in error_msg:
        print("   This API needs to be enabled in your Google Cloud Console.")

# Test Directions API
print("\nTesting Directions API...")
try:
    directions_result = gmaps.directions(
        origin="1600 Amphitheatre Parkway, Mountain View, CA",
        destination="1 Infinite Loop, Cupertino, CA",
        mode="driving",
        departure_time=datetime.now()
    )
    if directions_result:
        print(f"✅ Directions API working")
        legs = directions_result[0]['legs'][0]
        print(f"   Distance: {legs['distance']['text']}, Duration: {legs['duration']['text']}")
        test_results["Directions"] = True
    else:
        print("❌ Directions API returned empty results")
except Exception as e:
    error_msg = str(e)
    print(f"❌ Directions API error: {error_msg}")
    if "The provided API key is expired" in error_msg:
        print("   YOUR API KEY HAS EXPIRED!")
    elif "REQUEST_DENIED" in error_msg:
        print("   This API needs to be enabled in your Google Cloud Console.")

# Print summary
print("\n===========================================================")
print("API TEST SUMMARY")
print("===========================================================")

for api, passed in test_results.items():
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"{api} API: {status}")

if not any(test_results.values()):
    print("\n❌ ALL TESTS FAILED")
    print("The most likely issue is that your API key has expired or doesn't have the necessary permissions.")
    print("\nTo fix an expired API key:")
    print("1. Visit https://console.cloud.google.com/apis/credentials")
    print("2. Find your expired key and create a new one or renew it")
    print("3. Update your .env file with the new key")
    print("4. Restart your application")
else:
    if all(test_results.values()):
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("For any APIs that failed, check the following:")

    print("\nIf you're still having issues, check:")
    print("1. Enable all necessary APIs in Google Cloud Console:")
    print("   - Go to https://console.cloud.google.com/apis/dashboard")
    print("   - Select your project")
    print("   - Click '+ ENABLE APIS AND SERVICES'")
    print("   - Search for and enable: ")
    print("     - Geocoding API")
    print("     - Places API")
    print("     - Maps JavaScript API")
    print("     - Directions API")
    print("\n2. Ensure billing is enabled for your project (required even for free tier)")
    print("\n3. Other potential issues:")
    print("   - Domain/IP restrictions on your API key")
    print("   - Billing status of your Google Cloud project")
    print("   - API quotas and usage limits") 