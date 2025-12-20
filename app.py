import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# ---------------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="Navigators Study Manager",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. 테마 시스템 (다크/라이트 모드)
# ---------------------------------------------------------
if 'theme' not in st.session_state:
    st.session_state.theme = 'auto'  # auto, light, dark

# 테마 색상 정의
THEMES = {
    'light': {
        'bg_main': '#f8f9fa',
        'bg_sidebar': '#ffffff',
        'bg_card': '#ffffff',
        'text_primary': '#1a1a2e',
        'text_secondary': '#6c757d',
        'text_sidebar': '#1a1a2e',
        'border': '#e0e0e0',
        'card_shadow': 'rgba(0, 0, 0, 0.08)',
        'btn_bg': '#ffffff',
        'btn_text': '#000000',
        'btn_border': '#e0e0e0',
    },
    'dark': {
        'bg_main': '#0a0a12',
        'bg_sidebar': '#121220',
        'bg_card': '#1a1a2e', 
        'text_primary': '#ffffff', 
        'text_secondary': '#b0b0c0',
        'text_sidebar': '#ffffff',
        'border': '#3a3a5a',
        'card_shadow': 'rgba(0, 0, 0, 0.4)',
        'btn_bg': '#1a1a2e',        # 다크모드 버튼 배경 (어두운 남색)
        'btn_text': '#ffffff',      # 다크모드 버튼 글자 (흰색)
        'btn_border': '#3a3a5a',    # 다크모드 버튼 테두리
    }
}

# 공통 액센트 컬러
ACCENT_COLOR = "#6C63FF"
ACCENT_LIGHT = "#8B85FF"
ACCENT_DARK = "#5449CC"

# 현재 테마 가져오기
def get_theme():
    if st.session_state.theme == 'auto':
        return 'light'  # 기본값
    return st.session_state.theme

theme = get_theme()
T = THEMES[theme]

