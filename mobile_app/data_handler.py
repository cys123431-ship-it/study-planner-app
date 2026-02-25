import datetime
import json
import os
import shutil


def _resolve_data_file():
    try:
        base_dir = os.path.join(os.path.expanduser("~"), ".study_planner")
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, "schedule_data.json")
    except Exception:
        return "schedule_data.json"


DATA_FILE = _resolve_data_file()


class DataHandler:
    VALID_TIMETABLE_DAYS = ["월", "화", "수", "목", "금", "토"]
    MIN_PERIOD = 0
    MAX_PERIOD = 14
    DEFAULT_SUBJECT_COLOR = "#6CAB45"

    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.backup_file = f"{data_file}.bak"
        self.data = self._load_data()

    def _default_data(self):
        return {
            "daily": {},   # Format: "YYYY-MM-DD": [{"id": ..., "content": ..., "done": ..., "category": "todo"}]
            "weekly": {},  # Format: "YYYY-W##": {"Mon": [], ...}
            "monthly": {}, # Format: "YYYY-MM": []
            "memo": "",
            "timetable_entries": [],  # Format: [{"id": ..., "subject": ..., "day": ..., "start_period": ..., "end_period": ...}]
            "subject_colors": {},     # Format: {"subject": "#RRGGBB"}
        }

    def _default_week(self):
        return {day: [] for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}

    def _normalize_hex_color(self, value):
        if isinstance(value, str):
            text = value.strip()
            if len(text) == 7 and text[0] == "#":
                hex_part = text[1:]
                if all(ch in "0123456789abcdefABCDEF" for ch in hex_part):
                    return f"#{hex_part.upper()}"
        return self.DEFAULT_SUBJECT_COLOR

    def _normalize_subject_colors(self, raw):
        if not isinstance(raw, dict):
            return {}

        normalized = {}
        for subject, color in raw.items():
            if not isinstance(subject, str):
                continue
            subject_name = subject.strip()
            if not subject_name:
                continue
            normalized[subject_name] = self._normalize_hex_color(color)
        return normalized

    def _normalize_timetable_entries(self, raw):
        if not isinstance(raw, list):
            return []

        normalized = []
        for entry in raw:
            if not isinstance(entry, dict):
                continue

            subject = str(entry.get("subject", "")).strip()
            day = str(entry.get("day", "")).strip()
            if not subject or day not in self.VALID_TIMETABLE_DAYS:
                continue

            try:
                start_period = int(entry.get("start_period"))
                end_period = int(entry.get("end_period"))
            except (TypeError, ValueError):
                continue

            if start_period < self.MIN_PERIOD or end_period > self.MAX_PERIOD or start_period > end_period:
                continue

            entry_id = entry.get("id")
            if not isinstance(entry_id, str) or not entry_id:
                entry_id = datetime.datetime.now().isoformat()

            normalized.append(
                {
                    "id": entry_id,
                    "subject": subject,
                    "day": day,
                    "start_period": start_period,
                    "end_period": end_period,
                }
            )
        return normalized

    def _normalize_data(self, raw):
        default = self._default_data()
        if not isinstance(raw, dict):
            return default

        daily = raw.get("daily")
        weekly = raw.get("weekly")
        monthly = raw.get("monthly")
        memo = raw.get("memo")
        timetable_entries = raw.get("timetable_entries")
        subject_colors = raw.get("subject_colors")

        default["daily"] = daily if isinstance(daily, dict) else {}
        default["weekly"] = weekly if isinstance(weekly, dict) else {}
        default["monthly"] = monthly if isinstance(monthly, dict) else {}
        default["memo"] = memo if isinstance(memo, str) else ""
        default["timetable_entries"] = self._normalize_timetable_entries(timetable_entries)
        default["subject_colors"] = self._normalize_subject_colors(subject_colors)
        return default

    def _load_json_file(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _write_json_atomic(self, payload, create_backup=True):
        tmp_file = f"{self.data_file}.tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as file:
                json.dump(payload, file, indent=4, ensure_ascii=False)

            if create_backup and os.path.exists(self.data_file):
                shutil.copy2(self.data_file, self.backup_file)

            os.replace(tmp_file, self.data_file)
        except Exception:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
            raise

    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                return self._normalize_data(self._load_json_file(self.data_file))
            except Exception as exc:
                print(f"Error loading data file: {exc}")

        if os.path.exists(self.backup_file):
            try:
                recovered = self._normalize_data(self._load_json_file(self.backup_file))
                self._write_json_atomic(recovered, create_backup=False)
                print("Recovered data from backup file.")
                return recovered
            except Exception as exc:
                print(f"Error loading backup file: {exc}")

        return self._default_data()

    def _save_data(self):
        try:
            self._write_json_atomic(self.data, create_backup=True)
        except Exception as exc:
            print(f"Error saving data: {exc}")

    # --- Daily Operations ---
    def get_daily_tasks(self, date_str):
        # date_str format: "YYYY-MM-DD"
        return self.data.get("daily", {}).get(date_str, [])

    def add_daily_task(self, date_str, content, category="todo"):
        daily_map = self.data.setdefault("daily", {})
        if date_str not in daily_map or not isinstance(daily_map[date_str], list):
            daily_map[date_str] = []

        new_task = {
            "id": datetime.datetime.now().isoformat(),
            "content": content,
            "done": False,
            "category": category,
        }
        daily_map[date_str].append(new_task)
        self._save_data()

    def toggle_daily_task(self, date_str, task_id):
        for task in self.data.get("daily", {}).get(date_str, []):
            if task.get("id") == task_id:
                task["done"] = not bool(task.get("done"))
                self._save_data()
                return

    def delete_daily_task(self, date_str, task_id):
        daily_map = self.data.get("daily", {})
        if date_str in daily_map:
            daily_map[date_str] = [task for task in daily_map[date_str] if task.get("id") != task_id]
            self._save_data()

    # --- Weekly Operations ---
    def get_weekly_tasks(self, week_str):
        # week_str format: "YYYY-W##"
        week_data = self.data.get("weekly", {}).get(week_str)
        if not isinstance(week_data, dict):
            return self._default_week()

        normalized = self._default_week()
        for day in normalized:
            if isinstance(week_data.get(day), list):
                normalized[day] = week_data[day]
        return normalized

    def add_weekly_task(self, week_str, day, content):
        weekly_map = self.data.setdefault("weekly", {})
        if week_str not in weekly_map or not isinstance(weekly_map[week_str], dict):
            weekly_map[week_str] = self._default_week()

        if day not in weekly_map[week_str] or not isinstance(weekly_map[week_str][day], list):
            weekly_map[week_str][day] = []

        new_task = {
            "id": datetime.datetime.now().isoformat(),
            "content": content,
            "done": False,
        }
        weekly_map[week_str][day].append(new_task)
        self._save_data()

    def delete_weekly_task(self, week_str, day, task_id):
        weekly_map = self.data.get("weekly", {})
        if week_str in weekly_map and day in weekly_map[week_str]:
            weekly_map[week_str][day] = [task for task in weekly_map[week_str][day] if task.get("id") != task_id]
            self._save_data()

    def toggle_weekly_task(self, week_str, day, task_id):
        weekly_map = self.data.get("weekly", {})
        if week_str in weekly_map and day in weekly_map[week_str]:
            for task in weekly_map[week_str][day]:
                if task.get("id") == task_id:
                    task["done"] = not bool(task.get("done"))
                    self._save_data()
                    return

    # --- Monthly Operations (Goal Oriented) ---
    def get_monthly_goals(self, month_str):
        # month_str format: "YYYY-MM"
        monthly_map = self.data.setdefault("monthly", {})
        goals = monthly_map.get(month_str, [])
        if isinstance(goals, dict):
            monthly_map[month_str] = []
            self._save_data()
            return []
        if not isinstance(goals, list):
            return []
        return goals

    def add_monthly_goal(
        self,
        month_str,
        content,
        group=None,
        name=None,
        description=None,
        start=None,
        end=None,
    ):
        monthly_map = self.data.setdefault("monthly", {})
        if month_str not in monthly_map or isinstance(monthly_map[month_str], dict):
            monthly_map[month_str] = []

        new_goal = {
            "id": datetime.datetime.now().isoformat(),
            "content": content,
            "done": False,
        }

        if isinstance(group, str) and group.strip():
            new_goal["group"] = group.strip()
        if isinstance(name, str) and name.strip():
            new_goal["name"] = name.strip()
        if isinstance(description, str) and description.strip():
            new_goal["description"] = description.strip()
        if isinstance(start, str) and start.strip():
            new_goal["start"] = start.strip()
        if isinstance(end, str) and end.strip():
            new_goal["end"] = end.strip()

        monthly_map[month_str].append(new_goal)
        self._save_data()

    def toggle_monthly_goal(self, month_str, task_id):
        monthly_map = self.data.get("monthly", {})
        if month_str in monthly_map:
            for goal in monthly_map[month_str]:
                if goal.get("id") == task_id:
                    goal["done"] = not bool(goal.get("done"))
                    self._save_data()
                    return

    def delete_monthly_goal(self, month_str, task_id):
        monthly_map = self.data.get("monthly", {})
        if month_str in monthly_map:
            monthly_map[month_str] = [goal for goal in monthly_map[month_str] if goal.get("id") != task_id]
            self._save_data()

    # --- Memo Operations ---
    def get_memo(self):
        return self.data.get("memo", "")

    def update_memo(self, text):
        self.data["memo"] = text
        self._save_data()

    # --- Dashboard Stats ---
    def get_completion_rate(self, date_str):
        tasks = self.get_daily_tasks(date_str)
        if not tasks:
            return 0.0
        return sum(1 for task in tasks if task.get("done")) / len(tasks)

    def get_weekly_completion_rate(self, week_str):
        week_data = self.get_weekly_tasks(week_str)
        total_tasks = 0
        done_tasks = 0
        for tasks in week_data.values():
            total_tasks += len(tasks)
            done_tasks += sum(1 for task in tasks if task.get("done"))

        if total_tasks == 0:
            return 0.0
        return done_tasks / total_tasks

    def get_monthly_completion_rate(self, month_str):
        goals = self.get_monthly_goals(month_str)
        if not goals:
            return 0.0
        return sum(1 for goal in goals if goal.get("done")) / len(goals)

    def get_tasks(self):
        tasks = []
        for day_tasks in self.data.get("daily", {}).values():
            if isinstance(day_tasks, list):
                tasks.extend(day_tasks)
        return tasks

    # --- Timetable Operations ---
    def get_timetable_entries(self):
        entries = self.data.get("timetable_entries", [])
        if not isinstance(entries, list):
            return []
        return sorted(
            entries,
            key=lambda item: (
                self.VALID_TIMETABLE_DAYS.index(item.get("day", "월")) if item.get("day", "월") in self.VALID_TIMETABLE_DAYS else 99,
                int(item.get("start_period", 0)),
                int(item.get("end_period", 0)),
                item.get("subject", ""),
            ),
        )

    def get_subject_colors(self):
        colors = self.data.get("subject_colors", {})
        if not isinstance(colors, dict):
            return {}
        return dict(colors)

    def get_subject_color(self, subject):
        subject_name = str(subject).strip()
        if not subject_name:
            return self.DEFAULT_SUBJECT_COLOR
        return self.get_subject_colors().get(subject_name, self.DEFAULT_SUBJECT_COLOR)

    def add_timetable_entry(self, subject, day, start_period, end_period, color):
        subject_name = str(subject).strip()
        day_name = str(day).strip()

        if not subject_name:
            raise ValueError("과목명을 입력해 주세요.")
        if day_name not in self.VALID_TIMETABLE_DAYS:
            raise ValueError("월~토 중에서 요일을 선택해 주세요.")

        try:
            start = int(start_period)
            end = int(end_period)
        except (TypeError, ValueError):
            raise ValueError("교시는 숫자여야 합니다.")

        if start < self.MIN_PERIOD or end > self.MAX_PERIOD:
            raise ValueError("교시 범위는 0교시~14교시입니다.")
        if start > end:
            raise ValueError("시작 교시는 종료 교시보다 클 수 없습니다.")

        entries = self.data.setdefault("timetable_entries", [])
        if not isinstance(entries, list):
            entries = []
            self.data["timetable_entries"] = entries

        for entry in entries:
            if entry.get("day") != day_name:
                continue

            existing_start = int(entry.get("start_period", -1))
            existing_end = int(entry.get("end_period", -1))
            is_overlap = not (end < existing_start or start > existing_end)
            if is_overlap:
                raise ValueError("선택한 시간대에 이미 다른 과목이 있습니다.")

        subject_colors = self.data.setdefault("subject_colors", {})
        if not isinstance(subject_colors, dict):
            subject_colors = {}
            self.data["subject_colors"] = subject_colors

        if subject_name in subject_colors:
            color_value = subject_colors[subject_name]
        else:
            color_value = self._normalize_hex_color(color)
            subject_colors[subject_name] = color_value

        new_entry = {
            "id": datetime.datetime.now().isoformat(),
            "subject": subject_name,
            "day": day_name,
            "start_period": start,
            "end_period": end,
        }
        entries.append(new_entry)
        self._save_data()
        return dict(new_entry, color=color_value)

    def delete_timetable_entry(self, entry_id):
        entries = self.data.get("timetable_entries", [])
        if not isinstance(entries, list):
            return

        before_count = len(entries)
        self.data["timetable_entries"] = [entry for entry in entries if entry.get("id") != entry_id]
        if len(self.data["timetable_entries"]) != before_count:
            self._save_data()
