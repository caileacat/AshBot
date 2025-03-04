import json
import os
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), "../../data/users.json")  # Correct path

def load_user_data():
    """Loads all user memory from `users.json`."""
    try:
        with open(DATA_FILE, "r") as f:
            user_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        user_data = {}

    if "ash_personality" not in user_data:
        user_data["ash_personality"] = {"self_awareness": []}
        save_user_data(user_data)

    return user_data

def save_user_data(user_data):
    """Saves updated user memory to `users.json`."""
    max_entries = 5  

    for user_id, details in user_data.items():
        if "info" in details:
            now = datetime.utcnow().isoformat()
            for key, value in details["info"].items():
                if isinstance(value, list):
                    value.insert(0, {"value": value, "timestamp": now})
                    details["info"][key] = value[:max_entries]
                else:
                    details["info"][key] = [{"value": value, "timestamp": now}]

    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)
