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
    CONTROL_BG_COLOR,
    GRID_COLOR,
    GRID_SPACING,
    HOVER_FILL_COLOR,
    HOVER_GHOST_BLACK_FILL,
    HOVER_GHOST_BLACK_OUTLINE,
    HOVER_GHOST_RADIUS,
    HOVER_GHOST_STIPPLE,
    HOVER_GHOST_WHITE_FILL,
    HOVER_GHOST_WHITE_OUTLINE,
    HOVER_OUTLINE_COLOR,
    HOVER_RADIUS,
    LAST_MOVE_MARK_BLACK_ON_WHITE,
    LAST_MOVE_MARK_RADIUS,
    LAST_MOVE_MARK_WHITE_ON_BLACK,
    MARGIN,
    MODE_HUMAN_VS_AI,
    MODE_HUMAN_VS_HUMAN,
    STAR_POINT_RADIUS,
    STAR_POINTS,
    STATUS_BG_COLOR,
    STATUS_BORDER_COLOR,
    STATUS_LABEL_WIDTH,
    STATUS_MAX_CHARS,
    STATUS_READY,
    STONE_RADIUS,
    UI_FONT_FAMILY,
    UI_FONT_SIZE,
    WINDOW_EXTRA_HEIGHT,
    WINDOW_EXTRA_WIDTH,
    WHITE_STONE_COLOR,
    WINDOW_TITLE,
    WIN_HIGHLIGHT_COLOR,
    WIN_HIGHLIGHT_WIDTH,
)
from .models import Player


class GomokuUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.resizable(False, False)
        self.root.configure(bg=CONTROL_BG_COLOR)

        self._board_click_handler: Optional[Callable[[int, int], None]] = None
        self._restart_handler: Optional[Callable[[], None]] = None
        self._undo_handler: Optional[Callable[[], None]] = None
        self._mode_change_handler: Optional[Callable[[str], None]] = None
        self._hover_validation_handler: Optional[Callable[[int, int], bool]] = None
        self._hover_player_provider: Optional[Callable[[], Player]] = None
        self._hover_cell: tuple[int, int] | None = None

        self._status_var = tk.StringVar(value=STATUS_READY)
        self._mode_var = tk.StringVar(value=MODE_HUMAN_VS_HUMAN)
        self._font = (UI_FONT_FAMILY, UI_FONT_SIZE)

        self.canvas = tk.Canvas(
            self.root,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg=CANVAS_BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=(10, 6))
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<Leave>", self._on_canvas_leave)

        controls = tk.Frame(self.root, bg=CONTROL_BG_COLOR)
        controls.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.restart_button = tk.Button(
            controls,
            text="Restart",
            width=12,
            command=self._on_restart,
            font=self._font,
            bg="#F9F4E8",
            relief=tk.GROOVE,
            borderwidth=1,
            activebackground="#EFE5CC",
        )
        self.restart_button.pack(side=tk.LEFT, pady=2)

        self.undo_button = tk.Button(
            controls,
            text="Undo",
            width=10,
            command=self._on_undo,
            font=self._font,
            bg="#F9F4E8",
            relief=tk.GROOVE,
            borderwidth=1,
            activebackground="#EFE5CC",
        )
        self.undo_button.pack(side=tk.LEFT, padx=(8, 0), pady=2)

        mode_frame = tk.Frame(controls, bg=CONTROL_BG_COLOR)
        mode_frame.pack(side=tk.LEFT, padx=(12, 0))

        tk.Radiobutton(
            mode_frame,
            text=MODE_HUMAN_VS_HUMAN,
            variable=self._mode_var,
            value=MODE_HUMAN_VS_HUMAN,
            command=self._on_mode_change,
            font=self._font,
            bg=CONTROL_BG_COLOR,
            activebackground=CONTROL_BG_COLOR,
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            mode_frame,
            text=MODE_HUMAN_VS_AI,
            variable=self._mode_var,
            value=MODE_HUMAN_VS_AI,
            command=self._on_mode_change,
            font=self._font,
            bg=CONTROL_BG_COLOR,
            activebackground=CONTROL_BG_COLOR,
        ).pack(side=tk.LEFT, padx=(8, 0))

        self.status_label = tk.Label(
            controls,
            textvariable=self._status_var,
            anchor="w",
            font=self._font,
            bg=STATUS_BG_COLOR,
            relief=tk.GROOVE,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=STATUS_BORDER_COLOR,
            padx=8,
            width=STATUS_LABEL_WIDTH,
        )
        self.status_label.pack(side=tk.LEFT, padx=(12, 0), fill=tk.X, expand=True)

        self.draw_grid()
        self._lock_window_size()

    def draw_grid(self) -> None:
        self.canvas.delete("grid")
        self.canvas.delete("star")
        for index in range(BOARD_SIZE):
            x = MARGIN + index * GRID_SPACING
            y = MARGIN + index * GRID_SPACING
            self.canvas.create_line(
                MARGIN, y, CANVAS_SIZE - MARGIN, y, fill=GRID_COLOR, tags="grid"
            )
            self.canvas.create_line(
                x, MARGIN, x, CANVAS_SIZE - MARGIN, fill=GRID_COLOR, tags="grid"
            )
        self._draw_star_points()

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
        self._draw_last_move_marker(row, col, player)

    def highlight_winning_line(self, points: list[tuple[int, int]]) -> None:
        self.canvas.delete("win_highlight")
        for row, col in points:
            center_x = MARGIN + col * GRID_SPACING
            center_y = MARGIN + row * GRID_SPACING
            radius = STONE_RADIUS + 3
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline=WIN_HIGHLIGHT_COLOR,
                width=WIN_HIGHLIGHT_WIDTH,
                tags="win_highlight",
            )

    def clear_overlays(self) -> None:
        self.clear_hover()
        self.canvas.delete("last_move_marker")
        self.canvas.delete("win_highlight")

    def clear_hover(self) -> None:
        self._hover_cell = None
        self.canvas.delete("hover")

    def set_status(self, text: str) -> None:
        self._status_var.set(self._fit_status_text(text))

    def show_info(self, message: str) -> None:
        messagebox.showinfo("Gomoku", message)

    def show_warning(self, message: str) -> None:
        messagebox.showwarning("Invalid Move", message)

    def bind_board_click(self, handler: Callable[[int, int], None]) -> None:
        self._board_click_handler = handler

    def bind_restart(self, handler: Callable[[], None]) -> None:
        self._restart_handler = handler

    def bind_undo(self, handler: Callable[[], None]) -> None:
        self._undo_handler = handler

    def bind_mode_change(self, handler: Callable[[str], None]) -> None:
        self._mode_change_handler = handler

    def bind_hover_validation(self, handler: Callable[[int, int], bool]) -> None:
        self._hover_validation_handler = handler

    def bind_hover_player_provider(self, handler: Callable[[], Player]) -> None:
        self._hover_player_provider = handler

    def current_mode(self) -> str:
        return self._mode_var.get()

    def schedule_after(self, ms: int, callback: Callable[[], None]) -> str:
        return str(self.root.after(ms, callback))

    def cancel_after(self, task_id: str) -> None:
        self.root.after_cancel(task_id)

    def reset_board_view(self) -> None:
        self.canvas.delete("stone")
        self.clear_overlays()
        self.draw_grid()

    @staticmethod
    def marker_color_for(player: Player) -> str:
        if player == Player.BLACK:
            return LAST_MOVE_MARK_WHITE_ON_BLACK
        return LAST_MOVE_MARK_BLACK_ON_WHITE

    @staticmethod
    def should_show_hover(
        is_on_board: bool, is_empty: bool, game_running: bool, ai_pending: bool
    ) -> bool:
        return is_on_board and is_empty and game_running and not ai_pending

    @staticmethod
    def hover_style_for(
        player: Player | None,
    ) -> tuple[str, str, str | None, int]:
        if player == Player.BLACK:
            return (
                HOVER_GHOST_BLACK_FILL,
                HOVER_GHOST_BLACK_OUTLINE,
                HOVER_GHOST_STIPPLE,
                HOVER_GHOST_RADIUS,
            )
        if player == Player.WHITE:
            return (
                HOVER_GHOST_WHITE_FILL,
                HOVER_GHOST_WHITE_OUTLINE,
                HOVER_GHOST_STIPPLE,
                HOVER_GHOST_RADIUS,
            )
        return (HOVER_FILL_COLOR, HOVER_OUTLINE_COLOR, None, HOVER_RADIUS)

    def _draw_star_points(self) -> None:
        for row, col in STAR_POINTS:
            center_x = MARGIN + col * GRID_SPACING
            center_y = MARGIN + row * GRID_SPACING
            self.canvas.create_oval(
                center_x - STAR_POINT_RADIUS,
                center_y - STAR_POINT_RADIUS,
                center_x + STAR_POINT_RADIUS,
                center_y + STAR_POINT_RADIUS,
                fill=BLACK_STONE_COLOR,
                outline=BLACK_STONE_COLOR,
                tags="star",
            )

    def _draw_last_move_marker(self, row: int, col: int, player: Player) -> None:
        self.canvas.delete("last_move_marker")
        center_x = MARGIN + col * GRID_SPACING
        center_y = MARGIN + row * GRID_SPACING
        marker_color = self.marker_color_for(player)
        self.canvas.create_oval(
            center_x - LAST_MOVE_MARK_RADIUS,
            center_y - LAST_MOVE_MARK_RADIUS,
            center_x + LAST_MOVE_MARK_RADIUS,
            center_y + LAST_MOVE_MARK_RADIUS,
            fill=marker_color,
            outline=marker_color,
            tags="last_move_marker",
        )

    def _draw_hover(self, row: int, col: int) -> None:
        self.canvas.delete("hover")
        center_x = MARGIN + col * GRID_SPACING
        center_y = MARGIN + row * GRID_SPACING
        player = (
            self._hover_player_provider()
            if self._hover_player_provider is not None
            else None
        )
        fill, outline, stipple, radius = self.hover_style_for(player)
        kwargs: dict[str, object] = {
            "fill": fill,
            "outline": outline,
            "width": 1,
            "tags": "hover",
        }
        if stipple is not None:
            kwargs["stipple"] = stipple
        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            **kwargs,
        )
        self._hover_cell = (row, col)

    def _on_canvas_click(self, event: tk.Event) -> None:
        row, col = self._pixel_to_grid(event.x, event.y)
        if self._board_click_handler is not None:
            self._board_click_handler(row, col)

    def _on_canvas_motion(self, event: tk.Event) -> None:
        row, col = self._pixel_to_grid(event.x, event.y)
        if self._hover_validation_handler is None:
            return
        if not self._hover_validation_handler(row, col):
            self.clear_hover()
            return
        if self._hover_cell == (row, col):
            return
        self._draw_hover(row, col)

    def _on_canvas_leave(self, _event: tk.Event) -> None:
        self.clear_hover()

    def _on_restart(self) -> None:
        if self._restart_handler is not None:
            self._restart_handler()

    def _on_undo(self) -> None:
        if self._undo_handler is not None:
            self._undo_handler()

    def _on_mode_change(self) -> None:
        if self._mode_change_handler is not None:
            self._mode_change_handler(self._mode_var.get())

    @staticmethod
    def _fit_status_text(text: str) -> str:
        if STATUS_MAX_CHARS <= 0:
            return ""
        if len(text) <= STATUS_MAX_CHARS:
            return text
        if STATUS_MAX_CHARS <= 3:
            return "." * STATUS_MAX_CHARS
        return f"{text[: STATUS_MAX_CHARS - 3]}..."

    def _lock_window_size(self) -> None:
        self.root.update_idletasks()
        req_w = max(1, self.root.winfo_reqwidth() + WINDOW_EXTRA_WIDTH)
        req_h = max(1, self.root.winfo_reqheight() + WINDOW_EXTRA_HEIGHT)
        self.root.geometry(f"{req_w}x{req_h}")
        self.root.minsize(req_w, req_h)
        self.root.maxsize(req_w, req_h)

    @staticmethod
    def _pixel_to_grid(x: int, y: int) -> tuple[int, int]:
        row = round((y - MARGIN) / GRID_SPACING)
        col = round((x - MARGIN) / GRID_SPACING)
        return row, col
