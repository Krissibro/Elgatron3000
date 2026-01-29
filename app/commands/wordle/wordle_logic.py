from typing import List, Optional

def wordle_logic(guess: str, daily_word: str) -> List[int]:
    """
    Function to handle wordle logic
    :return: String of 0, 1, and 2 corresponding to red, yellow, and green.
    :
    """
    answer: str = daily_word.upper()

    # Initialize the result with all red squares
    guess_result: List[int] = [0] * len(guess)
    yellow_checker: List[Optional[str]] = list(answer)

    # Check for correct letters (green)
    for i, letter in enumerate(guess):
        if i < len(answer) and letter == answer[i]:
            guess_result[i] = 2
            yellow_checker[i] = None  # mark as used

    # Check for letters in the word but in the wrong place (yellow)
    for i, letter in enumerate(guess):
        if guess_result[i] == 0 and letter in yellow_checker:
            guess_result[i] = 1
            yellow_checker[yellow_checker.index(letter)] = None  # mark as used

    return guess_result
