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
    timetable_days = ["월", "화", "수", "목", "금", "토"]
    timetable_periods = list(range(0, 15))
    timetable_color_options = [
        ("초록", "#6CAB45"),
        ("노랑", "#F0D169"),
        ("주황", "#EB7F2D"),
        ("하늘", "#76B5E8"),
        ("분홍", "#F18DA3"),
        ("보라", "#A889E6"),
    ]

    def show_snack(message, bgcolor=ft.Colors.BLUE_GREY_800):
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=bgcolor)
        page.snack_bar.open = True

    def format_period_label(period: int):
        if period == 0:
            return "0교시"
        start_hour = 8 + period
        return f"{period}교시\n{start_hour:02d}:00~{start_hour:02d}:50"

    def text_color_for_background(hex_color: str):
        try:
            clean = hex_color.strip().lstrip("#")
            if len(clean) != 6:
                return ft.Colors.BLACK
            red = int(clean[0:2], 16)
            green = int(clean[2:4], 16)
            blue = int(clean[4:6], 16)
            luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255
            return ft.Colors.BLACK if luminance >= 0.62 else ft.Colors.WHITE
        except Exception:
            return ft.Colors.BLACK

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
        elif index == 4:
            build_timetable_view()

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

    # [TIMETABLE VIEW]
    def build_timetable_grid(entries, subject_colors):
        table_border_color = "white24"
        row_height = 74
        left_col_width = 140
        day_col_width = 138

        day_period_map = {day: {} for day in timetable_days}
        for entry in entries:
            day = entry.get("day")
            if day not in day_period_map:
                continue
            start_period = int(entry.get("start_period", 0))
            end_period = int(entry.get("end_period", 0))
            for period in range(start_period, end_period + 1):
                day_period_map[day][period] = entry

        header_cells = [
            ft.Container(
                content=ft.Text("교시(50분)", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                width=left_col_width,
                height=52,
                alignment=ft.alignment.center,
                bgcolor="#2a2a2a",
                border=ft.border.all(1, table_border_color),
            )
        ]
        for day in timetable_days:
            header_cells.append(
                ft.Container(
                    content=ft.Text(day, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    width=day_col_width,
                    height=52,
                    alignment=ft.alignment.center,
                    bgcolor="#2a2a2a",
                    border=ft.border.all(1, table_border_color),
                )
            )

        rows = [ft.Row(header_cells, spacing=0)]

        for period in timetable_periods:
            left_cell = ft.Container(
                content=ft.Text(format_period_label(period), size=12, text_align=ft.TextAlign.CENTER),
                width=left_col_width,
                height=row_height,
                alignment=ft.alignment.center,
                bgcolor="#2a2a2a",
                border=ft.border.all(1, table_border_color),
            )

            day_cells = []
            for day in timetable_days:
                entry = day_period_map[day].get(period)
                if entry:
                    subject = entry.get("subject", "")
                    bg_color = subject_colors.get(subject, db.DEFAULT_SUBJECT_COLOR)
                    is_start_period = int(entry.get("start_period", period)) == period
                    text_value = subject if is_start_period else ""
                    text_color = text_color_for_background(bg_color)
                    content = ft.Text(
                        text_value,
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=text_color,
                        text_align=ft.TextAlign.CENTER,
                    )
                else:
                    bg_color = "#202020"
                    content = ft.Text("", size=12)

                day_cells.append(
                    ft.Container(
                        content=content,
                        width=day_col_width,
                        height=row_height,
                        padding=6,
                        alignment=ft.alignment.center,
                        bgcolor=bg_color,
                        border=ft.border.all(1, table_border_color),
                    )
                )

            rows.append(ft.Row([left_cell, *day_cells], spacing=0))

        return ft.Column(rows, spacing=0)

    def build_timetable_view():
        entries = db.get_timetable_entries()
        subject_colors = db.get_subject_colors()

        subject_input = ft.TextField(label="과목명", width=180, dense=True)
        day_dropdown = ft.Dropdown(
            label="요일",
            width=120,
            dense=True,
            value=timetable_days[0],
            options=[ft.dropdown.Option(key=day, text=day) for day in timetable_days],
        )
        period_options = [ft.dropdown.Option(key=str(period), text=f"{period}교시") for period in timetable_periods]
        start_dropdown = ft.Dropdown(label="시작", width=110, dense=True, value="1", options=period_options)
        end_dropdown = ft.Dropdown(label="종료", width=110, dense=True, value="1", options=period_options)
        color_dropdown = ft.Dropdown(
            label="색상",
            width=150,
            dense=True,
            value=timetable_color_options[0][1],
            options=[
                ft.dropdown.Option(key=color_value, text=f"{color_name} ({color_value})")
                for color_name, color_value in timetable_color_options
            ],
        )

        def add_timetable_entry_ui(e):
            subject = (subject_input.value or "").strip()
            if not subject:
                show_snack("과목명을 입력해 주세요.", ft.Colors.RED_300)
                page.update()
                return

            try:
                start_period = int(start_dropdown.value)
                end_period = int(end_dropdown.value)
            except (TypeError, ValueError):
                show_snack("시작/종료 교시를 선택해 주세요.", ft.Colors.RED_300)
                page.update()
                return

            if start_period > end_period:
                show_snack("시작 교시는 종료 교시보다 클 수 없습니다.", ft.Colors.RED_300)
                page.update()
                return

            day_value = day_dropdown.value or timetable_days[0]
            selected_color = color_dropdown.value or timetable_color_options[0][1]
            colors_before = db.get_subject_colors()
            had_existing_color = subject in colors_before
            previous_color = colors_before.get(subject, "").upper()

            try:
                db.add_timetable_entry(subject, day_value, start_period, end_period, selected_color)
            except ValueError as exc:
                show_snack(str(exc), ft.Colors.RED_300)
                page.update()
                return

            subject_input.value = ""
            build_timetable_view()

            if had_existing_color and previous_color and previous_color != selected_color.upper():
                show_snack("같은 과목은 기존 색상을 자동으로 사용했습니다.", ft.Colors.BLUE_300)
            else:
                show_snack("시간표에 과목을 추가했습니다.", ft.Colors.GREEN_300)
            page.update()

        def delete_timetable_entry_ui(e, entry_id):
            db.delete_timetable_entry(entry_id)
            build_timetable_view()
            show_snack("시간표에서 과목을 삭제했습니다.", ft.Colors.BLUE_300)
            page.update()

        legend_controls = []
        for subject_name in sorted(subject_colors):
            color_value = subject_colors[subject_name]
            legend_controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(width=14, height=14, bgcolor=color_value, border_radius=3),
                            ft.Text(subject_name, size=12),
                        ],
                        spacing=8,
                    ),
                    padding=6,
                    bgcolor="#1c1c1c",
                    border_radius=8,
                )
            )

        timetable_grid = build_timetable_grid(entries, subject_colors)

        entry_list_controls = []
        if entries:
            for entry in entries:
                subject = entry["subject"]
                day = entry["day"]
                start_period = entry["start_period"]
                end_period = entry["end_period"]
                color_value = subject_colors.get(subject, db.DEFAULT_SUBJECT_COLOR)
                entry_list_controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(width=12, height=12, bgcolor=color_value, border_radius=2),
                                ft.Text(f"{subject} | {day} {start_period}~{end_period}교시", expand=True),
                                ft.IconButton(
                                    ft.Icons.DELETE_OUTLINE,
                                    icon_size=18,
                                    icon_color=ft.Colors.RED_300,
                                    on_click=lambda e, entry_id=entry["id"]: delete_timetable_entry_ui(e, entry_id),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=10,
                        bgcolor="#26ffffff",
                        border_radius=8,
                    )
                )
        else:
            entry_list_controls.append(ft.Text("등록된 시간표 과목이 없습니다.", color="white70"))

        page_content.controls.clear()
        page_content.controls.append(
            ft.Column(
                [
                    ft.Text("시간표", size=24, weight="bold"),
                    ft.Text("0교시는 시간 없이 표시됩니다. 1교시부터 09:00~09:50 형식으로 표기합니다.", size=12, color="white70"),
                    ft.Row(
                        [
                            subject_input,
                            day_dropdown,
                            start_dropdown,
                            end_dropdown,
                            color_dropdown,
                            ft.ElevatedButton("추가", icon=ft.Icons.ADD, on_click=add_timetable_entry_ui),
                        ],
                        spacing=8,
                        wrap=True,
                    ),
                    ft.Text("과목 색상", size=14, weight="bold"),
                    ft.Row(legend_controls, wrap=True, spacing=8) if legend_controls else ft.Text("등록된 과목 색상이 없습니다.", size=12, color="white70"),
                    ft.Container(height=6),
                    ft.Row([timetable_grid], scroll=ft.ScrollMode.AUTO),
                    ft.Divider(color="white24"),
                    ft.Text("등록된 과목", size=16, weight="bold"),
                    ft.Column(entry_list_controls, spacing=8),
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            )
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
                ft.NavigationBarDestination(icon=ft.Icons.TABLE_CHART, label="시간표"),
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
                ft.NavigationRailDestination(icon=ft.Icons.TABLE_CHART, label="시간표"),
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
