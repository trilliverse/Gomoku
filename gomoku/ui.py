"""Tkinter-based view layer for Gomoku."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from .constants import (
    BLACK_STONE_COLOR,
    BOARD_SIZE,
    CANVAS_BG_COLOR,
    CANVAS_SIZE,
    GRID_COLOR,
    GRID_SPACING,
    MARGIN,
    MODE_HUMAN_VS_AI,
    MODE_HUMAN_VS_HUMAN,
    STATUS_READY,
    STONE_RADIUS,
    WHITE_STONE_COLOR,
    WINDOW_TITLE,
)
from .models import Player


class GomokuUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.resizable(False, False)

        self._board_click_handler: Optional[Callable[[int, int], None]] = None
        self._restart_handler: Optional[Callable[[], None]] = None
        self._mode_change_handler: Optional[Callable[[str], None]] = None

        self._status_var = tk.StringVar(value=STATUS_READY)
        self._mode_var = tk.StringVar(value=MODE_HUMAN_VS_HUMAN)

        self.canvas = tk.Canvas(
            self.root,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg=CANVAS_BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=(10, 6))
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        controls = tk.Frame(self.root)
        controls.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.restart_button = tk.Button(controls, text="Restart", width=12, command=self._on_restart)
        self.restart_button.pack(side=tk.LEFT)

        mode_frame = tk.Frame(controls)
        mode_frame.pack(side=tk.LEFT, padx=(12, 0))

        tk.Radiobutton(
            mode_frame,
            text=MODE_HUMAN_VS_HUMAN,
            variable=self._mode_var,
            value=MODE_HUMAN_VS_HUMAN,
            command=self._on_mode_change,
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            mode_frame,
            text=MODE_HUMAN_VS_AI,
            variable=self._mode_var,
            value=MODE_HUMAN_VS_AI,
            command=self._on_mode_change,
        ).pack(side=tk.LEFT, padx=(8, 0))

        self.status_label = tk.Label(controls, textvariable=self._status_var, anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=(12, 0), fill=tk.X, expand=True)

        self.draw_grid()

    def draw_grid(self) -> None:
        self.canvas.delete("grid")
        for index in range(BOARD_SIZE):
            x = MARGIN + index * GRID_SPACING
            y = MARGIN + index * GRID_SPACING
            self.canvas.create_line(MARGIN, y, CANVAS_SIZE - MARGIN, y, fill=GRID_COLOR, tags="grid")
            self.canvas.create_line(x, MARGIN, x, CANVAS_SIZE - MARGIN, fill=GRID_COLOR, tags="grid")

    def draw_stone(self, row: int, col: int, player: Player) -> None:
        center_x = MARGIN + col * GRID_SPACING
        center_y = MARGIN + row * GRID_SPACING
        color = BLACK_STONE_COLOR if player == Player.BLACK else WHITE_STONE_COLOR
        self.canvas.create_oval(
            center_x - STONE_RADIUS,
            center_y - STONE_RADIUS,
            center_x + STONE_RADIUS,
            center_y + STONE_RADIUS,
            fill=color,
            outline="#333333",
            width=1,
            tags="stone",
        )

    def set_status(self, text: str) -> None:
        self._status_var.set(text)

    def show_info(self, message: str) -> None:
        messagebox.showinfo("Gomoku", message)

    def show_warning(self, message: str) -> None:
        messagebox.showwarning("Invalid Move", message)

    def bind_board_click(self, handler: Callable[[int, int], None]) -> None:
        self._board_click_handler = handler

    def bind_restart(self, handler: Callable[[], None]) -> None:
        self._restart_handler = handler

    def bind_mode_change(self, handler: Callable[[str], None]) -> None:
        self._mode_change_handler = handler

    def current_mode(self) -> str:
        return self._mode_var.get()

    def schedule_after(self, ms: int, callback: Callable[[], None]) -> str:
        return str(self.root.after(ms, callback))

    def reset_board_view(self) -> None:
        self.canvas.delete("stone")
        self.draw_grid()

    def _on_canvas_click(self, event: tk.Event) -> None:
        row, col = self._pixel_to_grid(event.x, event.y)
        if self._board_click_handler is not None:
            self._board_click_handler(row, col)

    def _on_restart(self) -> None:
        if self._restart_handler is not None:
            self._restart_handler()

    def _on_mode_change(self) -> None:
        if self._mode_change_handler is not None:
            self._mode_change_handler(self._mode_var.get())

    @staticmethod
    def _pixel_to_grid(x: int, y: int) -> tuple[int, int]:
        row = round((y - MARGIN) / GRID_SPACING)
        col = round((x - MARGIN) / GRID_SPACING)
        return row, col
