import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mobile_app"))

from data_handler import DataHandler


def test_get_tasks_returns_empty_list_for_new_store(tmp_path):
    data_file = tmp_path / "schedule_data.json"
    handler = DataHandler(data_file=str(data_file))
    assert handler.get_tasks() == []


def test_loads_from_backup_when_primary_file_is_corrupt(tmp_path):
    data_file = tmp_path / "schedule_data.json"
    handler = DataHandler(data_file=str(data_file))
    target_day = "2026-02-16"

    handler.add_daily_task(target_day, "Task A")
    handler.add_daily_task(target_day, "Task B")

    data_file.write_text("{broken json", encoding="utf-8")

    recovered = DataHandler(data_file=str(data_file))
    recovered_tasks = recovered.get_daily_tasks(target_day)

    assert len(recovered_tasks) >= 1
    assert any(task.get("content") == "Task A" for task in recovered_tasks)


def test_save_does_not_leave_tmp_file(tmp_path):
    data_file = tmp_path / "schedule_data.json"
    handler = DataHandler(data_file=str(data_file))
    handler.add_daily_task("2026-02-16", "Task C")

    assert not (tmp_path / "schedule_data.json.tmp").exists()


def test_add_timetable_entry_reuses_subject_color(tmp_path):
    data_file = tmp_path / "schedule_data.json"
    handler = DataHandler(data_file=str(data_file))

    handler.add_timetable_entry("자료구조", "월", 5, 8, "#F2CF66")
    handler.add_timetable_entry("자료구조", "수", 1, 2, "#111111")

    colors = handler.get_subject_colors()
    assert colors["자료구조"] == "#F2CF66"

    entries = handler.get_timetable_entries()
    assert len(entries) == 2
    assert {entry["day"] for entry in entries} == {"월", "수"}


def test_add_timetable_entry_rejects_overlap(tmp_path):
    data_file = tmp_path / "schedule_data.json"
    handler = DataHandler(data_file=str(data_file))

    handler.add_timetable_entry("기초프로그래밍", "화", 5, 8, "#EB7F2D")

    with pytest.raises(ValueError):
        handler.add_timetable_entry("컴퓨터네트워크", "화", 8, 9, "#6CAB45")


def test_delete_timetable_entry_removes_entry(tmp_path):
    data_file = tmp_path / "schedule_data.json"
    handler = DataHandler(data_file=str(data_file))

    created = handler.add_timetable_entry("컴퓨터구조", "목", 2, 4, "#F0D169")
    handler.delete_timetable_entry(created["id"])

    assert handler.get_timetable_entries() == []
