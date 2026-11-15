
import os
import random

MAX_MISTAKES = 6

# Fallback list used if 'words.txt' (the downloaded English word list) is missing.
DEFAULT_WORDS = [
    "python", "variable", "function", "keyboard", "internet", "algorithm",
    "database", "compiler", "network", "program", "developer", "terminal",
    "software", "hardware", "library", "teacher", "student", "computer",
    "elephant", "mountain", "chocolate", "umbrella", "adventure", "diamond",
]

# One ASCII picture for each number of mistakes (0 to 6).
HANGMAN_STAGES = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========""",
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========""",
]


def load_words(filename="words.txt"):
    """Load words from a text file (one per line); fall back to DEFAULT_WORDS."""
    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as f:
            words = [w.strip().lower() for w in f
                     if w.strip().isalpha() and len(w.strip()) >= 4]
        if words:
            return words
    return DEFAULT_WORDS


def masked_word(secret, guessed):
    """Return the word with unguessed letters hidden, e.g. 'p _ t h _ n'."""
    return " ".join(ch if ch in guessed else "_" for ch in secret)


def show_status(secret, guessed, wrong):
    """Print the gallows, masked word and guessed letters."""
    print(HANGMAN_STAGES[len(wrong)])
    print(f"\n  Word: {masked_word(secret, guessed)}")
    print(f"  Wrong letters: {' '.join(sorted(wrong)) or '-'}")
    print(f"  Attempts left: {MAX_MISTAKES - len(wrong)}\n")


def get_guess(guessed, wrong):
    """Ask for a valid single new letter."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter exactly ONE letter (a-z).")
        elif guess in guessed or guess in wrong:
            print(f"You already guessed '{guess}'. Try another (no penalty).")
        else:
            return guess


def play_round(words):
    """Play one game. Return True if the player won."""
    secret = random.choice(words)
    guessed = set()   # correct letters
    wrong = set()     # incorrect letters

    print("\n" + "=" * 40)
    print("        WELCOME TO HANGMAN")
    print("=" * 40)

    while len(wrong) < MAX_MISTAKES and not set(secret) <= guessed:
        show_status(secret, guessed, wrong)
        guess = get_guess(guessed, wrong)

        if guess in secret:
            guessed.add(guess)
            print(f"\nGood job! '{guess}' is in the word.")
        else:
            wrong.add(guess)
            print(f"\nSorry, '{guess}' is not in the word.")

    show_status(secret, guessed, wrong)

    if set(secret) <= guessed:
        print("*" * 40)
        print(f"  YOU WIN! The word was '{secret.upper()}'.")
        print("*" * 40)
        return True

    print("#" * 40)
    print(f"  GAME OVER! The word was '{secret.upper()}'.")
    print("#" * 40)
    return False


def main():
    words = load_words()
    wins = losses = 0

    while True:
        if play_round(words):
            wins += 1
        else:
            losses += 1
        print(f"\nScore -> Wins: {wins} | Losses: {losses}")

        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing. Goodbye!")
            break


if __name__ == "__main__":
    main()