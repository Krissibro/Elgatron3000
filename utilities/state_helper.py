import json

state_path = "./data/bot_state.json"


def load_state():
    default_state = {
        "wordle_streak": 0,
        "free_games": []
    }
    try:
        with open(state_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If there's no file or it's corrupted, save the default state to a new file
        save_state(default_state)
        return default_state


def save_state(state):
    with open(state_path, 'w') as file:
        json.dump(state, file, indent=4)