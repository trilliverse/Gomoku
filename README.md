# Gomoku (Python + Tkinter)

A modular, object-oriented Gomoku implementation for coursework.

## Features

- Python implementation with Tkinter GUI
- Event-driven board interaction (mouse click to place stone)
- Core Gomoku rules on a 15x15 board (five in a row wins)
- Restart support
- Mode switch: `Human vs Human` / `Human vs AI`
- Built-in greedy AI (attack + defense scoring)
- Status feedback for current player and invalid moves
- Win / draw popup messages
- Star points rendered on Tianyuan and four hoshi points
- Hover hint on valid empty intersections
- Last-move center marker (white on black stone / black on white stone)
- Winning five-stone highlight rings
- AI extension interface (`gomoku/ai/base.py`)

## Project Structure

- `main.py`: app entry point
- `gomoku/constants.py`: GUI and rule constants
- `gomoku/models.py`: enums and move result model
- `gomoku/board.py`: board state and validation
- `gomoku/rules.py`: win checking engine
- `gomoku/game.py`: game state transitions
- `gomoku/ui.py`: Tkinter view
- `gomoku/controller.py`: event orchestration
- `gomoku/ai/base.py`: AI interface
- `gomoku/ai/greedy.py`: greedy AI implementation
- `tests/`: unit tests for rules, game flow, AI, controller, UI helpers

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
- Inject custom AI into `GameController(game, ui, ai)`
- Keep game logic in `GameService`; avoid mixing logic into UI layer

## Human vs AI Behavior

- Human always plays Black, AI plays White
- Switching mode automatically restarts the game
- In Human vs AI mode, AI moves after a 300ms delay
