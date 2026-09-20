import re

def extract_session_id(session: str):
    """Safely extracts the unique session ID from the Dialogflow context path."""
    match = re.search(r"/sessions/([^/]+)", session)
    return match.group(1) if match else ""

def get_str_from_food_dict(food_dict: dict):
    """Formats the active cart dictionary into a human-readable comma-separated string."""
    return ", ".join([f"{item} (x{int(quantity)})" for item, quantity in food_dict.items()])
