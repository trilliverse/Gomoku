from collections.abc import Callable

from gomoku.ai.base import BaseAI
from gomoku.board import Board
from gomoku.constants import MODE_HUMAN_VS_AI, STATUS_WAIT_AI
from gomoku.controller import GameController
from gomoku.game import GameService
from gomoku.models import GamePhase, Player
from gomoku.rules import RuleEngine


class FakeUI:
    def __init__(self) -> None:
        self.board_click_handler: Callable[[int, int], None] | None = None
        self.restart_handler: Callable[[], None] | None = None
        self.undo_handler: Callable[[], None] | None = None
        self.mode_change_handler: Callable[[str], None] | None = None
        self.statuses: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []
        self.stones: list[tuple[int, int, Player]] = []
        self.scheduled: list[tuple[int, Callable[[], None]]] = []
        self.canceled_tasks: list[str] = []
        self.winning_lines: list[list[tuple[int, int]]] = []
        self.clear_overlays_count = 0
        self.clear_hover_count = 0
        self.reset_count = 0
        self._mode = "Human vs Human"
        self._hover_validation_handler: Callable[[int, int], bool] | None = None
        self._hover_player_provider: Callable[[], Player] | None = None

    def bind_board_click(self, handler: Callable[[int, int], None]) -> None:
        self.board_click_handler = handler

    def bind_restart(self, handler: Callable[[], None]) -> None:
        self.restart_handler = handler

    def bind_undo(self, handler: Callable[[], None]) -> None:
        self.undo_handler = handler

    def bind_mode_change(self, handler: Callable[[str], None]) -> None:
        self.mode_change_handler = handler

    def current_mode(self) -> str:
        return self._mode

    def schedule_after(self, ms: int, callback: Callable[[], None]) -> str:
        self.scheduled.append((ms, callback))
        return str(len(self.scheduled))

    def cancel_after(self, task_id: str) -> None:
        self.canceled_tasks.append(task_id)

    def bind_hover_validation(self, handler: Callable[[int, int], bool]) -> None:
        self._hover_validation_handler = handler

    def bind_hover_player_provider(self, handler: Callable[[], Player]) -> None:
        self._hover_player_provider = handler

    @staticmethod
    def should_show_hover(
        is_on_board: bool, is_empty: bool, game_running: bool, ai_pending: bool
    ) -> bool:
        return is_on_board and is_empty and game_running and not ai_pending

    def draw_stone(self, row: int, col: int, player: Player) -> None:
        self.stones.append((row, col, player))

    def highlight_winning_line(self, points: list[tuple[int, int]]) -> None:
        self.winning_lines.append(points)

    def clear_overlays(self) -> None:
        self.clear_overlays_count += 1

    def clear_hover(self) -> None:
        self.clear_hover_count += 1

    def set_status(self, text: str) -> None:
        self.statuses.append(text)

    def show_info(self, message: str) -> None:
        self.infos.append(message)

    def show_warning(self, message: str) -> None:
        self.warnings.append(message)

    def reset_board_view(self) -> None:
        self.reset_count += 1
        self.clear_overlays()

    def run_scheduled(self, index: int = 0) -> None:
        _, callback = self.scheduled[index]
        callback()


class FixedAI(BaseAI):
    def __init__(self, move: tuple[int, int]) -> None:
        self._move = move

    def choose_move(self, board: Board, player: Player) -> tuple[int, int]:
        return self._move


def _new_controller(ai: BaseAI | None = None) -> tuple[GameController, GameService, FakeUI]:
    game = GameService(Board(), RuleEngine())
    ui = FakeUI()
    controller = GameController(game, ui, ai)
    controller.start()
    return controller, game, ui


def test_mode_switch_to_hvai_auto_restarts_game() -> None:
    controller, game, ui = _new_controller(FixedAI((7, 8)))

    controller.on_board_click(7, 7)
    assert game.board.get_cell(7, 7) == Player.BLACK

    controller.on_mode_change(MODE_HUMAN_VS_AI)

    assert game.board.get_cell(7, 7) is None
    assert game.current_player() == Player.BLACK
    assert ui.reset_count >= 1


