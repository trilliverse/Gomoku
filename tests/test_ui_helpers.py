from gomoku.constants import STAR_POINTS
from gomoku.models import Player
from gomoku.ui import GomokuUI


def test_star_points_match_standard_15x15_positions() -> None:
    assert STAR_POINTS == ((3, 3), (3, 11), (7, 7), (11, 3), (11, 11))


def test_marker_color_for_last_move() -> None:
    assert GomokuUI.marker_color_for(Player.BLACK) != GomokuUI.marker_color_for(
        Player.WHITE
    )


def test_should_show_hover_logic() -> None:
    assert GomokuUI.should_show_hover(True, True, True, False)
    assert not GomokuUI.should_show_hover(False, True, True, False)
    assert not GomokuUI.should_show_hover(True, False, True, False)
    assert not GomokuUI.should_show_hover(True, True, False, False)
    assert not GomokuUI.should_show_hover(True, True, True, True)


def test_hover_style_follows_current_player() -> None:
    black_style = GomokuUI.hover_style_for(Player.BLACK)
    white_style = GomokuUI.hover_style_for(Player.WHITE)
    fallback_style = GomokuUI.hover_style_for(None)
    assert black_style != white_style
    assert black_style != fallback_style
    assert white_style != fallback_style