# Custom CSS - 테마 적용
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* 다이나믹 테마 변수 설정 */
    :root {{
        --bg-main: {T['bg_main']};
        --bg-sidebar: {T['bg_sidebar']};
        --bg-card: {T['bg_card']};
        --text-primary: {T['text_primary']};
        --text-secondary: {T['text_secondary']};
        --text-sidebar: {T['text_sidebar']};
        --border: {T['border']};
    }}
    
    /* 전체 배경 및 기본 텍스트 강제 설정 */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
    }}
    
    {'body.theme-dark, .theme-dark p, .theme-dark span, .theme-dark label, .theme-dark h1, .theme-dark h2, .theme-dark h3, .theme-dark h4 { color: #ffffff !important; }' if theme == 'dark' else ''}
    
    .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    p, span, label, h1, h2, h3, h4 {{
        color: var(--text-primary) !important;
    }}
    
    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] {{
        background: {T['bg_sidebar']};
        border-right: 1px solid {T['border']};
    }}
    section[data-testid="stSidebar"] * {{
        color: {T['text_sidebar']} !important;
    }}
    
    /* 라디오 버튼 (메뉴) 스타일 */
    section[data-testid="stSidebar"] .stRadio > div {{
        gap: 6px;
    }}
    section[data-testid="stSidebar"] .stRadio > div > label {{
        background-color: {'rgba(108, 99, 255, 0.08)' if theme == 'light' else 'rgba(108, 99, 255, 0.15)'};
        border-radius: 12px;
        padding: 14px 18px;
        min-height: 52px;
        display: flex;
        align-items: center;
        transition: all 0.2s ease;
        border: 2px solid transparent;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: {T['text_sidebar']} !important;
    }}
    section[data-testid="stSidebar"] .stRadio > div > label:hover {{
        background-color: {'rgba(108, 99, 255, 0.15)' if theme == 'light' else 'rgba(108, 99, 255, 0.25)'};
        border-color: {ACCENT_COLOR};
        transform: translateX(4px);
    }}
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, {ACCENT_DARK} 100%);
        border-color: {ACCENT_COLOR};
        color: white !important;
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.4);
    }}
    section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] span {{
        color: white !important;
    }}
    
    /* 메인 버튼 스타일 */
    .stButton > button {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, {ACCENT_DARK} 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        min-height: 48px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, {ACCENT_LIGHT} 0%, {ACCENT_COLOR} 100%);
        transform: translateY(-2px);
    }}
    
    /* 위젯 텍스트 색상 강제 지정 */
    [data-testid="stWidgetLabel"] p, 
    .stCheckbox label span,
    [data-testid="stCheckbox"] label span,
    .stToggle label p,
    .stMarkdown p, .stMarkdown span,
    .streamlit-expanderHeader p {{
        color: var(--text-primary) !important;
    }}
    
    .theme-dark [data-testid="stWidgetLabel"] p {{
        color: #ffffff !important;
    }}
    
    /* 카드 스타일 */
    .card {{
        background: {T['bg_card']};
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px {T['card_shadow']};
        margin-bottom: 16px;
        border: 1px solid {T['border']};
        transition: all 0.2s ease;
    }}
    .card:hover {{
        transform: translateY(-2px);
    }}
    
    /* 진행률 카드 */
    .progress-card {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, {ACCENT_DARK} 100%);
        color: white !important;
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(108, 99, 255, 0.3);
    }}
    .progress-card * {{ color: white !important; }}
    
    /* 메트릭 카드 */
    .metric-card {{
        background: {T['bg_card']};
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px {T['card_shadow']};
        border-left: 4px solid {ACCENT_COLOR};
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {ACCENT_COLOR} !important;
    }}
    .metric-label {{
        color: {T['text_secondary']} !important;
        font-size: 0.9rem;
        margin-top: 4px;
    }}
    
    /* 데이터프레임 스타일 */
    [data-testid="stDataFrame"] {{
        background: {T['bg_card']};
        border: 1px solid {T['border']};
    }}
    
    /* 입력 필드 스타일 */
    .stTextInput input, .stNumberInput input {{
        border-radius: 10px !important;
        border: 2px solid {T['border']} !important;
        background: {T['bg_card']} !important;
        color: {T['text_primary']} !important;
    }}
    
    /* ------------------------------------------------------------- */
    /* [수정됨] 관리 모드 삭제 버튼 디자인 (테마에 따라 완벽하게 변경) */
    /* ------------------------------------------------------------- */
    div[data-testid="column"]:last-child button {{
        background: {T['btn_bg']} !important;
        color: {T['btn_text']} !important;
        border: 1px solid {T['btn_border']} !important;
        padding: 4px 12px !important;
        border-radius: 10px !important;
        transition: all 0.2s !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 42px !important;
        width: 100% !important;
        cursor: pointer !important;
        box-shadow: 0 2px 8px {T['card_shadow']} !important;
    }}

    /* 버튼 내부 텍스트 색상 강제 지정 */
    div[data-testid="column"]:last-child button p,
    div[data-testid="column"]:last-child button span,
    div[data-testid="column"]:last-child button div {{
        color: {T['btn_text']} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }}

    /* 버튼 호버(마우스 올렸을 때) 효과 */
    div[data-testid="column"]:last-child button:hover {{
        background: {'#2d2d44' if theme == 'dark' else '#f1f3f5'} !important;
        border-color: #ff4b4b !important; /* 호버 시 빨간 테두리 */
        color: #ff4b4b !important;       /* 호버 시 빨간 글씨 */
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px {T['card_shadow']} !important;
    }}

    /* 호버 시 내부 텍스트 색상 변경 */
    div[data-testid="column"]:last-child button:hover p,
    div[data-testid="column"]:last-child button:hover span {{
        color: #ff4b4b !important;
    }}
    /* ------------------------------------------------------------- */

    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 데이터 관리 (Session State)
# ---------------------------------------------------------

# 프로젝트 데이터
if 'project_data' not in st.session_state:
    st.session_state.project_data = pd.DataFrame([
        {"Subject": "캡스톤디자인1", "Task": "주제 선정 및 기획안 작성", "Done": True, "Deadline": "2026-03-15", "Priority": "High"},
        {"Subject": "자료구조", "Task": "연결 리스트 구현 실습", "Done": False, "Deadline": "2026-03-20", "Priority": "Medium"},
        {"Subject": "개인공부", "Task": "정보처리기사 실기 기출 1회독", "Done": False, "Deadline": "2026-04-15", "Priority": "High"},
    ])

