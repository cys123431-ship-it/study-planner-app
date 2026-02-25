from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _main_source() -> str:
    return (ROOT / "mobile_app" / "main.py").read_text(encoding="utf-8")


def test_main_uses_light_theme_mode():
    source = _main_source()
    assert "page.theme_mode = ft.ThemeMode.LIGHT" in source


def test_main_no_longer_sets_dark_theme_mode():
    source = _main_source()
    assert "page.theme_mode = ft.ThemeMode.DARK" not in source


def test_timetable_grid_is_not_wrapped_with_horizontal_scroll_row():
    source = _main_source()
    assert "ft.Row([timetable_grid], scroll=ft.ScrollMode.AUTO)" not in source
