import json
import pickle


state_path = "./data/bot_state.json"
wordle_state_path = "./data/wordle_state.pkl"


def load_state():
    default_state = {
        "free_games": []
    }
    try:
        with open(state_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If there's no file, or it's corrupted, save the default state to a new file
        save_state(default_state)
        return default_state


def save_state(state):
    with open(state_path, 'w') as file:
        json.dump(state, file, indent=4)


def save_wordle_game_state(wordle_game):
    with open(wordle_state_path, 'wb') as file:
        pickle.dump(wordle_game, file)


async def load_wordle_game_state():
    try:
        with open(wordle_state_path, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        # Return a new Wordle game instance if no save file exists
        from commands.wordle import Wordle
        wordle = Wordle()
        await wordle.pick_new_word()
        return wordle