# 월간 목표
if 'monthly_goals' not in st.session_state:
    st.session_state.monthly_goals = pd.DataFrame([
        {"Goal": "C언어 포인터 완벽 이해", "Done": True},
        {"Goal": "매일 아침 1시간 코딩", "Done": False},
        {"Goal": "전공 서적 1권 완독", "Done": False},
    ])

# 주간 할일
if 'weekly_tasks' not in st.session_state:
    st.session_state.weekly_tasks = pd.DataFrame([
        {"Day": "Mon", "Task": "자료구조 강의 수강", "Done": True},
        {"Day": "Tue", "Task": "알고리즘 문제 3개 풀기", "Done": True},
        {"Day": "Wed", "Task": "정처기 요약본 암기", "Done": False},
        {"Day": "Thu", "Task": "프로젝트 코드 리팩토링", "Done": False},
        {"Day": "Fri", "Task": "주간 복습", "Done": False},
    ])

# 일간 메모
if 'daily_memo' not in st.session_state:
    st.session_state.daily_memo = ""

# 일간 시간 기록
if 'daily_time_logs' not in st.session_state:
    st.session_state.daily_time_logs = pd.DataFrame([
        {"StartTime": "09:00", "EndTime": "11:00", "Activity": "자료구조 인강", "Category": "Study"},
        {"StartTime": "14:00", "EndTime": "17:00", "Activity": "코딩 실습", "Category": "Practice"},
    ])

# 스터디 세션
if 'study_sessions' not in st.session_state:
    st.session_state.study_sessions = pd.DataFrame([
        {"Name": "알고리즘 스터디", "Schedule": "매주 화요일 19:00", "TotalSessions": 10, "CompletedSessions": 8, "Status": "Active"},
        {"Name": "정처기 스터디", "Schedule": "매주 목요일 20:00", "TotalSessions": 12, "CompletedSessions": 3, "Status": "Active"},
    ])

# 학기별 과목 이수 현황
if 'semester_progress' not in st.session_state:
    st.session_state.semester_progress = {
        "1-1 (2026 Spring)": {
            "기초C프로그래밍": False, "자바프로그래밍": False, "자료구조(Core)": False,
            "컴퓨터구조": False, "데이터통신": False, "캡스톤디자인1": False
        },
        "1-2 (2026 Fall)": {
            "데이터베이스(Core)": False, "운영체제": False, "소프트웨어공학": False,
            "정보보호학개론": False, "논리회로": False, "캡스톤디자인2": False
        },
        "2-1 (2027 Spring)": {
            "네트워크보안": False, "운영체제보안": False, "데이터베이스보안": False,
            "컴퓨터네트워크": False, "진로지도": False
        },
        "2-2 (2027 Fall)": {
            "알고리즘(7급)": False, "리눅스보안": False, "SW취약점분석": False, "졸업지도": False
        }
    }

