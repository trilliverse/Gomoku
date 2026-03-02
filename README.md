# Gomoku (Python + Tkinter)

A modular, object-oriented Gomoku implementation for coursework.

## Features

- Python implementation with Tkinter GUI
- Event-driven board interaction (mouse click to place stone)
- Core Gomoku rules on a 15x15 board (five in a row wins)
- Restart support
- Status feedback for current player and invalid moves
- Win / draw popup messages
- AI extension interface reserved (`gomoku/ai/base.py`)

## Project Structure

- `main.py`: app entry point
- `gomoku/constants.py`: GUI and rule constants
- `gomoku/models.py`: enums and move result model
- `gomoku/board.py`: board state and validation
- `gomoku/rules.py`: win checking engine
- `gomoku/game.py`: game state transitions
- `gomoku/ui.py`: Tkinter view
- `gomoku/controller.py`: event orchestration
- `gomoku/ai/base.py`: AI interface placeholder
- `tests/`: unit tests for rules and game service

## Requirements

- Python 3.10+
- Tkinter (usually bundled with Python on Windows)
- pytest (for tests)

## Run

```bash
cd gomoku
python main.py
```

## Test

```bash
cd gomoku
python -m pytest -q
```

## Extension Notes

- Implement a class that inherits `BaseAI` in `gomoku/ai/`
- Add mode switching in the controller/UI to enable human-vs-AI
- Keep game logic in `GameService`; avoid mixing logic into UI layer
