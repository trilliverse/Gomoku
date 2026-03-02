"""Controller layer that bridges UI events and game service logic."""

from __future__ import annotations

from .constants import STATUS_DRAW, STATUS_WIN_BLACK, STATUS_WIN_WHITE
from .game import GameService
from .models import GamePhase, Player
from .ui import GomokuUI


class GameController:
    def __init__(self, game: GameService, ui: GomokuUI) -> None:
        self._game = game
        self._ui = ui

    def start(self) -> None:
        self._ui.bind_board_click(self.on_board_click)
        self._ui.bind_restart(self.on_restart)
        self._ui.set_status(self._current_player_status())

    def on_board_click(self, row: int, col: int) -> None:
        result = self._game.play(row, col)

        if not result.ok:
            message = result.reason or "Invalid move."
            self._ui.set_status(message)
            self._ui.show_warning(message)
            return

        placed_player = self._game.board.get_cell(row, col)
        if placed_player is not None:
            self._ui.draw_stone(row, col, placed_player)

        if result.winner is not None:
            win_text = STATUS_WIN_BLACK if result.winner == Player.BLACK else STATUS_WIN_WHITE
            self._ui.set_status(win_text)
            self._ui.show_info(win_text)
            return

        if result.phase == GamePhase.DRAW:
            self._ui.set_status(STATUS_DRAW)
            self._ui.show_info(STATUS_DRAW)
            return

        self._ui.set_status(self._current_player_status())

    def on_restart(self) -> None:
        self._game.new_game()
        self._ui.reset_board_view()
        self._ui.set_status(self._current_player_status())

    def _current_player_status(self) -> str:
        return f"Current player: {self._game.current_player().label}"
