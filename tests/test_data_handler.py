import sys
from pathlib import Path


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
