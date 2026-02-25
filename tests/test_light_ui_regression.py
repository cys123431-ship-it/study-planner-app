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


def test_dropdown_constructor_does_not_use_on_change_kwarg():
    source = _main_source()
    assert "on_change=update_group" not in source


def test_submit_project_reads_from_controls_not_form_state_snapshot():
    source = _main_source()
    assert "name = (name_input.value or \"\").strip()" in source
    assert "group = group_dropdown.value or \"Work\"" in source
    assert "name = (project_form_state.get(\"name\") or \"\").strip()" not in source


def test_home_view_shows_recent_projects_section():
    source = _main_source()
    assert "Recent Projects" in source
