import json

from commands.wordle.wordle_commands import Wordle

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


# def save_wordle_game_state(wordle_game):
#     with open('wordle_state.json', 'w') as file:
#         json.dump(wordle_game.get_dict_of_data(), file)
#
#
# async def load_wordle_game_state():
#     wordle = Wordle()
#
#     if os.path.exists('wordle_state.json'):
#         with open('wordle_state.json', 'r') as file:
#             data = json.load(file)
#             wordle.retrieve_data_from_dict(data)
#     else:
#         await wordle.pick_new_word()
#
#     return wordle

