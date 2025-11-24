"""
Utility functions for weather processing, date handling, and data formatting.
"""
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any
from config import WEATHER_SAMPLE_POINTS, MAX_ALERTS, FORECAST_DAYS_LIMIT
from api_client import reverse_geocode, get_route_weather_data


def format_duration(minutes: float) -> str:
    """
    Format duration in minutes to a human-readable string.
    
    Examples:
        45 -> "45 min"
        90 -> "1 hr 30 min"
        120 -> "2 hr"
        1440 -> "1 day"
        1500 -> "1 day 1 hr"
        1530 -> "1 day 1 hr 30 min"
    
    Args:
        minutes: Duration in minutes (can be float)
        
    Returns:
        Formatted duration string
    """
    total_minutes = int(round(minutes))
    
    if total_minutes < 60:
        return f"{total_minutes} min"
    
    days = total_minutes // 1440
    hours = (total_minutes % 1440) // 60
    mins = total_minutes % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hr")  # Always use "hr" (singular form)
    # Show minutes if there are remaining minutes
    if mins > 0:
        parts.append(f"{mins} min")
    
    return " ".join(parts) if parts else "0 min"


def get_weather_severity(wmo_code: int) -> Tuple[str, List[int], str]:
    """
    Map WMO weather codes to severity, color, and description.
    
    Args:
        wmo_code: WMO weather code
        
    Returns:
        Tuple of (severity, [r, g, b] color, description)
    """
    if wmo_code <= 3:
        return "Low", [0, 100, 255], "Clear/Cloudy"
    elif wmo_code <= 48:
        return "Medium", [255, 215, 0], "Fog"
    elif wmo_code <= 55:
        return "Medium", [255, 165, 0], "Drizzle"
    elif wmo_code <= 67:
        return "High", [255, 69, 0], "Rain"
    elif wmo_code <= 77:
        return "Severe", [200, 200, 255], "Snow"
    elif wmo_code <= 82:
        return "High", [255, 140, 0], "Showers"
    else:
        return "Severe", [255, 0, 0], "Thunderstorm"


def get_next_day_weather(lat: float, lon: float, arrival_dt: datetime, mapbox_key: str) -> str:
    """
    Get weather forecast for the day after arrival.
    
    Args:
        lat: Latitude
        lon: Longitude
        arrival_dt: Arrival datetime
        mapbox_key: Mapbox access token (for error handling context)
        
    Returns:
        Formatted weather forecast string
    """
    if not arrival_dt:
        return "Data unavailable (No date)"
    
    # Check date range (Open-Meteo limit ~14 days)
    delta = (arrival_dt.date() - datetime.now().date()).days
    if delta > FORECAST_DAYS_LIMIT:
        return f"Forecast unavailable (>14 days)"
    if delta < -1:
        return f"Data unavailable (Past date)"
    
    next_day = arrival_dt + timedelta(days=1)
    date_str = next_day.strftime("%Y-%m-%d")
    
    from api_client import get_weather_forecast
    data = get_weather_forecast(lat, lon, date_str)
    
    if not data:
        return "Weather Service Unavailable"
    
    if "daily" in data and data["daily"]["weathercode"]:
        code = data["daily"]["weathercode"][0]
        t_max = data["daily"]["temperature_2m_max"][0]
        t_min = data["daily"]["temperature_2m_min"][0]
        _, _, desc = get_weather_severity(code)
        return f"{date_str}: {desc}, High {t_max}°C / Low {t_min}°C"
    else:
        return "Data unavailable for this location."


def process_route_and_weather(
    route_data: Dict[str, Any],
    departure_dt: datetime,
    mapbox_key: str
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Process route geometry and get weather data for segments.
    
    Args:
        route_data: Route data from Mapbox Directions API
        departure_dt: Departure datetime
        mapbox_key: Mapbox access token for reverse geocoding
        
    Returns:
        Tuple of (segments list, alerts list)
    """
    geometry = route_data.get('geometry', {}).get('coordinates', [])
    if not geometry:
        return [], []
    
    total_points = len(geometry)
    total_dur = route_data.get('duration', 0)
    
    # Sample points along the route
    num_samples = WEATHER_SAMPLE_POINTS
    step = max(1, total_points // num_samples)
    sample_indices = list(range(0, total_points, step))
    
    # Extract coordinates for sampled points
    lat_list, lon_list = [], []
    for i in sample_indices:
        lon, lat = geometry[i]
        lat_list.append(lat)
        lon_list.append(lon)
    
    # Get weather data for all sampled points
    weather_results = get_route_weather_data(lat_list, lon_list)
    
    segments = []
    detailed_alerts = []
    
    try:
        for k in range(len(sample_indices) - 1):
            start_idx = sample_indices[k]
            end_idx = sample_indices[k + 1] if k + 1 < len(sample_indices) else total_points - 1
            segment_path = geometry[start_idx: end_idx + 1]
            
            # Estimate arrival time at this segment
            progress = start_idx / total_points if total_points > 0 else 0
            seconds_from_dep = progress * total_dur
            arrival_time = departure_dt + timedelta(seconds=seconds_from_dep)
            
            # Get weather for this point
            if k < len(weather_results):
                w_loc = weather_results[k]
                forecast_times = w_loc.get('hourly', {}).get('time', [])
                target_iso_hour = arrival_time.strftime("%Y-%m-%dT%H:00")
                
                severity, color, desc = "Low", [0, 100, 255], "Clear"
                temp = "N/A"
                match_idx = -1
                
                # Find matching forecast time
                for idx, t_str in enumerate(forecast_times):
                    if t_str.startswith(target_iso_hour):
                        match_idx = idx
                        break
                
                if match_idx != -1:
                    code = w_loc['hourly']['weathercode'][match_idx]
                    temp = w_loc['hourly']['temperature_2m'][match_idx]
                    severity, color, desc = get_weather_severity(code)
                    
                    # Create alert for severe weather
                    if severity in ["High", "Severe"] and len(detailed_alerts) < MAX_ALERTS:
                        loc_lat, loc_lon = lat_list[k], lon_list[k]
                        loc_name = reverse_geocode(loc_lat, loc_lon, mapbox_key)
                        
                        detailed_alerts.append({
                            "severity": severity,
                            "desc": desc,
                            "time": arrival_time.strftime("%b %d - %I:%M %p"),
                            "temp": temp,
                            "location": loc_name
                        })
                
                lighter_color = [int(c + (255 - c) * 0.4) for c in color]
                segments.append({
                    "path": segment_path,
                    "color": color,
                    "outline_color": lighter_color,
                    "tooltip": f"{desc}, {temp}°C"
                })
            else:
                # Fallback if weather data unavailable
                segments.append({
                    "path": segment_path,
                    "color": [0, 100, 255],
                    "outline_color": [150, 200, 255],
                    "tooltip": "Weather Data Unavailable"
                })
    
    except Exception as e:
        print(f"Error processing route weather: {e}")
        # Return fallback segment
        segments = [{
            "path": geometry,
            "color": [0, 100, 255],
            "outline_color": [150, 200, 255],
            "tooltip": "Weather Data Unavailable"
        }]
    
    return segments, detailed_alerts

