"""Rule engine for Gomoku win detection."""

from __future__ import annotations

from .board import Board
from .models import Player


class RuleEngine:
    _DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))

    def check_win(self, board: Board, row: int, col: int, player: Player) -> bool:
        return self.find_winning_line(board, row, col, player) is not None

    def find_winning_line(
        self, board: Board, row: int, col: int, player: Player
    ) -> list[tuple[int, int]] | None:
        if board.get_cell(row, col) != player:
            return None

        for d_row, d_col in self._DIRECTIONS:
            chain = self._collect_line(board, row, col, player, d_row, d_col)
            if len(chain) >= 5:
                return self._closest_five_with_anchor(chain, (row, col))
        return None

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

    def _collect_line(
        self,
        board: Board,
        row: int,
        col: int,
        player: Player,
        d_row: int,
        d_col: int,
    ) -> list[tuple[int, int]]:
        backward: list[tuple[int, int]] = []
        r, c = row - d_row, col - d_col
        while board.is_on_board(r, c) and board.get_cell(r, c) == player:
            backward.append((r, c))
            r -= d_row
            c -= d_col

        forward: list[tuple[int, int]] = []
        r, c = row + d_row, col + d_col
        while board.is_on_board(r, c) and board.get_cell(r, c) == player:
            forward.append((r, c))
            r += d_row
            c += d_col

        backward.reverse()
        return backward + [(row, col)] + forward

    @staticmethod
    def _closest_five_with_anchor(
        chain: list[tuple[int, int]], anchor: tuple[int, int]
    ) -> list[tuple[int, int]]:
        anchor_index = chain.index(anchor)
        start_min = max(0, anchor_index - 4)
        start_max = min(anchor_index, len(chain) - 5)

        best_start = start_min
        best_distance = 10**9
        for start in range(start_min, start_max + 1):
            middle = start + 2
            distance = abs(middle - anchor_index)
            if distance < best_distance:
                best_distance = distance
                best_start = start
        return chain[best_start : best_start + 5]
