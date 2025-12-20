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
    },
    'dark': {
        'bg_main': '#0f0f1a',
        'bg_sidebar': '#1a1a2e',
        'bg_card': '#1e1e32',
        'text_primary': '#f0f0f5',
        'text_secondary': '#a0a0b0',
        'text_sidebar': '#ffffff',
        'border': '#2a2a4a',
        'card_shadow': 'rgba(0, 0, 0, 0.3)',
    }
}

# 공통 액센트 컬러
ACCENT_COLOR = "#6C63FF"
ACCENT_LIGHT = "#8B85FF"
ACCENT_DARK = "#5449CC"

# 현재 테마 가져오기
def get_theme():
    if st.session_state.theme == 'auto':
        return 'light'  # 기본값 (브라우저 감지는 JS 필요)
    return st.session_state.theme

theme = get_theme()
T = THEMES[theme]

# Custom CSS - 테마 적용
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* 다크모드 자동 감지 - 브라우저 설정 기반 */
    @media (prefers-color-scheme: dark) {{
        :root {{
            --bg-main: {THEMES['dark']['bg_main']};
            --bg-sidebar: {THEMES['dark']['bg_sidebar']};
            --bg-card: {THEMES['dark']['bg_card']};
            --text-primary: {THEMES['dark']['text_primary']};
            --text-secondary: {THEMES['dark']['text_secondary']};
            --text-sidebar: {THEMES['dark']['text_sidebar']};
            --border: {THEMES['dark']['border']};
        }}
    }}
    @media (prefers-color-scheme: light) {{
        :root {{
            --bg-main: {THEMES['light']['bg_main']};
            --bg-sidebar: {THEMES['light']['bg_sidebar']};
            --bg-card: {THEMES['light']['bg_card']};
            --text-primary: {THEMES['light']['text_primary']};
            --text-secondary: {THEMES['light']['text_secondary']};
            --text-sidebar: {THEMES['light']['text_sidebar']};
            --border: {THEMES['light']['border']};
        }}
    }}
    
    /* 수동 테마 오버라이드 */
    .theme-light {{
        --bg-main: {THEMES['light']['bg_main']};
        --bg-sidebar: {THEMES['light']['bg_sidebar']};
        --bg-card: {THEMES['light']['bg_card']};
        --text-primary: {THEMES['light']['text_primary']};
        --text-secondary: {THEMES['light']['text_secondary']};
        --text-sidebar: {THEMES['light']['text_sidebar']};
        --border: {THEMES['light']['border']};
    }}
    .theme-dark {{
        --bg-main: {THEMES['dark']['bg_main']};
        --bg-sidebar: {THEMES['dark']['bg_sidebar']};
        --bg-card: {THEMES['dark']['bg_card']};
        --text-primary: {THEMES['dark']['text_primary']};
        --text-secondary: {THEMES['dark']['text_secondary']};
        --text-sidebar: {THEMES['dark']['text_sidebar']};
        --border: {THEMES['dark']['border']};
    }}
    
    /* 전체 배경 및 폰트 */
    .stApp {{
        background-color: {T['bg_main']};
        color: {T['text_primary']};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* 사이드바 스타일 - 시인성 개선 */
    section[data-testid="stSidebar"] {{
        background: {T['bg_sidebar']};
        border-right: 1px solid {T['border']};
    }}
    section[data-testid="stSidebar"] * {{
        color: {T['text_sidebar']} !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio label {{
        color: {T['text_sidebar']} !important;
        font-weight: 500 !important;
    }}
    
    /* 라디오 버튼 (메뉴) 스타일 - 시인성 대폭 개선 */
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
    section[data-testid="stSidebar"] .stRadio > div > label span {{
        color: {T['text_sidebar']} !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
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
    
    /* 버튼 스타일 */
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
        box-shadow: 0 6px 20px rgba(108, 99, 255, 0.4);
    }}
    
    /* 체크박스 스타일 */
    .stCheckbox > label > div[data-checked="true"] {{
        background-color: {ACCENT_COLOR} !important;
        border-color: {ACCENT_COLOR} !important;
    }}
    .stCheckbox label span {{
        color: {T['text_primary']} !important;
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
        box-shadow: 0 8px 30px {T['card_shadow']};
        transform: translateY(-2px);
    }}
    .card h3, .card h4, .card p, .card span, .card div {{
        color: {T['text_primary']};
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
    .progress-card * {{
        color: white !important;
    }}
    .progress-card h2 {{
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
    }}
    .progress-card p {{
        opacity: 0.9;
        margin: 8px 0 0 0;
    }}
    
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
    
    /* 헤더 스타일 */
    h1, h2, h3 {{
        font-weight: 700 !important;
        color: {T['text_primary']} !important;
    }}
    
    /* 구분선 */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, {ACCENT_COLOR}40, transparent);
        margin: 24px 0;
    }}
    
    /* 데이터 에디터 스타일 */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
    }}
    [data-testid="stDataFrame"] {{
        background: {T['bg_card']};
    }}
    
    /* Expander 스타일 */
    .streamlit-expanderHeader {{
        background: {T['bg_card']} !important;
        color: {T['text_primary']} !important;
        border-radius: 12px;
    }}
    .streamlit-expanderContent {{
        background: {T['bg_card']};
        border: 1px solid {T['border']};
        border-radius: 0 0 12px 12px;
    }}
    
    /* 모바일 최적화 */
    @media (max-width: 768px) {{
        .stApp {{
            padding: 8px;
        }}
        .card {{
            padding: 16px;
            border-radius: 12px;
        }}
        h1 {{
            font-size: 1.5rem !important;
        }}
        h2 {{
            font-size: 1.2rem !important;
        }}
    }}
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: {T['bg_card']};
        padding: 4px;
        border-radius: 12px;
        border: 1px solid {T['border']};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        color: {T['text_primary']};
    }}
    .stTabs [aria-selected="true"] {{
        background: {ACCENT_COLOR} !important;
        color: white !important;
    }}
    
    /* 텍스트 영역 */
    .stTextArea textarea {{
        border-radius: 12px;
        border: 2px solid {T['border']};
        background: {T['bg_card']};
        color: {T['text_primary']};
        transition: border-color 0.2s;
    }}
    .stTextArea textarea:focus {{
        border-color: {ACCENT_COLOR};
        box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1);
    }}
    .stTextArea textarea::placeholder {{
        color: {T['text_secondary']};
    }}
    
    /* Select box */
    .stSelectbox > div > div {{
        background: {T['bg_card']};
        border-color: {T['border']};
        color: {T['text_primary']};
    }}
    
    /* 테마 토글 버튼 */
    .theme-toggle {{
        display: flex;
        gap: 4px;
        background: {T['bg_card']};
        padding: 4px;
        border-radius: 10px;
        border: 1px solid {T['border']};
    }}
    .theme-btn {{
        padding: 8px 12px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s;
        background: transparent;
        color: {T['text_secondary']};
    }}
    .theme-btn.active {{
        background: {ACCENT_COLOR};
        color: white;
    }}
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
    
    # 메뉴 선택 (6개 섹션)
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
    
    # 전체 이수율 계산
    total_subjects = sum(len(subjects) for subjects in st.session_state.semester_progress.values())
    completed_subjects = sum(
        sum(1 for done in subjects.values() if done) 
        for subjects in st.session_state.semester_progress.values()
    )
    overall_rate = int((completed_subjects / total_subjects * 100) if total_subjects > 0 else 0)
    
    # 전체 진행률 카드
    st.markdown(f"""
        <div class="progress-card">
            <h2>{overall_rate}%</h2>
            <p>전체 이수율 ({completed_subjects}/{total_subjects} 과목)</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 학기별 과목 표시
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
    
    # 월간 달성률 계산
    month_df = st.session_state.monthly_goals
    month_total = len(month_df)
    month_done = len(month_df[month_df['Done'] == True]) if month_total > 0 else 0
    month_rate = int((month_done / month_total * 100) if month_total > 0 else 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 원형 프로그레스
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
    
    # 주간 진행률 계산
    weekly_df = st.session_state.weekly_tasks.copy()
    week_total = len(weekly_df)
    week_done = len(weekly_df[weekly_df['Done'] == True]) if week_total > 0 else 0
    week_rate = int((week_done / week_total * 100) if week_total > 0 else 0)
    
    # 메트릭 카드들
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
    
    # 주간 바 차트
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
    
    # 총 공부 시간 계산
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
    
    st.markdown("### ✏️ Edit Sessions")
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
    
    st.markdown("### ✏️ Edit Projects")
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