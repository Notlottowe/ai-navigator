"""
Configuration module for AI Navigator application.
Handles API keys, URLs, and application settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Override parameter ensures .env file takes precedence
load_dotenv(override=True)

# --- API Configuration ---
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Check if keys exist for UI logic
KEYS_PRESENT = (MAPBOX_ACCESS_TOKEN != "" and GEMINI_API_KEY != "")

# --- API URLs ---
MAPBOX_DIRECTIONS_URL = "https://api.mapbox.com/directions/v5/mapbox/driving-traffic"
MAPBOX_GEOCODING_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# --- Application Settings ---
DEFAULT_LAT = 39.82
DEFAULT_LON = -98.57
WEATHER_SAMPLE_POINTS = 30
MAX_ALERTS = 5
FORECAST_DAYS_LIMIT = 14
REQUEST_TIMEOUT = 10

