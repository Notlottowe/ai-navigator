"""
AI Navigator - Main Application
A Streamlit app for intelligent route planning with weather alerts.
"""
import streamlit as st
import pydeck as pdk
import numpy as np
import time
from datetime import datetime, timedelta
import dateutil.parser

# Local imports
from config import (
    MAPBOX_ACCESS_TOKEN,
    GEMINI_API_KEY,
    KEYS_PRESENT,
    DEFAULT_LAT,
    DEFAULT_LON
)
from api_client import (
    geocode_location,
    get_user_location_ip,
    get_directions,
    parse_trip_with_gemini
)
from utils import (
    get_next_day_weather,
    process_route_and_weather,
    format_duration
)
from styles import CUSTOM_CSS

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Navigator",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Session State Initialization ---
if 'app_state' not in st.session_state:
    st.session_state['app_state'] = {
        'user_lat': DEFAULT_LAT,
        'user_lon': DEFAULT_LON,
        'segments': [],
        'alerts': [],
        'trip_meta': None,
        'origin_name': "Unknown",
        'dest_name': "Unknown",
        'dest_coords': None,
        'full_route_geo': [],
        'next_day_forecast': None,
        'trip_date_str': None,
        'departure_dt': None
    }

if 'is_processing' not in st.session_state:
    st.session_state['is_processing'] = False


def update_status(status_ph, text: str, color: str = "rgba(255,255,255,0.1)", animate: bool = False, error_style: bool = False, fade_out_delay: float = 1.6):
    """
    Update status message display.
    
    Args:
        status_ph: Streamlit placeholder for status
        text: Status text to display
        color: Background color (or text color for error style)
        animate: Whether to apply pulse animation
        error_style: If True, use white outline with transparent background
        fade_out_delay: Delay before fade out starts (in seconds, for error messages)
    """
    anim_class = "analyzing-pulse" if animate else ""
    
    if error_style:
        # Error style: white outline, transparent background, white text with fade in/out
        # Size matches normal style for consistency
        fade_class = "error-pill-fadein"
        # Calculate fade out delay in CSS (delay before fade out animation starts)
        fade_out_css = f"{fade_out_delay}s"
        style = f"""
            background-color: transparent;
            color: white;
            border: 2px solid rgba(255,255,255,0.8);
            padding: 8px 25px;
            border-radius: 30px;
            font-size: 0.9rem;
            font-weight: 500;
            letter-spacing: 0.5px;
            box-shadow: 0 0 20px rgba(255,255,255,0.2), 0 4px 15px rgba(0,0,0,0.3);
            cursor: default;
            display: inline-block;
            opacity: 0;
            animation: fadeIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards,
                       fadeOut 0.4s cubic-bezier(0.55, 0.055, 0.675, 0.19) {fade_out_css} forwards;
        """
    else:
        fade_class = ""
        # Normal style: colored background
        style = f"""
            background-color: {color};
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
            padding: 8px 25px;
            border-radius: 30px;
            font-size: 0.9rem;
            font-weight: 500;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            cursor: default;
            display: inline-block;
        """
    
    status_ph.markdown(f"""
        <div style="text-align: center; margin-top: 20px;">
            <span class="{anim_class} {fade_class}" style="{style}">
                {text}
            </span>
        </div>
    """, unsafe_allow_html=True)


