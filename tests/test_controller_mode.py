from collections.abc import Callable

from gomoku.ai.base import BaseAI
from gomoku.board import Board
from gomoku.constants import MODE_HUMAN_VS_AI, STATUS_WAIT_AI
from gomoku.controller import GameController
from gomoku.game import GameService
from gomoku.models import Player
from gomoku.rules import RuleEngine


class FakeUI:
    def __init__(self) -> None:
        self.board_click_handler: Callable[[int, int], None] | None = None
        self.restart_handler: Callable[[], None] | None = None
        self.mode_change_handler: Callable[[str], None] | None = None
        self.statuses: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []
        self.stones: list[tuple[int, int, Player]] = []
        self.scheduled: list[tuple[int, Callable[[], None]]] = []
        self.reset_count = 0
        self._mode = "Human vs Human"

    def bind_board_click(self, handler: Callable[[int, int], None]) -> None:
        self.board_click_handler = handler

    def bind_restart(self, handler: Callable[[], None]) -> None:
        self.restart_handler = handler

    def bind_mode_change(self, handler: Callable[[str], None]) -> None:
        self.mode_change_handler = handler

    def current_mode(self) -> str:
        return self._mode

    def schedule_after(self, ms: int, callback: Callable[[], None]) -> str:
        self.scheduled.append((ms, callback))
        return str(len(self.scheduled))

    def draw_stone(self, row: int, col: int, player: Player) -> None:
        self.stones.append((row, col, player))

    def set_status(self, text: str) -> None:
        self.statuses.append(text)

    def show_info(self, message: str) -> None:
        self.infos.append(message)

    def show_warning(self, message: str) -> None:
        self.warnings.append(message)

    def reset_board_view(self) -> None:
        self.reset_count += 1

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
