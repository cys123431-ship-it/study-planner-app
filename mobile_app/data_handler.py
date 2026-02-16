import datetime
import json
import os
import shutil

DATA_FILE = "schedule_data.json"


class DataHandler:
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
        }

    def _default_week(self):
        return {day: [] for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}

    def _normalize_data(self, raw):
        default = self._default_data()
        if not isinstance(raw, dict):
            return default

        daily = raw.get("daily")
        weekly = raw.get("weekly")
        monthly = raw.get("monthly")
        memo = raw.get("memo")

        default["daily"] = daily if isinstance(daily, dict) else {}
        default["weekly"] = weekly if isinstance(weekly, dict) else {}
        default["monthly"] = monthly if isinstance(monthly, dict) else {}
        default["memo"] = memo if isinstance(memo, str) else ""
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

    def add_monthly_goal(self, month_str, content):
        monthly_map = self.data.setdefault("monthly", {})
        if month_str not in monthly_map or isinstance(monthly_map[month_str], dict):
            monthly_map[month_str] = []

        new_goal = {
            "id": datetime.datetime.now().isoformat(),
            "content": content,
            "done": False,
        }
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
