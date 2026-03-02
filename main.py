"""Entry point for the Gomoku desktop application."""

from __future__ import annotations

import tkinter as tk

from gomoku.ai.greedy import GreedyAI
from gomoku.board import Board
from gomoku.controller import GameController
from gomoku.game import GameService
from gomoku.rules import RuleEngine
from gomoku.ui import GomokuUI


def build_app() -> tk.Tk:
    root = tk.Tk()
    board = Board()
    rule_engine = RuleEngine()
    game = GameService(board, rule_engine)
    ui = GomokuUI(root)
    controller = GameController(game, ui, GreedyAI())
    controller.start()
    return root


if __name__ == "__main__":
    app = build_app()
    app.mainloop()
