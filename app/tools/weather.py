import httpx
from langchain.tools import tool
from datetime import datetime
from typing import Optional, Dict, Any
from app.core.config import settings
from app.tools.base import tool_with_retry

CITY_COORDINATES = {
    "mumbai": (19.0760, 72.8777), "delhi": (28.6139, 77.2090), "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867), "chennai": (13.0827, 80.2707), "kolkata": (22.5726, 88.3639),
    "pune": (18.5204, 73.8567), "ahmedabad": (23.0225, 72.5714), "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462), "patna": (25.5941, 85.1376), "bhopal": (23.2599, 77.4126),
}

FALLBACK_WEATHER = {
    "summer": {"temp": 35, "condition": "Sunny", "humidity": 40, "rain_mm": 0},
    "monsoon": {"temp": 30, "condition": "Rainy", "humidity": 85, "rain_mm": 15},
    "winter": {"temp": 20, "condition": "Clear", "humidity": 60, "rain_mm": 0},
}


@tool_with_retry(max_retries=2)
async def get_weather_forecast(location: str, days: int = 5) -> str:
    """
    Get weather forecast and farming advisory for a location.
    Args:
        location: City or district name (e.g., 'Pune', 'Ludhiana', 'Nagpur')
        days: Number of days forecast (1-7)
    """
    days = min(max(days, 1), 7)
    
    # Try real weather API
    weather_data = await fetch_weather_api(location, days)
    
    if weather_data:
        return format_weather_response(weather_data, location, days)
    
    # Fallback to season-based estimation
    return format_fallback_weather(location, days)


async def fetch_weather_api(location: str, days: int) -> Optional[Dict[str, Any]]:
    """Fetch real weather data from OpenWeather API"""
    
    if not settings.OPENWEATHER_API_KEY:
        return None
    
    # Get coordinates for location
    coords = await get_coordinates(location)
    if not coords:
        return None
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Get 5-day forecast (3-hour intervals)
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params={
                    "lat": coords[0],
                    "lon": coords[1],
                    "appid": settings.OPENWEATHER_API_KEY,
                    "units": "metric",
                    "cnt": days * 8,  # 8 intervals per day
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return parse_forecast_data(data, days)
            
            return None
            
        except Exception as e:
            print(f"Weather API error: {e}")
            return None


async def get_coordinates(location: str) -> Optional[tuple]:
    """Get coordinates for a location using geocoding"""
    
    if not settings.OPENWEATHER_API_KEY:
        return CITY_COORDINATES.get(location.lower())
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                "http://api.openweathermap.org/geo/1.0/direct",
                params={
                    "q": f"{location},IN",
                    "limit": 1,
                    "appid": settings.OPENWEATHER_API_KEY,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return (data[0]["lat"], data[0]["lon"])
            
            return CITY_COORDINATES.get(location.lower())
            
        except Exception:
            return CITY_COORDINATES.get(location.lower())


def parse_forecast_data(data: Dict, days: int) -> Dict:
    """Parse OpenWeather forecast data"""
    forecasts = []
    
    # Group by day (every 8 intervals = 1 day)
    daily_data = {}
    for item in data["list"][:days*8]:
        date = item["dt_txt"].split(" ")[0]
        if date not in daily_data:
            daily_data[date] = []
        daily_data[date].append(item)
    
    for date, items in list(daily_data.items())[:days]:
        temps = [i["main"]["temp"] for i in items]
        rains = [i.get("rain", {}).get("3h", 0) for i in items]
        
        forecasts.append({
            "date": date,
            "temp_min": min(temps),
            "temp_max": max(temps),
            "temp_avg": sum(temps) / len(temps),
            "condition": items[0]["weather"][0]["description"],
            "humidity": items[0]["main"]["humidity"],
            "rain_total": sum(rains),
            "wind_speed": items[0]["wind"]["speed"],
        })
    
    return {"forecasts": forecasts, "source": "OpenWeather/IMD"}


def format_weather_response(data: Dict, location: str, days: int) -> str:
    """Format weather response with farming advisory"""
    forecasts = data["forecasts"]
    
    rain_days = sum(1 for f in forecasts if f.get("rain_total", 0) > 5)
    hot_days = sum(1 for f in forecasts if f.get("temp_max", 0) > 35)
    
    advisory = ""
    if rain_days > 2:
        advisory = "🌧️ *Heavy rainfall expected* - Delay fertilizer/pesticide application, ensure field drainage"
    elif hot_days > 2:
        advisory = "🔥 *Heatwave conditions* - Irrigate early morning/late evening, provide shade for livestock"
    else:
        advisory = "✅ *Favorable conditions* - Good for sowing, spraying, and fertilizer application"
    
    forecast_text = ""
    for f in forecasts:
        date_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        forecast_text += f"\n📅 {date_obj.strftime('%a, %d %b')}: 🌡️ {f['temp_min']:.0f}°-{f['temp_max']:.0f}°C | 💧 Rain: {f['rain_total']:.0f}mm | 💨 Wind: {f['wind_speed']:.0f}km/h"
    
    return f"""🌤️ *Weather Forecast for {location.title()}* (Next {days} days)

{forecast_text}

🌾 *Farming Advisory:*
{advisory}

📡 *Source:* {data.get('source', 'Weather Service')}

💡 *Tip:* Plan field activities based on rain forecast. Avoid spraying if rain >5mm predicted within 24 hours."""


def format_fallback_weather(location: str, days: int) -> str:
    """Fallback weather based on season"""
    import calendar
    current_month = datetime.now().month
    
    # Determine season
    if 3 <= current_month <= 5:
        season = "summer"
        season_name = "Summer (March-May)"
    elif 6 <= current_month <= 9:
        season = "monsoon"
        season_name = "Monsoon (June-September)"
    else:
        season = "winter"
        season_name = "Winter (November-February)"
    
    weather = FALLBACK_WEATHER[season]
    
    return f"""🌤️ *Weather Outlook for {location.title()}* ({season_name})

• 🌡️ *Temperature:* ~{weather['temp']}°C
• ☁️ *Conditions:* {weather['condition']}
• 💧 *Humidity:* ~{weather['humidity']}%
• 🌧️ *Expected Rain:* ~{weather['rain_mm']}mm

🌾 *General Advisory for {season_name}:*
{get_season_advisory(season)}

⚠️ *Note:* Real-time weather data temporarily unavailable. These are seasonal estimates.

📞 For accurate forecasts, check:
   • IMD Website: mausam.imd.gov.in
   • Meghdoot App by IMD
   • Local agriculture office"""


def get_season_advisory(season: str) -> str:
    """Get season-specific farming advisory"""
    advisories = {
        "summer": "• Irrigate crops early morning or evening\n• Provide mulch to retain soil moisture\n• Watch for heat stress in livestock\n• Plan for kharif sowing preparation",
        "monsoon": "• Ensure proper drainage in fields\n• Avoid fertilizer application during heavy rain\n• Watch for pest outbreaks after rain\n• Ideal for kharif crop sowing",
        "winter": "• Protect sensitive crops from frost\n• Reduce irrigation frequency\n• Ideal for rabi crop sowing\n• Watch for low-temperature diseases"
    }
    return advisories.get(season, "Follow local agricultural extension advice.")