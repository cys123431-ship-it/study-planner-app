import flet as ft
from data_handler import DataHandler
import traceback

try:
    from date_utils import to_date_str, to_iso_week_str, to_month_str
except Exception:
    import datetime as _dt

    def to_date_str(value=None):
        target = value or _dt.date.today()
        return target.strftime("%Y-%m-%d")

    def to_month_str(value=None):
        target = value or _dt.date.today()
        return target.strftime("%Y-%m")

    def to_iso_week_str(value=None):
        target = value or _dt.date.today()
        iso_year, iso_week, _ = target.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"


def _build_app(page: ft.Page):
    # --- 1. Page Configuration ---
    page.title = "Glass Planner"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = ft.Colors.BLACK

    platform_name = str(getattr(page, "platform", "")).lower()
    is_mobile = ("android" in platform_name) or ("ios" in platform_name)

    # Desktop-only window sizing. Mobile platforms may throw or ignore these properties.
    if not is_mobile:
        try:
            if getattr(page, "window", None) is not None:
                page.window.width = 450
                page.window.height = 850
            else:
                page.window_width = 450
                page.window_height = 850
        except Exception:
            pass

    db = DataHandler()

    # --- 2. State & Functions ---
    def show_view(index: int):
        page_content.controls.clear()
        if index == 0:
            build_daily_view()
        elif index == 1:
            build_weekly_view()
        elif index == 2:
            build_monthly_view()
        elif index == 3:
            build_dashboard_view()

    def on_nav_change(e):
        show_view(e.control.selected_index)
        page.update()

    def add_daily_todo(e):
        if not todo_input.value: return
        db.add_daily_task(to_date_str(), todo_input.value, "todo")
        todo_input.value = ""
        refresh_daily_list()
        page.update()

    def toggle_daily(e, task_id):
        db.toggle_daily_task(to_date_str(), task_id)
        refresh_daily_list()
        page.update()

    # --- 3. View Builders ---
    
    # [DAILY VIEW]
    todo_list = ft.Column(spacing=5)
    todo_input = ft.TextField(hint_text="Add task...", expand=True, on_submit=add_daily_todo, height=40, text_size=14, content_padding=10)
    
    def delete_daily(e, task_id):
        db.delete_daily_task(to_date_str(), task_id)
        refresh_daily_list()
        page.update()

    def refresh_daily_list():
        todo_list.controls.clear()
        tasks = db.get_daily_tasks(to_date_str())
        for t in tasks:
            if t.get("category") == "todo":
                todo_list.controls.append(
                    ft.Row([
                        ft.Checkbox(label=t["content"], value=t["done"], 
                                    on_change=lambda e, tid=t["id"]: toggle_daily(e, tid)),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red400", icon_size=20,
                                      on_click=lambda e, tid=t["id"]: delete_daily(e, tid))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )

    def build_daily_view():
        refresh_daily_list()
        page_content.controls.append(
            ft.Column([
                ft.Text("DAILY PLANNER", size=24, weight="bold", font_family="Verdana"),
                ft.Text(to_date_str(), size=16, color="white70"),
                ft.Divider(color="white24"),
                
                ft.Row([
                    ft.Column([
                        ft.Text("TO DO LIST", weight="bold"),
                        ft.Row([todo_input, ft.IconButton(ft.Icons.ADD, on_click=add_daily_todo)]),
                        todo_list
                    ], expand=1),
                    
                    ft.Column([
                        ft.Text("MEMO", weight="bold"),
                        ft.Container(
                            content=ft.TextField(
                                multiline=True, 
                                min_lines=5, 
                                border_color="transparent", 
                                value=db.get_memo(),
                                on_change=lambda e: db.update_memo(e.control.value)
                            ),
                            bgcolor="#26ffffff", border_radius=10, padding=10
                        )
                    ], expand=1)
                ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START)
            ], expand=True, scroll="auto")
        )

    # [WEEKLY VIEW]
    def add_weekly_item(e, day, input_field):
        if not input_field.value: return
        week_str = to_iso_week_str()
        db.add_weekly_task(week_str, day, input_field.value)
        input_field.value = ""
        build_weekly_view()
        page.update()

    def delete_weekly_item(e, day, task_id):
        week_str = to_iso_week_str()
        db.delete_weekly_task(week_str, day, task_id)
        build_weekly_view()
        page.update()
    
    def toggle_weekly_item(e, day, task_id):
        week_str = to_iso_week_str()
        db.toggle_weekly_task(week_str, day, task_id)
        # No full rebuild needed, just toggle state technically, but rebuild ensures consistency
        build_weekly_view()
        page.update()

    def build_weekly_view():
        week_str = to_iso_week_str()
        tasks_map = db.get_weekly_tasks(week_str)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        weekly_col = ft.Column(spacing=15, scroll="auto", expand=True)
        
        for day in days:
            day_tasks = tasks_map.get(day, [])
            task_rows = []
            for t in day_tasks:
                task_rows.append(
                    ft.Row([
                        # Checkbox for Completion
                        ft.Checkbox(label=t['content'], value=t['done'],
                                    on_change=lambda e, d=day, tid=t["id"]: toggle_weekly_item(e, d, tid)),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color="red200", 
                                      on_click=lambda e, d=day, tid=t["id"]: delete_weekly_item(e, d, tid))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            
            d_input = ft.TextField(hint_text="Add...", height=30, text_size=12, content_padding=5, expand=True)
            d_input.on_submit = lambda e, d=day, inp=d_input: add_weekly_item(e, d, inp)
            
            weekly_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text(day, weight="bold", color="cyan"), d_input, 
                                ft.IconButton(ft.Icons.ADD, icon_size=20, on_click=lambda e, d=day, inp=d_input: add_weekly_item(e, d, inp))]),
                        ft.Column(task_rows, spacing=2)
                    ]),
                    bgcolor="#26ffffff", padding=10, border_radius=10
                )
            )
            
        page_content.controls.clear()
        page_content.controls.append(ft.Column([
            ft.Text("WEEKLY PLANNER", size=24, weight="bold"),
            weekly_col
        ], expand=True))

    # [MONTHLY VIEW]
    def add_monthly_goal_ui(e):
        if not monthly_input.value: return
        db.add_monthly_goal(to_month_str(), monthly_input.value)
        monthly_input.value = ""
        build_monthly_view()
        page.update()

    def delete_monthly_goal_ui(e, goal_id):
        db.delete_monthly_goal(to_month_str(), goal_id)
        build_monthly_view()
        page.update()

    def toggle_monthly_goal_ui(e, goal_id):
        db.toggle_monthly_goal(to_month_str(), goal_id)
        build_monthly_view()
        page.update()

    monthly_input = ft.TextField(hint_text="Add Monthly Goal...", expand=True, on_submit=add_monthly_goal_ui)

    def build_monthly_view():
        goals = db.get_monthly_goals(to_month_str())
        goal_list = ft.Column(spacing=10)
        
        for g in goals:
            goal_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Checkbox(label=g["content"], value=g["done"], 
                                    on_change=lambda e, gid=g["id"]: toggle_monthly_goal_ui(e, gid)),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=20, icon_color="red400",
                                      on_click=lambda e, gid=g["id"]: delete_monthly_goal_ui(e, gid))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="#26ffffff", padding=10, border_radius=10
                )
            )

        page_content.controls.clear()
        page_content.controls.append(
             ft.Column([
                 ft.Text("MONTHLY PLANNER", size=24, weight="bold"),
                 ft.Row([monthly_input, ft.IconButton(ft.Icons.ADD, on_click=add_monthly_goal_ui)]),
                 goal_list
             ], expand=True, scroll="auto")
        )

    # [DASHBOARD VIEW]
    def build_dashboard_view():
        # Calculate Rates
        daily_rate = db.get_completion_rate(to_date_str())
        weekly_rate = db.get_weekly_completion_rate(to_iso_week_str())
        monthly_rate = db.get_monthly_completion_rate(to_month_str())
        
        page_content.controls.clear()
        page_content.controls.append(
            ft.Column([
                ft.Text("DASHBOARD", size=24, weight="bold"),
                ft.Divider(),
                
                # Daily Stats
                ft.Text("Daily Achievement", size=16),
                ft.ProgressBar(value=daily_rate, color="cyan", bgcolor="white24", height=20),
                ft.Text(f"{int(daily_rate*100)}%", size=14, text_align="right"),
                ft.Container(height=20),
                
                # Weekly Stats
                ft.Text("Weekly Achievement", size=16),
                ft.ProgressBar(value=weekly_rate, color="teal", bgcolor="white24", height=20),
                ft.Text(f"{int(weekly_rate*100)}%", size=14, text_align="right"),
                ft.Container(height=20),
                
                # Monthly Stats
                ft.Text("Monthly Achievement", size=16),
                ft.ProgressBar(value=monthly_rate, color="blue", bgcolor="white24", height=20),
                ft.Text(f"{int(monthly_rate*100)}%", size=14, text_align="right"),
                
            ], expand=True)
        )

    # --- 4. Main Layout Composition ---
    page_content = ft.Column(expand=True)  # Changed from Container to Column

    # Initialize with Daily View
    build_daily_view()

    if is_mobile:
        page.navigation_bar = ft.NavigationBar(
            selected_index=0,
            on_change=on_nav_change,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.TODAY, label="Daily"),
                ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_VIEW_WEEK, label="Weekly"),
                ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH, label="Monthly"),
                ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label="Stats"),
            ],
        )
        foreground = page_content
    else:
        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=70,
            min_extended_width=150,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.TODAY, label="Daily"),
                ft.NavigationRailDestination(icon=ft.Icons.CALENDAR_VIEW_WEEK, label="Weekly"),
                ft.NavigationRailDestination(icon=ft.Icons.CALENDAR_MONTH, label="Monthly"),
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Stats"),
            ],
            on_change=on_nav_change,
            bgcolor="#1a000000",
        )
        foreground = ft.Row(
            [
                nav_rail,
                ft.VerticalDivider(width=1, color="white24"),
                page_content,
            ],
            expand=True,
        )

    page.add(
        ft.Stack(
            [
                # Background
                ft.Image(
                    src="assets/background.png",
                    expand=True,
                    fit="cover",
                    opacity=0.8
                ),
                # Glass Gradient
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        colors=["#99000000", "#cc000000"],
                        begin=ft.alignment.Alignment(-1, -1),
                    ),
                ),
                # Foreground content
                foreground,
            ],
            expand=True
        )
    )


def main(page: ft.Page):
    try:
        _build_app(page)
    except Exception:
        error_text = traceback.format_exc()
        try:
            page.clean()
            page.padding = 16
            page.bgcolor = ft.Colors.BLACK
            page.add(
                ft.Text("앱 시작 오류", color=ft.Colors.RED_300, size=22, weight=ft.FontWeight.BOLD),
                ft.Text(error_text, color=ft.Colors.WHITE70, selectable=True, size=12),
            )
            page.update()
        except Exception:
            pass

        try:
            with open("app_error.log", "w", encoding="utf-8") as f:
                f.write(error_text)
        except Exception:
            pass


ft.app(target=main, assets_dir="assets")