# ---------------------------------------------------------
# 4. 사이드바 네비게이션
# ---------------------------------------------------------
with st.sidebar:
    # 헤더
    st.markdown(f"""
        <div style="text-align: center; padding: 16px 0;">
            <h1 style="color: {T['text_sidebar']}; font-size: 1.8rem; margin: 0;">🧭 Navigators</h1>
            <p style="color: {T['text_secondary']}; font-size: 0.85rem; margin-top: 8px;">
                CS Transfer Student<br>2026-2027 Roadmap
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 테마 토글
    st.markdown(f"<p style='font-size: 0.8rem; color: {T['text_secondary']}; margin-bottom: 8px;'>🎨 Theme</p>", unsafe_allow_html=True)
    theme_options = {"🌙 Dark": "dark", "☀️ Light": "light", "🔄 Auto": "auto"}
    theme_labels = list(theme_options.keys())
    current_idx = list(theme_options.values()).index(st.session_state.theme)
    
    selected_theme = st.radio(
        "Theme",
        theme_labels,
        index=current_idx,
        horizontal=True,
        label_visibility="collapsed",
        key="theme_selector"
    )
    new_theme = theme_options[selected_theme]
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
    
    st.markdown("---")
    
    # D-Day 계산
    target_date = datetime(2026, 4, 15)
    today = datetime.now()
    d_day = (target_date - today).days
    
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {ACCENT_COLOR} 0%, {ACCENT_DARK} 100%);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            margin: 8px 0 16px 0;
            color: white;
        ">
            <div style="font-size: 0.8rem; opacity: 0.9;">📅 정보처리기사 실기</div>
            <div style="font-size: 1.8rem; font-weight: 800;">D-{d_day}</div>
            <div style="font-size: 0.75rem; opacity: 0.8;">2026.04.15</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 메뉴 선택
    st.markdown(f"<p style='font-size: 0.8rem; color: {T['text_secondary']}; margin-bottom: 8px;'>📂 Menu</p>", unsafe_allow_html=True)
    menu = st.radio(
        "Navigation",
        ["📚 Semester", "📅 Monthly", "📆 Weekly", "📝 Daily", "👥 Study", "💼 Project"],
        index=0,
        label_visibility="collapsed",
        key="main_menu"
    )
    
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; color: {T['text_secondary']}; font-size: 0.75rem; padding: 8px 0;">
            Designed for Success ✨
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. 메인 콘텐츠
# ---------------------------------------------------------

# === [1] Semester (학기) ===
if menu == "📚 Semester":
    st.markdown("# 📚 2-Year Curriculum")
    st.markdown("배재대 컴퓨터공학과 편입생 (2026-2027) 로드맵")
    
    total_subjects = sum(len(subjects) for subjects in st.session_state.semester_progress.values())
    completed_subjects = sum(
        sum(1 for done in subjects.values() if done) 
        for subjects in st.session_state.semester_progress.values()
    )
    overall_rate = int((completed_subjects / total_subjects * 100) if total_subjects > 0 else 0)
    
    st.markdown(f"""
        <div class="progress-card">
            <h2>{overall_rate}%</h2>
            <p>전체 이수율 ({completed_subjects}/{total_subjects} 과목)</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    for semester, subjects in st.session_state.semester_progress.items():
        semester_done = sum(1 for done in subjects.values() if done)
        semester_total = len(subjects)
        semester_rate = int((semester_done / semester_total * 100) if semester_total > 0 else 0)
        
        with st.expander(f"📌 {semester} — {semester_rate}% ({semester_done}/{semester_total})", expanded=False):
            cols = st.columns(3)
            for i, (subject, done) in enumerate(subjects.items()):
                with cols[i % 3]:
                    new_value = st.checkbox(
                        subject, 
                        value=done, 
                        key=f"sem_{semester}_{subject}"
                    )
                    st.session_state.semester_progress[semester][subject] = new_value

# === [2] Monthly (월간) ===
elif menu == "📅 Monthly":
    today = datetime.now()
    month_name = today.strftime("%B %Y")
    
    st.markdown(f"# 📅 {month_name}")
    st.markdown("이달의 목표를 설정하고 달성률을 확인하세요")
    
    month_df = st.session_state.monthly_goals
    month_total = len(month_df)
    month_done = len(month_df[month_df['Done'] == True]) if month_total > 0 else 0
    month_rate = int((month_done / month_total * 100) if month_total > 0 else 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig = go.Figure(data=[go.Pie(
            values=[month_done, month_total - month_done],
            hole=0.75,
            marker_colors=[ACCENT_COLOR, T['border']],
            textinfo='none',
            hoverinfo='skip'
        )])
        fig.update_layout(
            showlegend=False,
            annotations=[dict(text=f'{month_rate}%', x=0.5, y=0.5, font_size=36, font_weight=700, font_color=T['text_primary'], showarrow=False)],
            margin=dict(t=20, b=20, l=20, r=20),
            height=200,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<p style='text-align:center; color:{T['text_secondary']};'>{month_total}개 중 {month_done}개 달성</p>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Goals")
        
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            show_add = st.toggle("➕ 항목 추가", key="toggle_monthly_add")
        with col_m2:
            manage_mode = st.toggle("⚙️ 관리 모드", key="manage_monthly")

        if show_add:
            with st.form("add_monthly_goal", clear_on_submit=True):
                new_goal = st.text_input("목표 내용")
                if st.form_submit_button("추가", use_container_width=True):
                    if new_goal:
                        new_row = pd.DataFrame([{"Goal": new_goal, "Done": False}])
                        st.session_state.monthly_goals = pd.concat([st.session_state.monthly_goals, new_row], ignore_index=True)
                        st.rerun()
        
        if manage_mode:
            st.info("💡 삭제하고 싶은 항목 옆의 '삭제' 버튼을 누르세요.")
            for idx, row in st.session_state.monthly_goals.iterrows():
                m_col1, m_col2 = st.columns([5, 1])
                m_col1.markdown(f"**{row['Goal']}**")
                if m_col2.button("삭제", key=f"del_monthly_{idx}", help="이 목표를 삭제합니다.", type="secondary"):
                    st.session_state.monthly_goals = st.session_state.monthly_goals.drop(idx).reset_index(drop=True)
                    st.rerun()
        else:
            edited_monthly = st.data_editor(
                st.session_state.monthly_goals,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Done": st.column_config.CheckboxColumn("✓", default=False, width="small"),
                    "Goal": st.column_config.TextColumn("목표", width="large"),
                },
                hide_index=True,
                key="monthly_editor"
            )
            st.session_state.monthly_goals = edited_monthly

# === [3] Weekly (주간) ===
elif menu == "📆 Weekly":
    today = datetime.now()
    week_num = today.isocalendar()[1]
    
    st.markdown(f"# 📆 Week {week_num}")
    st.markdown("이번 주 할 일을 계획하고 진행 상황을 확인하세요")
    
    weekly_df = st.session_state.weekly_tasks.copy()
    week_total = len(weekly_df)
    week_done = len(weekly_df[weekly_df['Done'] == True]) if week_total > 0 else 0
    week_rate = int((week_done / week_total * 100) if week_total > 0 else 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{week_rate}%</div>
                <div class="metric-label">주간 달성률</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{week_done}</div>
                <div class="metric-label">완료된 할일</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{week_total - week_done}</div>
                <div class="metric-label">남은 할일</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    chart_df = weekly_df.copy()
    chart_df['Value'] = chart_df['Done'].apply(lambda x: 100 if x else 20)
    
    fig = px.bar(
        chart_df, x='Day', y='Value',
        color='Done',
        color_discrete_map={True: ACCENT_COLOR, False: T['border']}
    )
    fig.update_layout(
        yaxis_range=[0, 100],
        yaxis_title="Progress",
        xaxis_title="",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=200,
        margin=dict(t=20, b=40, l=40, r=20),
        font=dict(color=T['text_primary'])
    )
    fig.update_traces(marker_line_width=0)
    fig.update_xaxes(tickfont=dict(color=T['text_primary']))
    fig.update_yaxes(tickfont=dict(color=T['text_secondary']))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 📋 Tasks")
    
    col_w1, col_w2 = st.columns([1, 1])
    with col_w1:
        show_add_w = st.toggle("➕ 항목 추가", key="toggle_weekly_add")
    with col_w2:
        manage_mode_w = st.toggle("⚙️ 관리 모드", key="manage_weekly")

    if show_add_w:
        with st.form("add_weekly_task", clear_on_submit=True):
            col_a, col_b = st.columns([1, 3])
            new_day = col_a.selectbox("요일", options=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
            new_task = col_b.text_input("할 일")
            if st.form_submit_button("추가", use_container_width=True):
                if new_task:
                    new_row = pd.DataFrame([{"Day": new_day, "Task": new_task, "Done": False}])
                    st.session_state.weekly_tasks = pd.concat([st.session_state.weekly_tasks, new_row], ignore_index=True)
                    st.rerun()

    if manage_mode_w:
        st.info("💡 삭제하고 싶은 일정을 선택하세요.")
        for idx, row in st.session_state.weekly_tasks.iterrows():
            w_col1, w_col2, w_col3 = st.columns([1, 4, 1])
            w_col1.markdown(f"**{row['Day']}**")
            w_col2.markdown(row['Task'])
            if w_col3.button("삭제", key=f"del_weekly_{idx}", help="이 할 일을 삭제합니다.", type="secondary", use_container_width=True):
                st.session_state.weekly_tasks = st.session_state.weekly_tasks.drop(idx).reset_index(drop=True)
                st.rerun()
    else:
        edited_weekly = st.data_editor(
            st.session_state.weekly_tasks,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Done": st.column_config.CheckboxColumn("✓", default=False, width="small"),
                "Day": st.column_config.SelectboxColumn("요일", options=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], width="small"),
                "Task": st.column_config.TextColumn("할 일", width="large"),
            },
            hide_index=True,
            key="weekly_editor"
        )
        st.session_state.weekly_tasks = edited_weekly

# === [4] Daily (일간) ===
elif menu == "📝 Daily":
    today = datetime.now()
    day_str = today.strftime("%B %d, %Y (%A)")
    
    st.markdown(f"# 📝 {day_str}")
    st.markdown("오늘의 공부 기록을 남기세요")
    
    time_df = st.session_state.daily_time_logs
    total_minutes = 0
    for _, row in time_df.iterrows():
        try:
            start = datetime.strptime(row['StartTime'], "%H:%M")
            end = datetime.strptime(row['EndTime'], "%H:%M")
            diff = (end - start).seconds // 60
            total_minutes += diff
        except:
            pass
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">🕐 {hours}h {minutes}m</div>
                <div class="metric-label">오늘 총 공부시간</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(time_df)}</div>
                <div class="metric-label">활동 세션</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ⏰ Time Log")
    
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        show_add_d = st.toggle("➕ 기록 추가", key="toggle_daily_add")
    with col_d2:
        manage_mode_d = st.toggle("⚙️ 관리 모드", key="manage_daily")

    if show_add_d:
        with st.form("add_daily_log", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            s_time = col_a.text_input("시작 (HH:MM)", placeholder="09:00")
            e_time = col_b.text_input("종료 (HH:MM)", placeholder="11:00")
            activity = st.text_input("활동 내용")
            category = st.selectbox("분류", options=["Study", "Practice", "Review", "Project", "Other"])
            if st.form_submit_button("기록 추가", use_container_width=True):
                if activity:
                    new_row = pd.DataFrame([{
                        "StartTime": s_time, 
                        "EndTime": e_time, 
                        "Activity": activity, 
                        "Category": category
                    }])
                    st.session_state.daily_time_logs = pd.concat([st.session_state.daily_time_logs, new_row], ignore_index=True)
                    st.rerun()

    if manage_mode_d:
        st.info("💡 삭제하고 싶은 기록 옆의 '삭제' 버튼을 누르세요.")
        for idx, row in st.session_state.daily_time_logs.iterrows():
            d_col1, d_col2, d_col3 = st.columns([2, 5, 1])
            d_col1.markdown(f"{row['StartTime']}~{row['EndTime']}")
            d_col2.markdown(f"**[{row['Category']}]** {row['Activity']}")
            if d_col3.button("삭제", key=f"del_daily_{idx}", help="이 시간 기록을 삭제합니다.", type="secondary", use_container_width=True):
                st.session_state.daily_time_logs = st.session_state.daily_time_logs.drop(idx).reset_index(drop=True)
                st.rerun()
    else:
        edited_time = st.data_editor(
            st.session_state.daily_time_logs,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "StartTime": st.column_config.TextColumn("시작", width="small"),
                "EndTime": st.column_config.TextColumn("종료", width="small"),
                "Activity": st.column_config.TextColumn("활동", width="large"),
                "Category": st.column_config.SelectboxColumn("분류", options=["Study", "Practice", "Review", "Project", "Other"], width="small"),
            },
            hide_index=True,
            key="time_editor"
        )
        st.session_state.daily_time_logs = edited_time
    
    st.markdown("---")
    
    st.markdown("### 📓 Today's Memo")
    st.session_state.daily_memo = st.text_area(
        "Memo",
        value=st.session_state.daily_memo,
        height=200,
        placeholder="오늘 공부한 내용, 느낀 점, 내일 할 일 등을 자유롭게 기록하세요...",
        label_visibility="collapsed"
    )

# === [5] Study (스터디) ===
elif menu == "👥 Study":
    st.markdown("# 👥 Study Sessions")
    st.markdown("스터디 그룹과 세션을 관리하세요")
    
    study_df = st.session_state.study_sessions
    
    for idx, row in study_df.iterrows():
        progress = int((row['CompletedSessions'] / row['TotalSessions'] * 100) if row['TotalSessions'] > 0 else 0)
        status_color = ACCENT_COLOR if row['Status'] == 'Active' else T['text_secondary']
        
        st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="margin: 0; font-size: 1.1rem; color: {T['text_primary']};">📖 {row['Name']}</h3>
                        <p style="color: {T['text_secondary']}; margin: 4px 0; font-size: 0.9rem;">{row['Schedule']}</p>
                    </div>
                    <span style="
                        background: {status_color}20;
                        color: {status_color};
                        padding: 4px 12px;
                        border-radius: 20px;
                        font-size: 0.8rem;
                        font-weight: 600;
                    ">{row['Status']}</span>
                </div>
                <div style="margin-top: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 6px; color: {T['text_primary']};">
                        <span>진행률</span>
                        <span style="font-weight: 600;">{row['CompletedSessions']}/{row['TotalSessions']} 회</span>
                    </div>
                    <div style="background: {T['border']}; border-radius: 10px; height: 10px; overflow: hidden;">
                        <div style="background: {ACCENT_COLOR}; width: {progress}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ✏️ Session List & Editor")
    
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        show_add_s = st.toggle("➕ 항목 추가", key="toggle_study_add")
    with col_s2:
        manage_mode_s = st.toggle("⚙️ 관리 모드", key="manage_study")

    if show_add_s:
        with st.form("add_study_session", clear_on_submit=True):
            s_name = st.text_input("스터디 이름")
            s_schedule = st.text_input("일정 (예: 매주 화요일 19:00)")
            col_a, col_b = st.columns(2)
            s_total = col_a.number_input("총 회차", min_value=1, value=10)
            s_done = col_b.number_input("현재 완료", min_value=0, value=0)
            if st.form_submit_button("스터디 생성", use_container_width=True):
                if s_name:
                    new_row = pd.DataFrame([{
                        "Name": s_name, 
                        "Schedule": s_schedule, 
                        "TotalSessions": int(s_total), 
                        "CompletedSessions": int(s_done), 
                        "Status": "Active"
                    }])
                    st.session_state.study_sessions = pd.concat([st.session_state.study_sessions, new_row], ignore_index=True)
                    st.rerun()

    if manage_mode_s:
        st.info("💡 삭제하고 싶은 스터디 옆의 '삭제' 버튼을 누르세요.")
        for idx, row in st.session_state.study_sessions.iterrows():
            sc_1, sc_2, sc_3 = st.columns([4, 2, 1])
            sc_1.markdown(f"**{row['Name']}**")
            sc_2.markdown(row['Schedule'])
            if sc_3.button("삭제", key=f"del_study_{idx}", help="이 스터디 세션을 삭제합니다.", type="secondary", use_container_width=True):
                st.session_state.study_sessions = st.session_state.study_sessions.drop(idx).reset_index(drop=True)
                st.rerun()
    else:
        edited_study = st.data_editor(
            st.session_state.study_sessions,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Name": st.column_config.TextColumn("스터디명", width="medium"),
                "Schedule": st.column_config.TextColumn("일정", width="medium"),
                "TotalSessions": st.column_config.NumberColumn("총 회차", min_value=1, width="small"),
                "CompletedSessions": st.column_config.NumberColumn("완료", min_value=0, width="small"),
                "Status": st.column_config.SelectboxColumn("상태", options=["Active", "Paused", "Completed"], width="small"),
            },
            hide_index=True,
            key="study_editor"
        )
        st.session_state.study_sessions = edited_study

