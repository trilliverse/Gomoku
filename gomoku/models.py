"""Core data models for Gomoku."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Player(Enum):
    BLACK = auto()
    WHITE = auto()

    def opponent(self) -> "Player":
        return Player.WHITE if self == Player.BLACK else Player.BLACK

    @property
    def label(self) -> str:
        return "Black" if self == Player.BLACK else "White"


class GamePhase(Enum):
    RUNNING = auto()
    WIN_BLACK = auto()
    WIN_WHITE = auto()
    DRAW = auto()


class GameMode(Enum):
    HUMAN_VS_HUMAN = auto()
    HUMAN_VS_AI = auto()


@dataclass(frozen=True)
class MoveResult:
    ok: bool
    reason: str | None = None
    winner: Player | None = None
    phase: GamePhase = GamePhase.RUNNING