def test_hvai_schedules_ai_move_after_human_move() -> None:
    controller, game, ui = _new_controller(FixedAI((7, 8)))
    controller.on_mode_change(MODE_HUMAN_VS_AI)

    controller.on_board_click(7, 7)

    assert game.board.get_cell(7, 7) == Player.BLACK
    assert len(ui.scheduled) == 1
    assert ui.scheduled[0][0] == 300

    ui.run_scheduled(0)
    assert game.board.get_cell(7, 8) == Player.WHITE


def test_click_is_ignored_while_ai_pending() -> None:
    controller, game, ui = _new_controller(FixedAI((7, 8)))
    controller.on_mode_change(MODE_HUMAN_VS_AI)
    controller.on_board_click(7, 7)

    controller.on_board_click(7, 9)

    assert game.board.get_cell(7, 9) is None
    assert ui.statuses[-1] == STATUS_WAIT_AI


def test_hvh_mode_does_not_schedule_ai() -> None:
    controller, _, ui = _new_controller(FixedAI((7, 8)))
    controller.on_board_click(7, 7)
    assert ui.scheduled == []


def test_winning_move_highlights_five_stones() -> None:
    controller, _, ui = _new_controller(FixedAI((7, 8)))
    sequence = [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 2),
        (1, 2),
        (0, 3),
        (1, 3),
        (0, 4),
    ]
    for row, col in sequence:
        controller.on_board_click(row, col)

    assert len(ui.winning_lines) == 1
    assert len(ui.winning_lines[0]) == 5


def test_restart_clears_overlays() -> None:
    controller, game, ui = _new_controller(FixedAI((7, 8)))
    controller.on_board_click(7, 7)
    assert game.phase() == GamePhase.RUNNING
    controller.on_restart()
    assert ui.clear_overlays_count >= 1


def test_occupied_move_no_popup_warning() -> None:
    controller, _, ui = _new_controller(FixedAI((7, 8)))
    controller.on_board_click(7, 7)
    controller.on_board_click(7, 7)
    assert ui.warnings == []
    assert "occupied" in ui.statuses[-1].lower()


def test_hvh_undo_reverts_one_move() -> None:
    controller, game, _ = _new_controller(FixedAI((7, 8)))
    controller.on_board_click(7, 7)
    controller.on_undo()
    assert game.board.get_cell(7, 7) is None
    assert game.current_player() == Player.BLACK


def test_hvai_undo_reverts_two_moves() -> None:
    controller, game, ui = _new_controller(FixedAI((7, 8)))
    controller.on_mode_change(MODE_HUMAN_VS_AI)
    controller.on_board_click(7, 7)
    ui.run_scheduled(0)
    assert game.board.get_cell(7, 7) == Player.BLACK
    assert game.board.get_cell(7, 8) == Player.WHITE
    controller.on_undo()
    assert game.board.get_cell(7, 7) is None
    assert game.board.get_cell(7, 8) is None
    assert game.current_player() == Player.BLACK


def test_hvai_pending_undo_cancels_ai_and_reverts_one_move() -> None:
    controller, game, ui = _new_controller(FixedAI((7, 8)))
    controller.on_mode_change(MODE_HUMAN_VS_AI)
    controller.on_board_click(7, 7)
    assert len(ui.scheduled) == 1
    controller.on_undo()
    assert ui.canceled_tasks == ["1"]
    assert game.board.get_cell(7, 7) is None
    assert game.current_player() == Player.BLACK


def test_undo_disabled_after_game_over() -> None:
    controller, game, ui = _new_controller(FixedAI((7, 8)))
    sequence = [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 2),
        (1, 2),
        (0, 3),
        (1, 3),
        (0, 4),
    ]
    for row, col in sequence:
        controller.on_board_click(row, col)
    assert game.phase() == GamePhase.WIN_BLACK
    controller.on_undo()
    assert game.board.get_cell(0, 4) == Player.BLACK
    assert ui.statuses[-1] == "Cannot undo after game over."
