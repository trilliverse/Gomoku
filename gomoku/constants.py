"""Project-wide constants for the Gomoku application."""

BOARD_SIZE = 15
GRID_SPACING = 40
MARGIN = 30
STONE_RADIUS = 16
CANVAS_SIZE = MARGIN * 2 + GRID_SPACING * (BOARD_SIZE - 1)

WINDOW_TITLE = "Gomoku"
CANVAS_BG_COLOR = "#D8B26E"
GRID_COLOR = "#2F2F2F"
BLACK_STONE_COLOR = "#111111"
WHITE_STONE_COLOR = "#F6F6F6"

STATUS_READY = "Current player: Black"
STATUS_WIN_BLACK = "Black wins!"
STATUS_WIN_WHITE = "White wins!"
STATUS_DRAW = "Draw game."
STATUS_AI_THINKING = "AI is thinking..."
STATUS_WAIT_AI = "Please wait: AI is thinking..."

MODE_HUMAN_VS_HUMAN = "Human vs Human"
MODE_HUMAN_VS_AI = "Human vs AI"
