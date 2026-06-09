import re
from typing import Optional

def format_response(text: str, language: str = "hi") -> str:
    """Format response based on language preference"""
    emoji_map = {
        "price": "💰",
        "pest": "🌾",
        "scheme": "📜",
        "weather": "🌤️"
    }
    
    # In production, integrate with translation API
    if language == "hi":
        # Simple Hinglish conversion (demo)
        text = text.replace("Price Update", "Bhav")
        text = text.replace("Crop", "Fasal")
    
    return text

def extract_location(text: str) -> Optional[str]:
    states = ["punjab", "haryana", "maharashtra", "up", "gujarat"]
    for state in states:
        if state in text.lower():
            return state
    return None