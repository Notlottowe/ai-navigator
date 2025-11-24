"""
API Client module for external API calls.
Handles Mapbox, Open-Meteo, and Gemini API interactions.
"""
import requests
import json
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any
from config import (
    MAPBOX_ACCESS_TOKEN,
    MAPBOX_DIRECTIONS_URL,
    MAPBOX_GEOCODING_URL,
    OPEN_METEO_URL,
    GEMINI_API_URL,
    GEMINI_API_KEY,
    REQUEST_TIMEOUT
)


def geocode_location(query: str, access_token: str) -> Tuple[Optional[List[float]], Optional[str], Optional[str]]:
    """
    Geocode a location query to coordinates.
    
    Args:
        query: Location string to geocode
        access_token: Mapbox access token
        
    Returns:
        Tuple of (coordinates [lon, lat], place_name, country_code) or (None, None, None) on error
    """
    if not query:
        return None, None, None
    
    encoded_query = urllib.parse.quote(query)
    url = f"{MAPBOX_GEOCODING_URL}/{encoded_query}.json"
    params = {"access_token": access_token, "limit": 1}
    
    try:
        r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        
        if data.get("features"):
            feat = data["features"][0]
            
            # Extract country code
            country_code = "US"  # Default
            if "context" in feat:
                for item in feat["context"]:
                    if item.get("id", "").startswith("country"):
                        country_code = item.get("short_code", "us").upper()
                        break
            
            return feat["center"], feat["place_name"], country_code
    except Exception as e:
        print(f"Geocoding Error: {e}")
        pass
    
    return None, None, None


def reverse_geocode(lat: float, lon: float, access_token: str) -> str:
    """
    Reverse geocode coordinates to a place name.
    
    Args:
        lat: Latitude
        lon: Longitude
        access_token: Mapbox access token
        
    Returns:
        Place name string or coordinates as fallback
    """
    url = f"{MAPBOX_GEOCODING_URL}/{lon},{lat}.json"
    params = {"access_token": access_token, "limit": 1, "types": "place,locality"}
    
    try:
        r = requests.get(url, params=params, timeout=2)
        r.raise_for_status()
        data = r.json()
        if data.get("features"):
            return data["features"][0]["place_name"]
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        pass
    
    return f"{lat:.2f}, {lon:.2f}"


def get_user_location_ip() -> Optional[Tuple[float, float, str, str]]:
    """
    Get user's location based on IP address.
    
    Returns:
        Tuple of (lat, lon, location_string, country_code) or None on error
    """
    try:
        r = requests.get("http://ip-api.com/json/", timeout=3)
        r.raise_for_status()
        d = r.json()
        if d.get('status') == 'success':
            return d['lat'], d['lon'], f"{d['city']}, {d['regionName']}", d.get('countryCode', 'US')
    except Exception as e:
        print(f"IP geolocation error: {e}")
        return None
    
    return None


def get_directions(start_coords: List[float], end_coords: List[float], access_token: str) -> Dict[str, Any]:
    """
    Get driving directions between two coordinates.
    
    Args:
        start_coords: [lon, lat] of start point
        end_coords: [lon, lat] of end point
        access_token: Mapbox access token
        
    Returns:
        Directions API response as dictionary
    """
    coords = f"{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
    url = f"{MAPBOX_DIRECTIONS_URL}/{coords}"
    params = {
        "access_token": access_token,
        "geometries": "geojson",
        "overview": "full",
        "annotations": "duration,distance,congestion"
    }
    
    try:
        r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Directions API error: {e}")
        return {}


def get_weather_forecast(lat: float, lon: float, date_str: str) -> Optional[Dict[str, Any]]:
    """
    Get weather forecast for a specific date and location.
    
    Args:
        lat: Latitude
        lon: Longitude
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Weather data dictionary or None on error
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "start_date": date_str,
        "end_date": date_str
    }
    
    try:
        r = requests.get(OPEN_METEO_URL, params=params, timeout=8)
        r.raise_for_status()
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Weather forecast error: {e}")
        return None
    
    return None


def get_route_weather_data(lat_list: List[float], lon_list: List[float]) -> List[Dict[str, Any]]:
    """
    Get weather data for multiple coordinates along a route.
    
    Args:
        lat_list: List of latitudes
        lon_list: List of longitudes
        
    Returns:
        List of weather data dictionaries
    """
    params = {
        "latitude": ",".join(map(str, lat_list)),
        "longitude": ",".join(map(str, lon_list)),
        "hourly": "weathercode,temperature_2m",
        "forecast_days": 10,
        "timezone": "UTC"
    }
    
    try:
        r = requests.get(OPEN_METEO_URL, params=params, timeout=5)
        r.raise_for_status()
        w_data = r.json()
        return [w_data] if isinstance(w_data, dict) else w_data
    except Exception as e:
        print(f"Route weather data error: {e}")
        return []


def parse_trip_with_gemini(user_text: str, google_key: str) -> Optional[Dict[str, Any]]:
    """
    Parse trip details from user text using Gemini API.
    
    Args:
        user_text: User's natural language trip description
        google_key: Gemini API key
        
    Returns:
        Parsed trip details dictionary or None on error
    """
    current_time = datetime.now().isoformat()
    system_prompt = f"""
    You are a navigation assistant. Extract trip details from the user's input.
    Current Date/Time: {current_time}
    Output Format: JSON object ONLY.
    Keys:
    - "origin": The starting location (string). If not specified, return null.
    - "destination": The destination (string). Required.
    - "departure_time": The specific departure time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
      - If user says "Sunday", find the next upcoming Sunday relative to {current_time}.
      - If no time is specified, use the Current Date/Time exactly.
    """
    
    payload = {
        "contents": [{"parts": [{"text": user_text}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    try:
        url = f"{GEMINI_API_URL}?key={google_key}"
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        
        if "candidates" in result:
            raw_json = result["candidates"][0]["content"]["parts"][0]["text"]
            # Clean up potential markdown fences
            raw_json = raw_json.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_json)
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None
    
    return None

