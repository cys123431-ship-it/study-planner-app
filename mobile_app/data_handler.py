import json
import os
import datetime

DATA_FILE = "schedule_data.json"

class DataHandler:
    def __init__(self):
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                return self._default_data()
        return self._default_data()

    def _default_data(self):
        return {
            "daily": {},  # Format: "YYYY-MM-DD": [{"id": ..., "content": ..., "done": ..., "category": "todo"}]
            "weekly": {}, # Format: "YYYY-W##": {"Monday": [], ...}
            "monthly": {}, # Format: "YYYY-MM": []
            "memo": ""
        }

    def _save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")

    # --- Daily Operations ---
    def get_daily_tasks(self, date_str):
        # date_str format: "YYYY-MM-DD"
        return self.data["daily"].get(date_str, [])

    def add_daily_task(self, date_str, content, category="todo"):
        if date_str not in self.data["daily"]:
            self.data["daily"][date_str] = []
        
        new_task = {
            "id": datetime.datetime.now().isoformat(),
            "content": content,
            "done": False,
            "category": category
        }
        self.data["daily"][date_str].append(new_task)
        self._save_data()

    def toggle_daily_task(self, date_str, task_id):
        if date_str in self.data["daily"]:
            for task in self.data["daily"][date_str]:
                if task["id"] == task_id:
                    task["done"] = not task["done"]
                    self._save_data()
                    return

    def delete_daily_task(self, date_str, task_id):
        if date_str in self.data["daily"]:
             self.data["daily"][date_str] = [t for t in self.data["daily"][date_str] if t["id"] != task_id]
             self._save_data()

    # --- Weekly Operations ---
    def get_weekly_tasks(self, week_str):
        # week_str format: "YYYY-W##"
        return self.data["weekly"].get(week_str, {day: [] for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]})

    def add_weekly_task(self, week_str, day, content):
        if week_str not in self.data["weekly"]:
            self.data["weekly"][week_str] = {d: [] for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
        
        new_task = {
            "id": datetime.datetime.now().isoformat(),
            "content": content,
            "done": False
        }
        self.data["weekly"][week_str][day].append(new_task)
        self._save_data()

    def delete_weekly_task(self, week_str, day, task_id):
        if week_str in self.data["weekly"] and day in self.data["weekly"][week_str]:
            self.data["weekly"][week_str][day] = [t for t in self.data["weekly"][week_str][day] if t["id"] != task_id]
            self._save_data()
            
    def toggle_weekly_task(self, week_str, day, task_id):
        if week_str in self.data["weekly"] and day in self.data["weekly"][week_str]:
            for t in self.data["weekly"][week_str][day]:
                 if t["id"] == task_id:
                     t["done"] = not t["done"]
                     self._save_data()
                     return

    # --- Monthly Operations (Goal Oriented) ---
    def get_monthly_goals(self, month_str):
        # month_str format: "YYYY-MM"
        data = self.data["monthly"].get(month_str, [])
        if isinstance(data, dict):
            # Migration: Old schema found. Reset or return empty.
            # decided to reset to empty list to avoid crash.
            self.data["monthly"][month_str] = []
            self._save_data()
            return []
        return data

    def add_monthly_goal(self, month_str, content):
        if month_str not in self.data["monthly"] or isinstance(self.data["monthly"][month_str], dict):
            self.data["monthly"][month_str] = []

        new_goal = {
            "id": datetime.datetime.now().isoformat(),
            "content": content,
            "done": False
        }
        self.data["monthly"][month_str].append(new_goal)
        self._save_data()

    def toggle_monthly_goal(self, month_str, task_id):
        if month_str in self.data["monthly"]:
            for goal in self.data["monthly"][month_str]:
                if goal["id"] == task_id:
                    goal["done"] = not goal["done"]
                    self._save_data()
                    return

    def delete_monthly_goal(self, month_str, task_id):
        if month_str in self.data["monthly"]:
             self.data["monthly"][month_str] = [g for g in self.data["monthly"][month_str] if g["id"] != task_id]
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
        if not tasks: return 0.0
        return sum(1 for t in tasks if t["done"]) / len(tasks)
        
    def get_weekly_completion_rate(self, week_str):
        week_data = self.data["weekly"].get(week_str, {})
        total_tasks = 0
        done_tasks = 0
        for day, tasks in week_data.items():
            total_tasks += len(tasks)
            done_tasks += sum(1 for t in tasks if t["done"])
        
        if total_tasks == 0: return 0.0
        return done_tasks / total_tasks

    def get_monthly_completion_rate(self, month_str):
        goals = self.get_monthly_goals(month_str)
        if not goals: return 0.0
        return sum(1 for g in goals if g["done"]) / len(goals)

    def get_tasks(self):
        return self.data["tasks"]
