from gomoku.ai.greedy import GreedyAI
from gomoku.board import Board
from gomoku.models import Player


def _place_many(board: Board, stones: list[tuple[int, int, Player]]) -> None:
    for row, col, player in stones:
        assert board.place_stone(row, col, player)


def test_ai_chooses_immediate_winning_move() -> None:
    board = Board()
    ai = GreedyAI()
    _place_many(
        board,
        [
            (7, 3, Player.WHITE),
            (7, 4, Player.WHITE),
            (7, 5, Player.WHITE),
            (7, 6, Player.WHITE),
            (6, 6, Player.BLACK),
        ],
    )
    assert ai.choose_move(board, Player.WHITE) == (7, 7)


def test_ai_blocks_opponent_immediate_win() -> None:
    board = Board()
    ai = GreedyAI()
    _place_many(
        board,
        [
            (7, 3, Player.BLACK),
            (7, 4, Player.BLACK),
            (7, 5, Player.BLACK),
            (7, 6, Player.BLACK),
            (6, 6, Player.WHITE),
        ],
    )
    assert ai.choose_move(board, Player.WHITE) == (7, 7)


def test_ai_chooses_center_on_empty_board() -> None:
    board = Board()
    ai = GreedyAI()
    assert ai.choose_move(board, Player.WHITE) == (7, 7)


def test_ai_tie_break_prefers_center_then_row_col() -> None:
    board = Board()
    ai = GreedyAI()
    assert board.place_stone(7, 7, Player.BLACK)
    assert ai.choose_move(board, Player.WHITE) == (6, 7)
