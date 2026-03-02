"""Controller layer that bridges UI events and game service logic."""

from __future__ import annotations

from .ai.base import BaseAI
from .constants import (
    MODE_HUMAN_VS_AI,
    STATUS_AI_THINKING,
    STATUS_DRAW,
    STATUS_WAIT_AI,
    STATUS_WIN_BLACK,
    STATUS_WIN_WHITE,
)
from .game import GameService
from .models import GameMode, GamePhase, Player
from .ui import GomokuUI


class GameController:
    def __init__(self, game: GameService, ui: GomokuUI, ai: BaseAI | None = None) -> None:
        self._game = game
        self._ui = ui
        self._ai = ai
        self._mode = GameMode.HUMAN_VS_HUMAN
        self._ai_player = Player.WHITE
        self._ai_pending = False

    def start(self) -> None:
        self._ui.bind_board_click(self.on_board_click)
        self._ui.bind_restart(self.on_restart)
        self._ui.bind_mode_change(self.on_mode_change)
        self._ui.set_status(self._current_player_status())

    def on_board_click(self, row: int, col: int) -> None:
        if self._ai_pending:
            self._ui.set_status(STATUS_WAIT_AI)
            return

        if not self._handle_move(row, col, show_warning=True):
            return

        if self._is_ai_turn():
            self._schedule_ai_move()

    def on_restart(self) -> None:
        self._ai_pending = False
        self._game.new_game()
        self._ui.reset_board_view()
        self._ui.set_status(self._current_player_status())

    def on_mode_change(self, mode_value: str) -> None:
        self._mode = (
            GameMode.HUMAN_VS_AI
            if mode_value == MODE_HUMAN_VS_AI
            else GameMode.HUMAN_VS_HUMAN
        )
        self.on_restart()

    def _schedule_ai_move(self) -> None:
        if self._ai_pending or not self._is_ai_turn():
            return
        self._ai_pending = True
        self._ui.set_status(STATUS_AI_THINKING)
        self._ui.schedule_after(300, self._execute_ai_move)

    def _execute_ai_move(self) -> None:
        if not self._ai_pending:
            return
        self._ai_pending = False

        if not self._is_ai_turn():
            return

        move = self._choose_ai_move()
        if move is None:
            return

        row, col = move
        self._handle_move(row, col, show_warning=False)

    def _choose_ai_move(self) -> tuple[int, int] | None:
        fallback_move = self._find_first_empty()
        if self._ai is None:
            return fallback_move

        try:
            row, col = self._ai.choose_move(self._game.board, self._ai_player)
        except Exception:
            return fallback_move

        if self._is_valid_empty(row, col):
            return (row, col)

        print("AI produced invalid move; using fallback move.")
        return fallback_move

    def _find_first_empty(self) -> tuple[int, int] | None:
        board = self._game.board
        for row in range(board.size):
            for col in range(board.size):
                if board.is_empty(row, col):
                    return (row, col)
        return None

    def _is_valid_empty(self, row: int, col: int) -> bool:
        board = self._game.board
        return board.is_on_board(row, col) and board.is_empty(row, col)

    def _handle_move(self, row: int, col: int, show_warning: bool) -> bool:
        result = self._game.play(row, col)

        if not result.ok:
            message = result.reason or "Invalid move."
            self._ui.set_status(message)
            if show_warning:
                self._ui.show_warning(message)
            return False

        placed_player = self._game.board.get_cell(row, col)
        if placed_player is not None:
            self._ui.draw_stone(row, col, placed_player)

        if result.winner is not None:
            win_text = (
                STATUS_WIN_BLACK if result.winner == Player.BLACK else STATUS_WIN_WHITE
            )
            self._ui.set_status(win_text)
            self._ui.show_info(win_text)
            return False

        if result.phase == GamePhase.DRAW:
            self._ui.set_status(STATUS_DRAW)
            self._ui.show_info(STATUS_DRAW)
            return False

        self._ui.set_status(self._current_player_status())
        return True

    def _is_ai_turn(self) -> bool:
        return (
            self._mode == GameMode.HUMAN_VS_AI
            and self._ai is not None
            and self._game.phase() == GamePhase.RUNNING
            and self._game.current_player() == self._ai_player
        )

    def _current_player_status(self) -> str:
        return f"Current player: {self._game.current_player().label}"
