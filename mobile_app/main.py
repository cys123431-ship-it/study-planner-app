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


BG_APP = "#F6F7FC"
SURFACE = "#FFFFFF"
SURFACE_SOFT = "#F3F2FF"
BORDER = "#E7E9F3"
TEXT_PRIMARY = "#1E2030"
TEXT_SECONDARY = "#7C8198"
PRIMARY_PURPLE = "#5B3CFF"
PRIMARY_PURPLE_DARK = "#4B2FE0"
SUCCESS_GREEN = "#17B26A"
INFO_BLUE = "#4E8CFF"
WARNING_ORANGE = "#FF8A4C"


def _build_app(page: ft.Page):
    page.title = "Task Management"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = BG_APP

    platform_name = str(getattr(page, "platform", "")).lower()
    is_mobile = ("android" in platform_name) or ("ios" in platform_name)

    if not is_mobile:
        try:
            if getattr(page, "window", None) is not None:
                page.window.width = 460
                page.window.height = 900
            else:
                page.window_width = 460
                page.window_height = 900
        except Exception:
            pass

    db = DataHandler()
    timetable_days = ["월", "화", "수", "목", "금", "토"]
    timetable_periods = list(range(0, 15))
    timetable_color_options = [
        ("보라", "#5B3CFF"),
        ("노랑", "#F0D169"),
        ("주황", "#EB7F2D"),
        ("초록", "#6CAB45"),
        ("하늘", "#76B5E8"),
        ("핑크", "#F18DA3"),
    ]

    current_view_index = 0
    today_filter = "All"
    project_form_state = {
        "group": "Work",
        "name": "",
        "description": "",
        "start": to_date_str(),
        "end": to_date_str(),
    }

    desktop_nav = None
    page_content = ft.Column(expand=True)

    def show_snack(message: str, bgcolor: str = PRIMARY_PURPLE):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF"),
            bgcolor=bgcolor,
            duration=1800,
        )
        page.snack_bar.open = True

    def card(content, padding=14, bgcolor=SURFACE, radius=18, height=None, expand=False):
        return ft.Container(
            content=content,
            padding=padding,
            bgcolor=bgcolor,
            border_radius=radius,
            border=ft.border.all(1, BORDER),
            shadow=[
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=16,
                    color="#120E1B57",
                    offset=ft.Offset(0, 6),
                )
            ],
            height=height,
            expand=expand,
        )

    def primary_button(label, on_click, icon=None, width=None):
        return ft.ElevatedButton(
            label,
            icon=icon,
            on_click=on_click,
            width=width,
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: PRIMARY_PURPLE,
                    ft.ControlState.HOVERED: PRIMARY_PURPLE_DARK,
                },
                color={ft.ControlState.DEFAULT: "#FFFFFF"},
                shape=ft.RoundedRectangleBorder(radius=14),
                elevation={ft.ControlState.DEFAULT: 0},
                padding={ft.ControlState.DEFAULT: ft.Padding(16, 12, 16, 12)},
            ),
        )

    def chip_button(label, selected, on_click):
        return ft.TextButton(
            label,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: PRIMARY_PURPLE if selected else SURFACE_SOFT},
                color={ft.ControlState.DEFAULT: "#FFFFFF" if selected else TEXT_SECONDARY},
                shape=ft.RoundedRectangleBorder(radius=12),
                padding={ft.ControlState.DEFAULT: ft.Padding(12, 8, 12, 8)},
            ),
        )

    def format_period_label(period: int):
        if period == 0:
            return "0교시"
        start_hour = 8 + period
        return f"{period}교시\n{start_hour:02d}:00~{start_hour:02d}:50"

    def text_color_for_background(hex_color: str):
        try:
            clean = hex_color.strip().lstrip("#")
            if len(clean) != 6:
                return TEXT_PRIMARY
            red = int(clean[0:2], 16)
            green = int(clean[2:4], 16)
            blue = int(clean[4:6], 16)
            luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255
            return TEXT_PRIMARY if luminance >= 0.62 else "#FFFFFF"
        except Exception:
            return TEXT_PRIMARY

    def _today_tasks():
        return [t for t in db.get_daily_tasks(to_date_str()) if t.get("category") == "todo"]

    def _weekly_flat_tasks():
        week_tasks = db.get_weekly_tasks(to_iso_week_str())
        rows = []
        for day, tasks in week_tasks.items():
            for task in tasks:
                rows.append((day, task))
        return rows

    def build_home_view():
        tasks = _today_tasks()
        done_count = sum(1 for task in tasks if task.get("done"))
        total_count = len(tasks)
        progress_value = (done_count / total_count) if total_count else 0

        weekly_rows = _weekly_flat_tasks()
        in_progress = [(day, task) for day, task in weekly_rows if not task.get("done")][:3]

        monthly_goals = db.get_monthly_goals(to_month_str())
        goal_total = len(monthly_goals)

        hero = card(
            ft.Column(
                [
                    ft.Text("오늘의 진행 상황", color="#DDD5FF", size=12),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Task Focus", color="#FFFFFF", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        f"완료 {done_count} / {total_count if total_count else 0}",
                                        color="#ECE8FF",
                                        size=13,
                                    ),
                                    ft.Container(height=8),
                                    primary_button("View Today", lambda e: jump_to(1), icon=ft.Icons.ARROW_FORWARD, width=130),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.ProgressRing(
                                value=progress_value,
                                color="#FFFFFF",
                                bgcolor="#8B76FF",
                                stroke_width=7,
                                width=74,
                                height=74,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=PRIMARY_PURPLE,
            radius=20,
        )

        in_progress_cards = []
        if in_progress:
            for day, task in in_progress:
                in_progress_cards.append(
                    card(
                        ft.Column(
                            [
                                ft.Text(day, color=TEXT_SECONDARY, size=11),
                                ft.Text(task.get("content", ""), size=13, weight=ft.FontWeight.W_600, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Container(height=6),
                                ft.Container(height=4, bgcolor=SURFACE_SOFT, border_radius=6),
                            ],
                            spacing=2,
                        ),
                        bgcolor="#FFFFFF",
                    )
                )
        else:
            in_progress_cards.append(card(ft.Text("이번 주 진행 중인 작업이 없습니다.", color=TEXT_SECONDARY)))

        task_groups = [
            ("Office Project", len([r for r in weekly_rows if r[0] in ["Mon", "Tue", "Wed"]])),
            ("Personal Project", len([r for r in weekly_rows if r[0] in ["Thu", "Fri", "Sat", "Sun"]])),
            ("Monthly Goals", goal_total),
        ]

        group_cards = []
        for label, count in task_groups:
            group_cards.append(
                card(
                    ft.Row(
                        [
                            ft.Text(label, size=14, weight=ft.FontWeight.W_600),
                            ft.Container(
                                content=ft.Text(f"{count}", size=12, color=PRIMARY_PURPLE, weight=ft.FontWeight.BOLD),
                                bgcolor=SURFACE_SOFT,
                                border_radius=10,
                                padding=ft.Padding(10, 4, 10, 4),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=12,
                )
            )

        page_content.controls.clear()
        page_content.controls.append(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.CircleAvatar(content=ft.Text("L", color="#FFFFFF"), bgcolor=PRIMARY_PURPLE, radius=18),
                                    ft.Column(
                                        [
                                            ft.Text("Hello!", size=11, color=TEXT_SECONDARY),
                                            ft.Text("Livia Vaccaro", size=18, weight=ft.FontWeight.BOLD),
                                        ],
                                        spacing=1,
                                    ),
                                ],
                                spacing=10,
                            ),
                            ft.Icon(ft.Icons.NOTIFICATIONS_NONE, color=TEXT_SECONDARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    hero,
                    ft.Row([ft.Text("In Progress", size=18, weight=ft.FontWeight.BOLD), ft.Text("•", color=PRIMARY_PURPLE)], spacing=6),
                    ft.Column(in_progress_cards, spacing=10),
                    ft.Row([ft.Text("Task Groups", size=18, weight=ft.FontWeight.BOLD), ft.Text("4", color=PRIMARY_PURPLE)], spacing=6),
                    ft.Column(group_cards, spacing=10),
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=14,
            )
        )

    def build_today_view():
        nonlocal today_filter
        today_str = to_date_str()
        tasks = _today_tasks()

        if today_filter == "To do":
            visible_tasks = [task for task in tasks if not task.get("done")]
        elif today_filter == "Done":
            visible_tasks = [task for task in tasks if task.get("done")]
        else:
            visible_tasks = tasks

        def add_today_task(e):
            content = (task_input.value or "").strip()
            if not content:
                show_snack("할 일을 입력해 주세요.", "#D14343")
                page.update()
                return
            db.add_daily_task(today_str, content, "todo")
            task_input.value = ""
            build_today_view()
            page.update()

        def toggle_today_task(e, task_id):
            db.toggle_daily_task(today_str, task_id)
            build_today_view()
            page.update()

        def delete_today_task(e, task_id):
            db.delete_daily_task(today_str, task_id)
            build_today_view()
            page.update()

        def set_filter(value):
            nonlocal today_filter
            today_filter = value
            build_today_view()
            page.update()

        task_input = ft.TextField(
            hint_text="오늘 할 일 추가",
            expand=True,
            dense=True,
            border_radius=12,
            filled=True,
            bgcolor=SURFACE_SOFT,
            border_color="transparent",
            on_submit=add_today_task,
        )

        date_strip_items = []
        import datetime as _dt

        today_date = _dt.date.fromisoformat(today_str)
        for offset in range(-2, 3):
            target = today_date + _dt.timedelta(days=offset)
            selected = offset == 0
            date_strip_items.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(target.strftime("%d"), size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF" if selected else TEXT_PRIMARY),
                            ft.Text(target.strftime("%a"), size=11, color="#EFEAFF" if selected else TEXT_SECONDARY),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                    ),
                    width=54,
                    height=74,
                    bgcolor=PRIMARY_PURPLE if selected else SURFACE,
                    border=ft.border.all(1, "transparent" if selected else BORDER),
                    border_radius=14,
                    alignment=ft.Alignment(0, 0),
                )
            )

        task_cards = []
        if visible_tasks:
            for task in visible_tasks:
                done = bool(task.get("done"))
                badge_text = "Done" if done else "To do"
                badge_bg = "#E8F8EF" if done else "#EAF0FF"
                badge_color = SUCCESS_GREEN if done else INFO_BLUE
                task_cards.append(
                    card(
                        ft.Row(
                            [
                                ft.Checkbox(
                                    label=task.get("content", ""),
                                    value=done,
                                    check_color="#FFFFFF",
                                    active_color=PRIMARY_PURPLE,
                                    on_change=lambda e, task_id=task.get("id"): toggle_today_task(e, task_id),
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(badge_text, size=11, color=badge_color),
                                    bgcolor=badge_bg,
                                    border_radius=10,
                                    padding=ft.Padding(8, 4, 8, 4),
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE_OUTLINE,
                                    icon_size=18,
                                    icon_color="#B84D4D",
                                    on_click=lambda e, task_id=task.get("id"): delete_today_task(e, task_id),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=8,
                    )
                )
        else:
            task_cards.append(card(ft.Text("표시할 작업이 없습니다.", color=TEXT_SECONDARY)))

        page_content.controls.clear()
        page_content.controls.append(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(ft.Icons.ARROW_BACK, icon_color=TEXT_PRIMARY, on_click=lambda e: jump_to(0)),
                            ft.Text("Today’s Tasks", size=22, weight=ft.FontWeight.BOLD),
                            ft.Icon(ft.Icons.NOTIFICATIONS_NONE, color=TEXT_SECONDARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(date_strip_items, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row(
                        [
                            chip_button("All", today_filter == "All", lambda e: set_filter("All")),
                            chip_button("To do", today_filter == "To do", lambda e: set_filter("To do")),
                            chip_button("Done", today_filter == "Done", lambda e: set_filter("Done")),
                        ],
                        spacing=8,
                    ),
                    card(
                        ft.Row(
                            [
                                task_input,
                                primary_button("+", add_today_task),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=10,
                    ),
                    ft.Column(task_cards, spacing=10),
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
            )
        )

    def build_add_project_view():
        def update_group(e):
            project_form_state["group"] = e.control.value or "Work"

        def update_name(e):
            project_form_state["name"] = e.control.value or ""

        def update_description(e):
            project_form_state["description"] = e.control.value or ""

        def update_start(e):
            project_form_state["start"] = e.control.value or to_date_str()

        def update_end(e):
            project_form_state["end"] = e.control.value or to_date_str()

        def submit_project(e):
            name = (project_form_state.get("name") or "").strip()
            if not name:
                show_snack("프로젝트 이름을 입력해 주세요.", "#D14343")
                page.update()
                return

            group = project_form_state.get("group") or "Work"
            db.add_monthly_goal(to_month_str(), f"[{group}] {name}")
            project_form_state["name"] = ""
            project_form_state["description"] = ""
            build_add_project_view()
            show_snack("프로젝트가 추가되었습니다.", SUCCESS_GREEN)
            page.update()

        group_dropdown = ft.Dropdown(
            label="Task Group",
            value=project_form_state.get("group", "Work"),
            options=[ft.dropdown.Option("Work"), ft.dropdown.Option("Study"), ft.dropdown.Option("Personal")],
            on_change=update_group,
            filled=True,
            bgcolor=SURFACE_SOFT,
            border_color="transparent",
            border_radius=12,
        )

        name_input = ft.TextField(
            label="Project Name",
            value=project_form_state.get("name", ""),
            on_change=update_name,
            filled=True,
            bgcolor=SURFACE_SOFT,
            border_color="transparent",
            border_radius=12,
        )

        description_input = ft.TextField(
            label="Description",
            value=project_form_state.get("description", ""),
            on_change=update_description,
            multiline=True,
            min_lines=4,
            max_lines=4,
            filled=True,
            bgcolor=SURFACE_SOFT,
            border_color="transparent",
            border_radius=12,
        )

        start_input = ft.TextField(
            label="Start Date",
            value=project_form_state.get("start", to_date_str()),
            on_change=update_start,
            filled=True,
            bgcolor=SURFACE_SOFT,
            border_color="transparent",
            border_radius=12,
        )

        end_input = ft.TextField(
            label="End Date",
            value=project_form_state.get("end", to_date_str()),
            on_change=update_end,
            filled=True,
            bgcolor=SURFACE_SOFT,
            border_color="transparent",
            border_radius=12,
        )

        preview_name = project_form_state.get("name") or "(project name)"
        preview_group = project_form_state.get("group") or "Work"

        page_content.controls.clear()
        page_content.controls.append(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(ft.Icons.ARROW_BACK, icon_color=TEXT_PRIMARY, on_click=lambda e: jump_to(0)),
                            ft.Text("Add Project", size=22, weight=ft.FontWeight.BOLD),
                            ft.Icon(ft.Icons.NOTIFICATIONS_NONE, color=TEXT_SECONDARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    card(
                        ft.Column(
                            [
                                group_dropdown,
                                name_input,
                                description_input,
                                ft.Row([start_input, end_input], spacing=10),
                            ],
                            spacing=10,
                        )
                    ),
                    card(
                        ft.Column(
                            [
                                ft.Text("Preview", size=12, color=TEXT_SECONDARY),
                                ft.Text(preview_name, size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(preview_group, size=13, color=PRIMARY_PURPLE),
                            ],
                            spacing=4,
                        ),
                        bgcolor="#FFFFFF",
                    ),
                    primary_button("Add Project", submit_project, icon=ft.Icons.ADD),
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=14,
            )
        )

    def build_timetable_grid(entries, subject_colors):
        row_height = 54
        header_height = 44
        left_col_width = 76

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
                content=ft.Text("교시", size=11, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                width=left_col_width,
                height=header_height,
                alignment=ft.Alignment(0, 0),
                bgcolor="#F0F2FA",
                border=ft.border.all(1, BORDER),
            )
        ]

        for day in timetable_days:
            header_cells.append(
                ft.Container(
                    content=ft.Text(day, size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    expand=True,
                    height=header_height,
                    alignment=ft.Alignment(0, 0),
                    bgcolor="#F0F2FA",
                    border=ft.border.all(1, BORDER),
                )
            )

        rows = [ft.Row(header_cells, spacing=0)]

        for period in timetable_periods:
            left_cell = ft.Container(
                content=ft.Text(format_period_label(period), size=10, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                width=left_col_width,
                height=row_height,
                alignment=ft.Alignment(0, 0),
                bgcolor="#FAFBFF",
                border=ft.border.all(1, BORDER),
            )

            day_cells = []
            for day in timetable_days:
                entry = day_period_map[day].get(period)
                if entry:
                    subject = entry.get("subject", "")
                    bg_color = subject_colors.get(subject, db.DEFAULT_SUBJECT_COLOR)
                    text_color = text_color_for_background(bg_color)
                    show_text = int(entry.get("start_period", period)) == period
                    cell_text = subject if show_text else ""
                    content = ft.Text(
                        cell_text,
                        size=10,
                        color=text_color,
                        weight=ft.FontWeight.W_600,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        text_align=ft.TextAlign.CENTER,
                    )
                else:
                    bg_color = SURFACE
                    content = ft.Text("", size=10)

                day_cells.append(
                    ft.Container(
                        content=content,
                        expand=True,
                        height=row_height,
                        alignment=ft.Alignment(0, 0),
                        border=ft.border.all(1, BORDER),
                        bgcolor=bg_color,
                        padding=4,
                    )
                )

            rows.append(ft.Row([left_cell, *day_cells], spacing=0))

        return ft.Column(rows, spacing=0)

    def build_timetable_view():
        entries = db.get_timetable_entries()
        subject_colors = db.get_subject_colors()

        subject_input = ft.TextField(label="과목명", width=130, dense=True)
        day_dropdown = ft.Dropdown(
            label="요일",
            width=85,
            dense=True,
            value=timetable_days[0],
            options=[ft.dropdown.Option(key=day, text=day) for day in timetable_days],
        )
        start_dropdown = ft.Dropdown(
            label="시작",
            width=90,
            dense=True,
            value="1",
            options=[ft.dropdown.Option(key=str(period), text=f"{period}교시") for period in timetable_periods],
        )
        end_dropdown = ft.Dropdown(
            label="종료",
            width=90,
            dense=True,
            value="1",
            options=[ft.dropdown.Option(key=str(period), text=f"{period}교시") for period in timetable_periods],
        )
        color_dropdown = ft.Dropdown(
            label="색상",
            width=120,
            dense=True,
            value=timetable_color_options[0][1],
            options=[ft.dropdown.Option(key=color, text=name) for name, color in timetable_color_options],
        )

        def add_timetable_entry_ui(e):
            subject = (subject_input.value or "").strip()
            if not subject:
                show_snack("과목명을 입력해 주세요.", "#D14343")
                page.update()
                return

            try:
                start_period = int(start_dropdown.value)
                end_period = int(end_dropdown.value)
            except (TypeError, ValueError):
                show_snack("교시를 다시 선택해 주세요.", "#D14343")
                page.update()
                return

            if start_period > end_period:
                show_snack("시작 교시는 종료 교시보다 클 수 없습니다.", "#D14343")
                page.update()
                return

            day = day_dropdown.value or timetable_days[0]
            selected_color = color_dropdown.value or timetable_color_options[0][1]
            color_map_before = db.get_subject_colors()
            had_color = subject in color_map_before

            try:
                db.add_timetable_entry(subject, day, start_period, end_period, selected_color)
            except ValueError as exc:
                show_snack(str(exc), "#D14343")
                page.update()
                return

            build_timetable_view()
            if had_color and color_map_before.get(subject, "").upper() != selected_color.upper():
                show_snack("같은 과목은 기존 색상을 유지했습니다.", INFO_BLUE)
            else:
                show_snack("시간표에 과목을 추가했습니다.", SUCCESS_GREEN)
            page.update()

        def delete_timetable_entry_ui(e, entry_id):
            db.delete_timetable_entry(entry_id)
            build_timetable_view()
            show_snack("과목을 삭제했습니다.", INFO_BLUE)
            page.update()

        legend = []
        for subject_name in sorted(subject_colors):
            color = subject_colors[subject_name]
            legend.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(width=12, height=12, bgcolor=color, border_radius=3),
                            ft.Text(subject_name, size=11, color=TEXT_PRIMARY),
                        ],
                        spacing=6,
                    ),
                    padding=ft.Padding(8, 6, 8, 6),
                    bgcolor=SURFACE,
                    border=ft.border.all(1, BORDER),
                    border_radius=10,
                )
            )

        timetable_grid = build_timetable_grid(entries, subject_colors)

        entry_rows = []
        for entry in entries:
            subject = entry.get("subject", "")
            day = entry.get("day", "")
            start_period = entry.get("start_period", 0)
            end_period = entry.get("end_period", 0)
            color = subject_colors.get(subject, db.DEFAULT_SUBJECT_COLOR)
            entry_rows.append(
                card(
                    ft.Row(
                        [
                            ft.Container(width=12, height=12, bgcolor=color, border_radius=2),
                            ft.Text(f"{subject} | {day} {start_period}~{end_period}교시", expand=True, size=12),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                icon_size=18,
                                icon_color="#B84D4D",
                                on_click=lambda e, entry_id=entry.get("id"): delete_timetable_entry_ui(e, entry_id),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=8,
                )
            )

        if not entry_rows:
            entry_rows.append(card(ft.Text("등록된 과목이 없습니다.", color=TEXT_SECONDARY)))

        page_content.controls.clear()
        page_content.controls.append(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("시간표", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("0교시는 시간 없음", color=TEXT_SECONDARY, size=11),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    card(
                        ft.Row(
                            [
                                subject_input,
                                day_dropdown,
                                start_dropdown,
                                end_dropdown,
                                color_dropdown,
                                primary_button("추가", add_timetable_entry_ui, icon=ft.Icons.ADD),
                            ],
                            wrap=True,
                            spacing=8,
                        ),
                        padding=10,
                    ),
                    ft.Row(legend, wrap=True, spacing=8) if legend else ft.Text("과목 색상 정보가 없습니다.", color=TEXT_SECONDARY),
                    card(
                        ft.Column(
                            [timetable_grid],
                            spacing=0,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=0,
                    ),
                    ft.Text("등록된 과목", size=16, weight=ft.FontWeight.BOLD),
                    ft.Column(entry_rows, spacing=8),
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
            )
        )

    def build_stats_view():
        daily_rate = db.get_completion_rate(to_date_str())
        weekly_rate = db.get_weekly_completion_rate(to_iso_week_str())
        monthly_rate = db.get_monthly_completion_rate(to_month_str())

        stats_cards = [
            ("Daily", daily_rate, PRIMARY_PURPLE),
            ("Weekly", weekly_rate, INFO_BLUE),
            ("Monthly", monthly_rate, WARNING_ORANGE),
        ]

        rows = []
        for label, value, color in stats_cards:
            rows.append(
                card(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(label, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{int(value * 100)}%", size=15, color=color, weight=ft.FontWeight.BOLD),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.ProgressBar(value=value, color=color, bgcolor=SURFACE_SOFT, height=12),
                        ],
                        spacing=8,
                    )
                )
            )

        rows.append(
            card(
                ft.Row(
                    [
                        ft.Column([ft.Text("TimeTable Entries", color=TEXT_SECONDARY), ft.Text(str(len(db.get_timetable_entries())), size=24, weight=ft.FontWeight.BOLD)]),
                        ft.Column([ft.Text("Task Count", color=TEXT_SECONDARY), ft.Text(str(len(_today_tasks())), size=24, weight=ft.FontWeight.BOLD)]),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                )
            )
        )

        page_content.controls.clear()
        page_content.controls.append(
            ft.Column(
                [
                    ft.Text("Stats", size=24, weight=ft.FontWeight.BOLD),
                    ft.Column(rows, spacing=12),
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
            )
        )

    def show_view(index: int):
        nonlocal current_view_index
        current_view_index = index

        if page.navigation_bar is not None:
            page.navigation_bar.selected_index = index
        if desktop_nav is not None:
            desktop_nav.selected_index = index

        if index == 0:
            build_home_view()
        elif index == 1:
            build_today_view()
        elif index == 2:
            build_add_project_view()
        elif index == 3:
            build_timetable_view()
        else:
            build_stats_view()

    def jump_to(index: int):
        show_view(index)
        page.update()

    def on_nav_change(e):
        show_view(e.control.selected_index)
        page.update()

    if is_mobile:
        page.navigation_bar = ft.NavigationBar(
            selected_index=0,
            on_change=on_nav_change,
            bgcolor="#FFFFFF",
            indicator_color="#EDE9FF",
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.Icons.TODAY, label="Today"),
                ft.NavigationBarDestination(icon=ft.Icons.ADD_CIRCLE, label="Add"),
                ft.NavigationBarDestination(icon=ft.Icons.TABLE_CHART, label="시간표"),
                ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label="Stats"),
            ],
        )
        foreground = ft.Container(
            content=page_content,
            padding=ft.Padding(16, 18, 16, 90),
            expand=True,
        )
    else:
        desktop_nav = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=84,
            min_extended_width=130,
            on_change=on_nav_change,
            bgcolor="#FFFFFF",
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationRailDestination(icon=ft.Icons.TODAY, label="Today"),
                ft.NavigationRailDestination(icon=ft.Icons.ADD_CIRCLE, label="Add"),
                ft.NavigationRailDestination(icon=ft.Icons.TABLE_CHART, label="시간표"),
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Stats"),
            ],
        )
        foreground = ft.Row(
            [
                desktop_nav,
                ft.VerticalDivider(width=1, color=BORDER),
                ft.Container(content=page_content, padding=16, expand=True),
            ],
            expand=True,
        )

    page.add(
        ft.Stack(
            [
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        colors=["#F8F8FF", "#F2F4FB"],
                        begin=ft.Alignment(-1, -1),
                        end=ft.Alignment(1, 1),
                    ),
                ),
                foreground,
            ],
            expand=True,
        )
    )

    show_view(0)


def main(page: ft.Page):
    try:
        _build_app(page)
    except Exception:
        error_text = traceback.format_exc()
        try:
            page.clean()
            page.padding = 16
            page.bgcolor = "#FFFFFF"
            page.add(
                ft.Text("앱 시작 오류", color="#D14343", size=22, weight=ft.FontWeight.BOLD),
                ft.Text(error_text, color="#4A4A4A", selectable=True, size=12),
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
