# AI Navigator 🤖

An intelligent route planning application with real-time weather alerts. Built with Streamlit, Mapbox, and Google Gemini AI.

## Features

- 🗺️ **Interactive Route Visualization** - Beautiful 3D map with weather-colored route segments
- 🌦️ **Real-time Weather Alerts** - Get notified about severe weather conditions along your route
- 🤖 **AI-Powered Trip Parsing** - Natural language input (e.g., "Drive from NYC to Boston next Sunday")
- 📊 **Trip Metrics** - Distance, duration, and weather status at a glance
- ⚠️ **Weather Timeline** - See when and where you'll encounter weather conditions

## Prerequisites

- Python 3.8 or higher
- Mapbox API key ([Get one here](https://account.mapbox.com/access-tokens/))
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your API keys:
     ```
     MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

## Usage

1. **Run the application:**
   ```bash
   streamlit run app.py
   ```

2. **Enter your trip query** in natural language:
   - "Drive from New York to Boston next Sunday"
   - "Route from Los Angeles to San Francisco tomorrow at 2pm"
   - "NYC to Miami on Friday"

3. **View your route** with weather-colored segments and alerts

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── config.py           # Configuration and API keys
├── api_client.py       # External API calls (Mapbox, Gemini, Open-Meteo)
├── utils.py            # Utility functions (weather processing, etc.)
├── styles.py           # CSS styling
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## API Services Used

- **Mapbox** - Geocoding and routing
- **Google Gemini** - Natural language trip parsing
- **Open-Meteo** - Weather forecasts
- **IP-API** - User location detection

## Limitations

- Currently supports **USA only** routes
- Weather forecasts limited to 14 days ahead
- Requires active internet connection

## Troubleshooting

- **"API Keys Missing"** - Make sure you've created a `.env` file with your API keys
- **"Location Error"** - Check that your location query is valid and in the USA
- **"No Route Found"** - Verify both origin and destination are accessible by road

## License

This project is open source and available for personal and commercial use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

