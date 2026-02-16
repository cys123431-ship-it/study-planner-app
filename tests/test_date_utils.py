import datetime
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mobile_app"))

from date_utils import to_date_str, to_iso_week_str, to_month_str


def test_to_date_str_formats_date():
    assert to_date_str(datetime.date(2026, 2, 16)) == "2026-02-16"


def test_to_month_str_formats_date():
    assert to_month_str(datetime.date(2026, 2, 16)) == "2026-02"


def test_to_iso_week_str_uses_iso_year_boundary():
    # 2024-12-30 belongs to ISO week 1 of 2025.
    assert to_iso_week_str(datetime.date(2024, 12, 30)) == "2025-W01"