def _process_query(query: str):
    """
    Internal function to process the query and generate route.
    
    Args:
        query: User's natural language trip query
    """
    error_ph = st.empty()
    trip_details = parse_trip_with_gemini(query, GEMINI_API_KEY)
    if not trip_details:
        st.session_state['is_processing'] = False
        update_status(error_ph, "AI FAILED", "#ff4b4b", error_style=True, fade_out_delay=1.6)
        time.sleep(2)
        return

    origin_str = trip_details.get("origin")
    dest_str = trip_details.get("destination")
    time_str = trip_details.get("departure_time")

    # Get start coordinates
    start_coords, start_name, start_country = None, "Current Location", "US"
    if origin_str:
        start_coords, start_name, start_country = geocode_location(origin_str, MAPBOX_ACCESS_TOKEN)
    else:
        loc = get_user_location_ip()
        if loc:
            start_coords = [loc[1], loc[0]]  # [lon, lat]
            start_name = loc[2]
            start_country = loc[3]

    # Get end coordinates
    end_coords, end_name, end_country = geocode_location(dest_str, MAPBOX_ACCESS_TOKEN)

    # Check country restrictions (US only)
    if start_country and start_country.upper() != "US":
        st.session_state['is_processing'] = False
        update_status(error_ph, "ONLY USA SUPPORTED", "#ff4b4b", error_style=True, fade_out_delay=2.1)
        time.sleep(2.5)
        return
    if end_country and end_country.upper() != "US":
        st.session_state['is_processing'] = False
        update_status(error_ph, "ONLY USA SUPPORTED", "#ff4b4b", error_style=True, fade_out_delay=2.1)
        time.sleep(2.5)
        return

    if not start_coords or not end_coords:
        st.session_state['is_processing'] = False
        update_status(error_ph, "LOCATION ERROR", "#ff4b4b", error_style=True, fade_out_delay=1.6)
        time.sleep(2)
        return

    # Parse departure time
    try:
        dep_dt = dateutil.parser.isoparse(time_str)
        date_display = dep_dt.strftime('%m-%d-%Y')
    except Exception:
        dep_dt = datetime.now()
        date_display = dep_dt.strftime('%m-%d-%Y')

    # Get directions
    route_data = get_directions(start_coords, end_coords, MAPBOX_ACCESS_TOKEN)

    if "routes" in route_data and route_data["routes"]:
        route = route_data["routes"][0]
        dist_miles = route['distance'] / 1609.34
        dur_mins = route['duration'] / 60

        # Process route and weather
        segments, alerts = process_route_and_weather(route, dep_dt, MAPBOX_ACCESS_TOKEN)
        next_day_cast = get_next_day_weather(
            end_coords[1], end_coords[0], dep_dt, MAPBOX_ACCESS_TOKEN
        )

        # Update session state
        st.session_state['app_state'].update({
            'segments': segments,
            'alerts': alerts,
            'user_lat': start_coords[1],
            'user_lon': start_coords[0],
            'origin_name': start_name,
            'dest_name': end_name,
            'dest_coords': end_coords,
            'trip_meta': {"dist": round(dist_miles, 1), "dur": round(dur_mins)},
            'full_route_geo': route['geometry']['coordinates'],
            'next_day_forecast': next_day_cast,
            'trip_date_str': date_display,
            'departure_dt': dep_dt
        })

        st.session_state['is_processing'] = False
    else:
        st.session_state['is_processing'] = False
        update_status(error_ph, "NO ROUTE FOUND", "#ff4b4b", error_style=True, fade_out_delay=1.6)
        time.sleep(2)


