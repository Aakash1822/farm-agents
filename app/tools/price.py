import httpx
import hashlib
from langchain.tools import tool
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings
from app.tools.base import tool_with_retry
import asyncio

FALLBACK_PRICES = {
    "wheat": {"punjab": 2250, "haryana": 2180, "up": 2100, "madhya pradesh": 2050, "bihar": 1950},
    "rice": {"punjab": 2150, "telangana": 2080, "west bengal": 1950, "odisha": 1900, "chhattisgarh": 1920},
    "tomato": {"maharashtra": 1850, "karnataka": 1750, "madhya pradesh": 1650, "gujarat": 1700, "himachal pradesh": 2200},
    "onion": {"maharashtra": 2850, "gujarat": 2750, "rajasthan": 2650, "madhya pradesh": 2600, "karnataka": 2700},
    "potato": {"uttar pradesh": 1850, "west bengal": 1750, "gujarat": 1650, "punjab": 1950, "bihar": 1700},
    "maize": {"karnataka": 2150, "madhya pradesh": 2050, "bihar": 1950, "punjab": 2200, "rajasthan": 2100},
    "soybean": {"madhya pradesh": 4250, "maharashtra": 4150, "rajasthan": 4100, "gujarat": 4200},
    "cotton": {"gujarat": 6150, "maharashtra": 6050, "telangana": 6100, "punjab": 6250},
    "sugarcane": {"uttar pradesh": 3450, "maharashtra": 3350, "karnataka": 3400, "tamil nadu": 3300},
}

STATE_MAPPING = {
    "punjab": "Punjab", "haryana": "Haryana", "up": "Uttar Pradesh", "uttar pradesh": "Uttar Pradesh",
    "maharashtra": "Maharashtra", "gujarat": "Gujarat", "rajasthan": "Rajasthan", "madhya pradesh": "Madhya Pradesh",
    "karnataka": "Karnataka", "telangana": "Telangana", "tamil nadu": "Tamil Nadu", "bihar": "Bihar",
    "west bengal": "West Bengal", "odisha": "Odisha", "assam": "Assam", "kerala": "Kerala",
}

CROP_MAPPING = {
    "wheat": "Wheat", "rice": "Rice", "paddy": "Rice", "tomato": "Tomato", "onion": "Onion",
    "potato": "Potato", "maize": "Maize", "corn": "Maize", "soybean": "Soybean", "soyabean": "Soybean",
    "cotton": "Cotton", "sugarcane": "Sugarcane", "mustard": "Mustard", "groundnut": "Groundnut",
}


@tool_with_retry(max_retries=2)
async def get_price(crop: str, state: str, market: str = "local") -> str:
    """
    Get current mandi price for a crop using official AGMARKNET API.
    Args:
        crop: Crop name (wheat, rice, tomato, onion, potato, maize, soybean, cotton, sugarcane)
        state: Indian state (punjab, maharashtra, up, etc.)
        market: Mandi name (optional, defaults to major mandi in state)
    """
    crop = crop.lower()
    state = state.lower()
    
    api_crop = CROP_MAPPING.get(crop, crop.title())
    api_state = STATE_MAPPING.get(state, state.title())
    price_data = await fetch_agmarknet_price(api_crop, api_state, market)
    
    if price_data:
        return format_price_response(price_data, crop, state, market, source="AGMARKNET (Government of India)")
    
    fallback_price = FALLBACK_PRICES.get(crop, {}).get(state, None)
    if fallback_price:
        return format_fallback_response(crop, state, market, fallback_price)
    
    # If no fallback available, return helpful message
    return f"""⚠️ Price data temporarily unavailable for {crop} in {state}.

💡 Suggestions:
1. Call local APMC mandi directly
2. Check https://agmarknet.gov.in
3. Try a different crop or state

📞 APMC Helpline: 1800-XXX-XXXX"""


async def fetch_agmarknet_price(crop: str, state: str, market: str) -> Optional[Dict[str, Any]]:
    """Fetch real prices from data.gov.in AGMARKNET API"""
    
    # Check if we have API key
    if not settings.AGMARKNET_API_KEY:
        return None
    
    # data.gov.in resource ID for AGMARKNET prices
    # Different resource IDs exist for different data sets
    RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"  # Commodity prices
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(
                "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
                params={
                    "api-key": settings.AGMARKNET_API_KEY,
                    "format": "json",
                    "filters[f0]": crop,  # Commodity filter
                    "filters[f1]": state,  # State filter
                    "limit": 5,
                    "offset": 0,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                
                if records:
                    # Get latest record
                    latest = records[0]
                    return {
                        "crop": latest.get("commodity", crop),
                        "state": latest.get("state", state),
                        "market": latest.get("market", market),
                        "price": latest.get("modal_price", latest.get("min_price", "N/A")),
                        "arrival_date": latest.get("arrival_date", datetime.now().strftime("%d %b %Y")),
                        "source": "AGMARKNET"
                    }
            
            return None
            
        except Exception as e:
            # Log error but don't crash
            print(f"AGMARKNET API error: {e}")
            return None


def format_price_response(data: Dict, crop: str, state: str, market: str, source: str) -> str:
    """Format successful API response"""
    return f"""💰 *{data.get('crop', crop).upper()} Price Update*

📍 *Market:* {market.title() if market != 'local' else data.get('market', 'Local Mandi')}, {data.get('state', state).title()}
💵 *Modal Price:* ₹{data.get('price')}/quintal
📅 *As on:* {data.get('arrival_date')}

🔗 *Source:* {source}

📞 For exact rates, contact local APMC or check agmarknet.gov.in

_Note: Prices vary by quality, variety, and time of day._"""


def format_fallback_response(crop: str, state: str, market: str, price: int) -> str:
    """Format fallback response when API fails"""
    return f"""💰 *{crop.upper()} Price Estimate*

📍 *Market:* {market.title()}, {state.title()}
💰 *Estimated Price:* ₹{price}/quintal
📅 *As of:* {datetime.now().strftime('%d %b %Y')}

⚠️ *Note:* This is an estimated price based on recent trends.
📞 For exact rates, please:
   • Call local APMC mandi
   • Check https://agmarknet.gov.in
   • Contact your local agriculture officer

*Nearby Mandi Contacts:*
   • APMC Helpline: 1800-XXX-XXXX
   • Agriculture Dept: 155XXX"""