# === [6] Project (프로젝트) ===
elif menu == "💼 Project":
    st.markdown("# 💼 My Projects")
    st.markdown("프로젝트와 과제를 관리하세요")
    
    proj_df = st.session_state.project_data
    proj_total = len(proj_df)
    proj_done = len(proj_df[proj_df['Done'] == True]) if proj_total > 0 else 0
    proj_rate = int((proj_done / proj_total * 100) if proj_total > 0 else 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{proj_rate}%</div>
                <div class="metric-label">완료율</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{proj_done}</div>
                <div class="metric-label">완료</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{proj_total - proj_done}</div>
                <div class="metric-label">진행중</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📋 Task List")
    for idx, row in proj_df.iterrows():
        try:
            deadline = datetime.strptime(str(row.get('Deadline', '')), "%Y-%m-%d")
            d_day = (deadline - datetime.now()).days
            d_day_str = f"D-{d_day}" if d_day >= 0 else f"D+{abs(d_day)}"
            d_day_color = ACCENT_COLOR if d_day >= 7 else ("#ff6b6b" if d_day >= 0 else T['text_secondary'])
        except:
            d_day_str = ""
            d_day_color = T['text_secondary']
        
        priority_colors = {"High": "#ff6b6b", "Medium": "#ffd93d", "Low": "#6bcb77"}
        priority_color = priority_colors.get(row.get('Priority', 'Medium'), '#6c757d')
        
        done_style = "opacity: 0.5;" if row['Done'] else ""
        text_style = "text-decoration: line-through;" if row['Done'] else ""
        
        st.markdown(f"""
            <div class="card" style="{done_style}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="
                            background: {priority_color}20;
                            color: {priority_color};
                            padding: 2px 8px;
                            border-radius: 4px;
                            font-size: 0.7rem;
                            font-weight: 600;
                        ">{row.get('Priority', 'Medium')}</span>
                        <h4 style="margin: 8px 0 4px 0; color: {T['text_primary']}; {text_style}">{row['Subject']}</h4>
                        <p style="color: {T['text_secondary']}; margin: 0; font-size: 0.9rem; {text_style}">{row['Task']}</p>
                    </div>
                    <span style="
                        color: {d_day_color};
                        font-weight: 700;
                        font-size: 0.9rem;
                    ">{d_day_str}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ✏️ Project List & Editor")
    
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        show_add_p = st.toggle("➕ 항목 추가", key="toggle_project_add")
    with col_p2:
        manage_mode_p = st.toggle("⚙️ 관리 모드", key="manage_project")

    if show_add_p:
        with st.form("add_project_task", clear_on_submit=True):
            p_subject = st.text_input("과목/프로젝트")
            p_task = st.text_input("할 일 내용")
            col_a, col_b = st.columns(2)
            p_deadline = col_a.text_input("마감 (YYYY-MM-DD)", placeholder="2026-12-31")
            p_priority = col_b.selectbox("우선순위", options=["High", "Medium", "Low"], index=1)
            if st.form_submit_button("태스크 추가", use_container_width=True):
                if p_subject and p_task:
                    new_row = pd.DataFrame([{
                        "Subject": p_subject, 
                        "Task": p_task, 
                        "Done": False, 
                        "Deadline": p_deadline, 
                        "Priority": p_priority
                    }])
                    st.session_state.project_data = pd.concat([st.session_state.project_data, new_row], ignore_index=True)
                    st.rerun()

    if manage_mode_p:
        st.info("💡 삭제하고 싶은 태스크 옆의 '삭제' 버튼을 누르세요.")
        for idx, row in st.session_state.project_data.iterrows():
            pr_1, pr_2, pr_3 = st.columns([3, 4, 1])
            pr_1.markdown(f"**{row['Subject']}**")
            pr_2.markdown(row['Task'])
            if pr_3.button("삭제", key=f"del_project_{idx}", help="이 프로젝트 태스크를 삭제합니다.", type="secondary", use_container_width=True):
                st.session_state.project_data = st.session_state.project_data.drop(idx).reset_index(drop=True)
                st.rerun()
    else:
        edited_proj = st.data_editor(
            st.session_state.project_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Done": st.column_config.CheckboxColumn("✓", default=False, width="small"),
                "Subject": st.column_config.TextColumn("과목/프로젝트", width="medium"),
                "Task": st.column_config.TextColumn("할 일", width="large"),
                "Deadline": st.column_config.TextColumn("마감일 (YYYY-MM-DD)", width="medium"),
                "Priority": st.column_config.SelectboxColumn("우선순위", options=["High", "Medium", "Low"], width="small"),
            },
            hide_index=True,
            key="project_editor"
        )
        st.session_state.project_data = edited_proj