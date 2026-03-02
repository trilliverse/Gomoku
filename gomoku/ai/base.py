"""Base AI interface for Gomoku."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..board import Board
from ..models import Player


class BaseAI(ABC):
    @abstractmethod
    def choose_move(self, board: Board, player: Player) -> tuple[int, int]:
        """Return a (row, col) move for the given board and player."""
        raise NotImplementedError
