from gomoku.board import Board
from gomoku.game import GameService
from gomoku.models import GamePhase, Player
from gomoku.rules import RuleEngine


def _new_game_service() -> GameService:
    return GameService(Board(), RuleEngine())


def test_turn_switch_after_valid_move() -> None:
    game = _new_game_service()
    result = game.play(7, 7)
    assert result.ok
    assert game.current_player() == Player.WHITE
    assert game.phase() == GamePhase.RUNNING


def test_occupied_position_is_invalid() -> None:
    game = _new_game_service()
    first = game.play(7, 7)
    second = game.play(7, 7)
    assert first.ok
    assert not second.ok
    assert second.reason is not None
    assert "occupied" in second.reason.lower()


def test_win_and_no_further_moves_after_finish() -> None:
    game = _new_game_service()
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

    last_result = None
    for row, col in sequence:
        last_result = game.play(row, col)

    assert last_result is not None
    assert last_result.ok
    assert last_result.winner == Player.BLACK
    assert last_result.winning_line is not None
    assert len(last_result.winning_line) == 5
    assert game.phase() == GamePhase.WIN_BLACK

    blocked = game.play(2, 2)
    assert not blocked.ok
    assert blocked.reason is not None
    assert "over" in blocked.reason.lower()


def test_new_game_resets_all_state() -> None:
    game = _new_game_service()
    game.play(7, 7)
    game.play(7, 8)

    game.new_game()

    assert game.current_player() == Player.BLACK
    assert game.phase() == GamePhase.RUNNING
    assert game.board.get_cell(7, 7) is None
    assert game.board.get_cell(7, 8) is None
