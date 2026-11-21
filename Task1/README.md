# Task 1: Hangman Game

A console-based Hangman word guessing game written in Python.

## How the game works
- The computer picks a random word.
- The word is shown as blanks, for example `_ _ _ _ _`.
- You guess one letter at a time.
- A correct guess reveals the letter in the word.
- A wrong guess costs one attempt and the ASCII gallows is drawn further.
- You have 6 attempts. Guess the whole word before they run out to win.

## Features
- Random word selection (`random` module)
- 6 attempts with ASCII gallows art
- Victory and defeat screens
- Uses only the Python standard library

## How to run
```
python hangman.py
```

## Concepts used
Loops, lists, strings, functions, conditions, and the `random` module.
