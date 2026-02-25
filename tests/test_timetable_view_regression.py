from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_timetable_view_does_not_use_removed_alignment_center_constant():
    source = (ROOT / "mobile_app" / "main.py").read_text(encoding="utf-8")
    assert "ft.alignment.center" not in source
