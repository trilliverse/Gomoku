from gomoku.board import Board
from gomoku.models import Player
from gomoku.rules import RuleEngine


def _place_many(board: Board, stones: list[tuple[int, int, Player]]) -> None:
    for row, col, player in stones:
        assert board.place_stone(row, col, player)


def test_horizontal_win() -> None:
    board = Board()
    engine = RuleEngine()
    _place_many(board, [(7, c, Player.BLACK) for c in range(2, 7)])
    assert engine.check_win(board, 7, 6, Player.BLACK)


def test_vertical_win() -> None:
    board = Board()
    engine = RuleEngine()
    _place_many(board, [(r, 8, Player.WHITE) for r in range(4, 9)])
    assert engine.check_win(board, 8, 8, Player.WHITE)


def test_main_diagonal_win() -> None:
    board = Board()
    engine = RuleEngine()
    _place_many(board, [(i, i, Player.BLACK) for i in range(3, 8)])
    assert engine.check_win(board, 7, 7, Player.BLACK)


def test_anti_diagonal_win() -> None:
    board = Board()
    engine = RuleEngine()
    stones = [(3, 7, Player.WHITE), (4, 6, Player.WHITE), (5, 5, Player.WHITE), (6, 4, Player.WHITE), (7, 3, Player.WHITE)]
    _place_many(board, stones)
    assert engine.check_win(board, 7, 3, Player.WHITE)


def test_four_in_a_row_not_win() -> None:
    board = Board()
    engine = RuleEngine()
    _place_many(board, [(10, c, Player.BLACK) for c in range(1, 5)])
    assert not engine.check_win(board, 10, 4, Player.BLACK)


def test_broken_line_not_win() -> None:
    board = Board()
    engine = RuleEngine()
    _place_many(
        board,
        [
            (5, 2, Player.WHITE),
            (5, 3, Player.WHITE),
            (5, 4, Player.WHITE),
            (5, 6, Player.WHITE),
            (5, 7, Player.WHITE),
        ],
    )
    assert not engine.check_win(board, 5, 7, Player.WHITE)


def test_edge_win() -> None:
    board = Board()
    engine = RuleEngine()
    _place_many(board, [(r, 0, Player.BLACK) for r in range(5)])
    assert engine.check_win(board, 4, 0, Player.BLACK)
