"""Game service containing move flow and state transitions."""

from __future__ import annotations

from .board import Board
from .models import GamePhase, MoveResult, Player
from .rules import RuleEngine


class GameService:
    def __init__(self, board: Board, rule_engine: RuleEngine) -> None:
        self._board = board
        self._rule_engine = rule_engine
        self._current_player = Player.BLACK
        self._phase = GamePhase.RUNNING

    @property
    def board(self) -> Board:
        return self._board

    def new_game(self) -> None:
        self._board.reset()
        self._current_player = Player.BLACK
        self._phase = GamePhase.RUNNING

    def current_player(self) -> Player:
        return self._current_player

    def phase(self) -> GamePhase:
        return self._phase

    def play(self, row: int, col: int) -> MoveResult:
        if self._phase != GamePhase.RUNNING:
            return MoveResult(
                ok=False,
                reason="Game is already over. Click Restart to play again.",
                phase=self._phase,
            )

        if not self._board.is_on_board(row, col):
            return MoveResult(
                ok=False,
                reason="Invalid move: outside the board.",
                phase=self._phase,
            )

        if not self._board.is_empty(row, col):
            return MoveResult(
                ok=False,
                reason="Invalid move: this point is already occupied.",
                phase=self._phase,
            )

        if not self._board.place_stone(row, col, self._current_player):
            return MoveResult(
                ok=False,
                reason="Invalid move: failed to place stone.",
                phase=self._phase,
            )

        if self._rule_engine.check_win(self._board, row, col, self._current_player):
            winner = self._current_player
            self._phase = (
                GamePhase.WIN_BLACK if winner == Player.BLACK else GamePhase.WIN_WHITE
            )
            return MoveResult(ok=True, winner=winner, phase=self._phase)

        if self._board.is_full():
            self._phase = GamePhase.DRAW
            return MoveResult(ok=True, phase=self._phase)

        self._current_player = self._current_player.opponent()
        return MoveResult(ok=True, phase=self._phase)