def render_map():
    """Render the interactive map with route visualization."""
    app_state = st.session_state['app_state']
    layers = []

    # Route segments
    if app_state['segments']:
        layers.append(pdk.Layer(
            "PathLayer",
            data=app_state['segments'],
            get_path="path",
            get_color="outline_color",
            width_units="pixels",
            get_width=22,
            width_min_pixels=20,
            pickable=False,
            cap_rounded=True,
            joint_rounded=True,
            parameters={"depthTest": False}
        ))
        layers.append(pdk.Layer(
            "PathLayer",
            data=app_state['segments'],
            get_path="path",
            get_color="color",
            width_units="pixels",
            get_width=12,
            width_min_pixels=10,
            pickable=True,
            cap_rounded=True,
            joint_rounded=True,
            auto_highlight=True,
            parameters={"depthTest": False}
        ))

    # Start marker
    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=[{"pos": [app_state['user_lon'], app_state['user_lat']]}],
        get_position="pos",
        get_fill_color=[0, 100, 255, 76],
        get_radius=25,
        radius_units="pixels",
        stroked=False,
        pickable=False
    ))
    layers.append(pdk.Layer(
        "ScatterplotLayer",
        data=[{"pos": [app_state['user_lon'], app_state['user_lat']]}],
        get_position="pos",
        get_fill_color=[0, 100, 255],
        get_radius=15,
        radius_units="pixels",
        stroked=True,
        get_line_color=[255, 255, 255],
        get_line_width=6,
        line_width_units="pixels",
        pickable=False
    ))

    # Destination marker
    dest_pos = None
    if app_state['segments']:
        dest_pos = app_state['segments'][-1]['path'][-1]
    elif app_state.get('dest_coords'):
        dest_pos = app_state.get('dest_coords')

    if dest_pos:
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=[{"pos": dest_pos}],
            get_position="pos",
            get_fill_color=[255, 0, 85],
            get_radius=20,
            radius_units="pixels",
            stroked=False
        ))
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=[{"pos": dest_pos}],
            get_position="pos",
            get_fill_color=[255, 255, 255],
            get_radius=12,
            radius_units="pixels",
            stroked=False
        ))
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=[{"pos": dest_pos}],
            get_position="pos",
            get_fill_color=[255, 0, 85],
            get_radius=6,
            radius_units="pixels",
            stroked=False
        ))

    # Calculate view state
    if app_state['segments']:
        path_flat = [p for s in app_state['segments'] for p in s['path']]
        lats, lons = [p[1] for p in path_flat], [p[0] for p in path_flat]

        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)

        mid_lat = (min_lat + max_lat) / 2
        mid_lon = (min_lon + max_lon) / 2

        lat_diff = max_lat - min_lat
        lon_diff = max_lon - min_lon
        max_diff = max(lat_diff, lon_diff)

        zoom = 11
        if max_diff > 0:
            zoom = 11.5 - np.log2(max_diff)
            zoom = max(1, min(20, zoom))
    else:
        mid_lat, mid_lon, zoom = DEFAULT_LAT, DEFAULT_LON, 3

    # Create deck
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/navigation-night-v1",
        initial_view_state=pdk.ViewState(
            latitude=mid_lat,
            longitude=mid_lon,
            zoom=zoom
        ),
        layers=layers,
        api_keys={"mapbox": MAPBOX_ACCESS_TOKEN},
        tooltip={"html": "<b>Condition:</b> {tooltip}"}
    )
    st.pydeck_chart(deck)


