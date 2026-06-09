from typing import Tuple, bool

INDIAN_STATES = [
    "punjab", "haryana", "maharashtra", "up", "gujarat", 
    "rajasthan", "bihar", "west bengal", "telangana", "karnataka"
]

CROPS = ["wheat", "rice", "tomato", "onion", "potato", "maize"]

def validate_indian_state(state: str) -> bool:
    return state.lower() in INDIAN_STATES

def validate_crop_name(crop: str) -> bool:
    return crop.lower() in CROPS