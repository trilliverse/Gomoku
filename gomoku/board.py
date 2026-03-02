"""Board state container and basic validation methods."""

from __future__ import annotations

from typing import Optional

from .constants import BOARD_SIZE
from .models import Player


class Board:
    def __init__(self, size: int = BOARD_SIZE) -> None:
        self.size = size
        self._grid: list[list[Optional[Player]]] = []
        self.reset()

    def reset(self) -> None:
        self._grid = [[None for _ in range(self.size)] for _ in range(self.size)]

    def is_on_board(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def is_empty(self, row: int, col: int) -> bool:
        return self.is_on_board(row, col) and self._grid[row][col] is None

    def place_stone(self, row: int, col: int, player: Player) -> bool:
        if not self.is_empty(row, col):
            return False
        self._grid[row][col] = player
        return True

    def get_cell(self, row: int, col: int) -> Optional[Player]:
        if not self.is_on_board(row, col):
            return None
        return self._grid[row][col]

    def is_full(self) -> bool:
        return all(cell is not None for row in self._grid for cell in row)