def render_results():
    """Render trip results including metrics and alerts."""
    app_state = st.session_state['app_state']
    
    if not app_state['trip_meta']:
        return

    meta = app_state['trip_meta']
    alerts = app_state['alerts']
    start_dt = app_state.get('departure_dt')

    # Center container
    c1, c2, c3 = st.columns([1, 6, 1])

    with c2:
        # Timeline header
        if start_dt:
            eta_dt = start_dt + timedelta(minutes=meta['dur'])
            start_fmt = start_dt.strftime("%b %d, %I:%M %p")
            eta_fmt = eta_dt.strftime("%b %d, %I:%M %p")
            st.markdown(
                f"<div class='timeline-header'>{start_fmt} &nbsp;&nbsp;→&nbsp;&nbsp;{eta_fmt}</div>",
                unsafe_allow_html=True
            )

        # Metrics row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f"<div class='metric-box' style='animation-delay: 0.1s'><h3>Distance</h3><h2>{meta['dist']} mi</h2></div>",
                unsafe_allow_html=True
            )
        with m2:
            dur_formatted = format_duration(meta['dur'])
            st.markdown(
                f"<div class='metric-box' style='animation-delay: 0.2s'><h3>Duration</h3><h2>{dur_formatted}</h2></div>",
                unsafe_allow_html=True
            )
        with m3:
            count = len(alerts)
            color = "#ff4b4b" if count > 0 else "#00AAFF"
            status = f"{count} Alerts" if count > 0 else "Clear"
            st.markdown(
                f"<div class='metric-box' style='border-color:{color}; animation-delay: 0.3s'><h3>Status</h3><h2 style='color:{color}'>{status}</h2></div>",
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Detailed alerts
        if alerts:
            alert_count_text = f"{len(alerts)} alert{'s' if len(alerts) != 1 else ''}"
            st.markdown(f"""
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #fff; font-size: 1.3em; margin-bottom: 8px; display: flex; align-items: center; gap: 10px;">
                        <span>Weather Alerts on Route</span>
                        <span style="font-size: 0.7em; color: #888; font-weight: normal;">({alert_count_text})</span>
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            for i, a in enumerate(alerts):
                border_color = "#ff4b4b" if a['severity'] == "Severe" else "#ffa500"
                delay = 0.4 + (i * 0.1)
                
                # Format temperature with color coding
                temp = float(a['temp'])
                temp_color = "#ff6b6b" if temp < 0 else "#4ecdc4" if temp < 10 else "#ffe66d" if temp < 20 else "#95e1d3"

                html = f"""
                <div class="alert-card" style="border-left-color: {border_color}; animation-delay: {delay}s;">
                    <div class="alert-main">
                        <div class="alert-header">
                            <span class="alert-title">{a['desc']}</span>
                            <span class="alert-temp" style="color: {temp_color}; border-color: {temp_color}40;">
                                {a['temp']}°C
                            </span>
                        </div>
                        <div class="alert-loc">
                            <span>{a['location']}</span>
                        </div>
                    </div>
                    <div class="alert-time">
                        <span class="alert-time-label">Time</span>
                        <span class="alert-time-value">{a['time']}</span>
                    </div>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
        elif app_state['next_day_forecast']:
            forecast = app_state['next_day_forecast']
            # Parse and format the forecast nicely
            if ":" in forecast:
                parts = forecast.split(":", 1)
                date_part = parts[0].strip()
                weather_part = parts[1].strip() if len(parts) > 1 else ""
                st.markdown(f"""
                    <div style="
                        background: rgba(26, 28, 36, 0.8);
                        border: 1px solid rgba(0, 170, 255, 0.3);
                        border-radius: 12px;
                        padding: 16px 20px;
                        margin-top: 20px;
                        color: #d0d0d0;
                    ">
                        <div style="color: #00AAFF; font-weight: 600; margin-bottom: 8px; font-size: 1.05em;">
                            Route Clear
                        </div>
                        <div style="font-size: 0.95em; line-height: 1.6;">
                            <strong>Destination Forecast ({date_part}):</strong><br>
                            {weather_part}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info(f"Route is clear! {forecast}")


# --- MAIN UI RENDERING ---

# Map visualization
if not KEYS_PRESENT:
    st.markdown(
        """<div class='skeleton-map'><div>waiting for api keys...</div></div>
        <style>.missing-keys input { opacity: 0.3 !important; }</style>""",
        unsafe_allow_html=True
    )
else:
    render_map()

# Input form with thinking state
container_class = "" if KEYS_PRESENT else "missing-keys"
is_processing = st.session_state.get('is_processing', False)

with st.container():
    st.markdown(f'<div class="{container_class} input-form-wrapper">', unsafe_allow_html=True)
    
    # Show "Thinking" text when processing - positioned above entire form
    if is_processing:
        st.markdown("""
            <div class="thinking-indicator">
                <span class="thinking-text">Thinking</span>
            </div>
        """, unsafe_allow_html=True)
    
    with st.form(key="nav_form"):
        ph_text = "What's your next trip?" if KEYS_PRESENT else "Missing API Keys"
        user_input = st.text_input(
            "Navigation Input",
            placeholder=ph_text,
            label_visibility="collapsed",
            disabled=(not KEYS_PRESENT or is_processing)
        )
        submit_button = st.form_submit_button("Go", disabled=is_processing)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply skeleton loading effect to input when processing
    if is_processing:
        st.markdown("""
            <style>
                div[data-testid="stTextInput"] input[disabled],
                div[data-testid="stTextInput"] input:disabled {
                    background: linear-gradient(90deg, 
                        rgba(15, 17, 22, 0.85) 0%, 
                        rgba(30, 32, 38, 0.95) 50%, 
                        rgba(15, 17, 22, 0.85) 100%) !important;
                    background-size: 200% 100% !important;
                    animation: inputSkeleton 1.5s infinite linear !important;
                    border-color: rgba(255, 255, 255, 0.2) !important;
                    opacity: 0.9 !important;
                }
            </style>
        """, unsafe_allow_html=True)

# Spacer
st.markdown("<div class='result-spacer'></div>", unsafe_allow_html=True)

# Process form submission
if submit_button and user_input and KEYS_PRESENT and not is_processing:
    # Store the query and set processing state
    st.session_state['processing_query'] = user_input
    st.session_state['is_processing'] = True
    st.rerun()

# Actually process the query after UI update
if is_processing and 'processing_query' in st.session_state:
    query = st.session_state['processing_query']
    # Process the query
    _process_query(query)
    # Clear processing state
    if 'processing_query' in st.session_state:
        del st.session_state['processing_query']
    st.rerun()

# Render results
render_results()
