from typing import List, Optional

def wordle_logic(guess: str, daily_word: str) -> List[int]:
    """
    Function to handle wordle logic
    :return: String of 0, 1, and 2 corresponding to red, yellow, and green.
    :
    """
    # Initialize the result with all red squares
    guess_result: List[int] = [0] * len(guess)
    yellow_checker: List[Optional[str]] = list(daily_word)

    # Check for correct letters (green)
    for i, letter in enumerate(guess):
        if i < len(daily_word) and letter == daily_word[i]:
            guess_result[i] = 2
            yellow_checker[i] = None  # mark as used

    # Check for letters in the word but in the wrong place (yellow)
    for i, letter in enumerate(guess):
        if guess_result[i] == 0 and letter in yellow_checker:
            guess_result[i] = 1
            yellow_checker[yellow_checker.index(letter)] = None  # mark as used

    return guess_result


NBSP = "\u00A0"   # non-breaking space
THIN = "\u2009"   # thin space
HAIR = "\u200A"   # hair space

LETTER_PAD = {
    "A": THIN,
    "B": THIN+HAIR,
    "C": THIN,
    "D": HAIR + HAIR,
    "E": HAIR + HAIR + HAIR,
    "F": THIN + HAIR,
    "G": THIN,
    "H": THIN,
    "I": NBSP + THIN + HAIR + HAIR,
    "J": THIN + HAIR,
    "K": THIN,
    "L": THIN + HAIR,
    "M": "",
    "N": HAIR + HAIR,
    "O": THIN + HAIR,
    "P": HAIR + HAIR + HAIR,
    "Q": HAIR + HAIR,
    "R": THIN,
    "S": THIN + HAIR,
    "T": HAIR + HAIR + HAIR,
    "U": THIN,
    "V": THIN,
    "W": "",
    "X": THIN,
    "Y": HAIR + HAIR + HAIR,
    "Z": NBSP + HAIR,
}

def pad_wordle_letters(word: str) -> str:
    out = []
    for c in word.upper():
        pad = LETTER_PAD.get(c, NBSP + THIN)
        out.append(c + pad)
    return "   ".join(out)