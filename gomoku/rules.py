"""Rule engine for Gomoku win detection."""

from __future__ import annotations

from .board import Board
from .models import Player


class RuleEngine:
    _DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))

    def check_win(self, board: Board, row: int, col: int, player: Player) -> bool:
        if board.get_cell(row, col) != player:
            return False

        for d_row, d_col in self._DIRECTIONS:
            total = 1
            total += self._count_one_direction(board, row, col, player, d_row, d_col)
            total += self._count_one_direction(board, row, col, player, -d_row, -d_col)
            if total >= 5:
                return True
        return False

    def _count_one_direction(
        self,
        board: Board,
        row: int,
        col: int,
        player: Player,
        d_row: int,
        d_col: int,
    ) -> int:
        count = 0
        r, c = row + d_row, col + d_col
        while board.is_on_board(r, c) and board.get_cell(r, c) == player:
            count += 1
            r += d_row
            c += d_col
        return count
