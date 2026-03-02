"""Greedy AI implementation for Gomoku."""

from __future__ import annotations

from ..board import Board
from ..models import Player
from .base import BaseAI


class GreedyAI(BaseAI):
    _DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))

    def choose_move(self, board: Board, player: Player) -> tuple[int, int]:
        best_move: tuple[int, int] | None = None
        best_key: tuple[int, int, int, int, int] | None = None

        for row in range(board.size):
            for col in range(board.size):
                if not board.is_empty(row, col):
                    continue
                key = self._evaluate_move_key(board, row, col, player)
                if best_key is None or key > best_key:
                    best_key = key
                    best_move = (row, col)

        if best_move is None:
            raise ValueError("No valid move available for AI.")
        return best_move

    def _evaluate_move_key(
        self,
        board: Board,
        row: int,
        col: int,
        player: Player,
    ) -> tuple[int, int, int, int, int]:
        opponent = player.opponent()
        attack_score = self._point_score(board, row, col, player)
        defense_score = self._point_score(board, row, col, opponent)
        total_score = attack_score + int(defense_score * 1.1)

        if self._is_winning_move(board, row, col, player):
            priority = 3
        elif self._is_winning_move(board, row, col, opponent):
            priority = 2
        else:
            priority = 1

        center = board.size // 2
        dist2 = (row - center) * (row - center) + (col - center) * (col - center)
        return (priority, total_score, -dist2, -row, -col)

    def _is_winning_move(self, board: Board, row: int, col: int, player: Player) -> bool:
        for d_row, d_col in self._DIRECTIONS:
            count, _ = self._line_stats(board, row, col, player, d_row, d_col)
            if count >= 5:
                return True
        return False

    def _point_score(self, board: Board, row: int, col: int, player: Player) -> int:
        total = 0
        for d_row, d_col in self._DIRECTIONS:
            count, open_ends = self._line_stats(board, row, col, player, d_row, d_col)
            total += self._pattern_score(count, open_ends)
        return total

    def _line_stats(
        self,
        board: Board,
        row: int,
        col: int,
        player: Player,
        d_row: int,
        d_col: int,
    ) -> tuple[int, int]:
        count = 1
        open_ends = 0

        for sign in (1, -1):
            r = row + sign * d_row
            c = col + sign * d_col
            while board.is_on_board(r, c) and board.get_cell(r, c) == player:
                count += 1
                r += sign * d_row
                c += sign * d_col
            if board.is_on_board(r, c) and board.get_cell(r, c) is None:
                open_ends += 1

        return count, open_ends

    @staticmethod
    def _pattern_score(count: int, open_ends: int) -> int:
        if count >= 5:
            return 100000
        if count == 4 and open_ends == 2:
            return 10000
        if count == 4 and open_ends == 1:
            return 3000
        if count == 3 and open_ends == 2:
            return 1000
        if count == 3 and open_ends == 1:
            return 200
        if count == 2 and open_ends == 2:
            return 80
        if count == 2 and open_ends == 1:
            return 30
        if count == 1 and open_ends == 2:
            return 10
        return 1
