import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os

# ---------------------------------------------------------
# 0. 데이터 지속성 설정 (로컬 JSON 저장 방식)
# ---------------------------------------------------------
DATA_FILE = "data.json"

def sync_load_data():
    """로컬 JSON 파일에서 데이터를 읽어와 세션 상태에 반영"""
    if not os.path.exists(DATA_FILE):
        return False
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 1. 학기
        if "semester_progress" in data:
            st.session_state.semester_progress = data["semester_progress"]
            
        # 2~6, 8. DataFrames
        keys = ["monthly_goals", "weekly_tasks", "daily_time_logs", 
                "study_sessions", "project_data", "habits"]
        for key in keys:
            if key in data:
                st.session_state[key] = pd.DataFrame(data[key])
                
        # 7. 메모
        if "daily_memo" in data:
            st.session_state.daily_memo = data["daily_memo"]
            
        # 9. 습관 로그
        if "habit_logs" in data:
            st.session_state.habit_logs = data["habit_logs"]
            
        return True
    except Exception as e:
        st.sidebar.error(f"데이터 로드 실패: {e}")
        return False

def sync_save_data():
    """세션 상태의 데이터를 로컬 JSON 파일로 저장"""
    try:
        data = {}
        # 1. 학기 (Dict)
        data["semester_progress"] = st.session_state.semester_progress
        
        # 2~6, 8. DataFrames (JSON 저장을 위해 Dict로 변환)
        keys = ["monthly_goals", "weekly_tasks", "daily_time_logs", 
                "study_sessions", "project_data", "habits"]
        for key in keys:
            data[key] = st.session_state[key].to_dict(orient="records")
            
        # 7. 메모
        data["daily_memo"] = st.session_state.daily_memo
        
        # 9. 습관 로그
        data["habit_logs"] = st.session_state.habit_logs
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.sidebar.warning(f"데이터 자동 저장 실패: {e}")
        return False


# ---------------------------------------------------------
# 1. 페이지 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="Navigators Mobile",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed" # 모바일 최적화를 위해 사이드바 접기
)

# ---------------------------------------------------------
# 2. 테마 시스템 (Light / Dark / Auto)
# ---------------------------------------------------------
# 테마 상태 관리
if 'theme' not in st.session_state:
    st.session_state.theme = 'auto'  # auto, light, dark

# 사이드바에 테마 선택 추가
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    theme_options = {"🌓 Auto (시스템)": "auto", "☀️ Light": "light", "🌙 Dark": "dark"}
    selected = st.radio("테마 선택", list(theme_options.keys()), 
                        index=list(theme_options.values()).index(st.session_state.theme),
                        label_visibility="collapsed")
    new_theme = theme_options[selected]
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
    
    st.markdown("---")
    
    # 로컬 저장소 수동 동기화 버튼
    if st.button("💾 데이터 강제 저장", use_container_width=True):
        if sync_save_data():
            st.success("저장 완료!")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📤 데이터 관리")
    
    # 데이터 내보내기
    import json
    if st.button("📥 데이터 백업 (JSON)", use_container_width=True):
        export_data = {
            "monthly_goals": st.session_state.monthly_goals.to_dict('records'),
            "weekly_tasks": st.session_state.weekly_tasks.to_dict('records'),
            "study_sessions": st.session_state.study_sessions.to_dict('records'),
            "project_data": st.session_state.project_data.to_dict('records'),
            "habits": st.session_state.habits.to_dict('records'),
            "habit_logs": st.session_state.habit_logs,
            "daily_memo": st.session_state.daily_memo
        }
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ 다운로드",
            json_str,
            file_name="navigators_backup.json",
            mime="application/json",
            use_container_width=True
        )

# 테마 팔레트 정의 (예시 이미지 기반)
THEMES = {
    'light': {
        'bg_main': '#f8fafc',
        'bg_card': '#ffffff',
        'text_primary': '#1e293b',
        'text_secondary': '#64748b',
        'accent': '#0d9488',  # Teal (예시1)
        'accent_light': '#14b8a6',
        'border': '#e2e8f0',
        'chart_colors': ['#0d9488', '#64748b', '#94a3b8'],
    },
    'dark': {
        'bg_main': '#0a1628',
        'bg_card': 'rgba(15, 30, 60, 0.8)',
        'text_primary': '#f1f5f9',
        'text_secondary': '#94a3b8',
        'accent': '#38bdf8',  # Sky Blue (예시2)
        'accent_light': '#7dd3fc',
        'border': 'rgba(56, 189, 248, 0.2)',
        'chart_colors': ['#38bdf8', '#0ea5e9', '#0284c7'],
    }
}

# 현재 테마 결정
def get_current_theme():
    if st.session_state.theme == 'auto':
        return 'dark'  # 기본값 (JS로 감지 불가하여 dark 사용)
    return st.session_state.theme

current = get_current_theme()
T = THEMES[current]
is_dark = current == 'dark'

# 기존 코드 호환성 변수
PURPLE_BTN = T['accent']
CARD_BG = T['bg_card']

# CSS 생성
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* ============================================ */
    /* 기본 스타일 */
    /* ============================================ */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background: {T['bg_main']} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    {"" if not is_dark else f'''
    /* 다크모드 글로우 배경 효과 */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: 
            radial-gradient(ellipse 80% 60% at 30% 30%, rgba(56, 189, 248, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse 60% 50% at 70% 70%, rgba(14, 165, 233, 0.06) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }}
    '''}
    
    h1, h2, h3, h4 {{
        color: {T['text_primary']} !important;
        font-weight: 700 !important;
    }}
    
    p, span, div, label {{
        color: {T['text_primary']} !important;
    }}
    
    /* ============================================ */
    /* 카드 스타일 */
    /* ============================================ */
    .metric-card {{
        background: {T['bg_card']};
        {"backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);" if is_dark else ""}
        border-radius: 16px;
        padding: 20px;
        border: 1px solid {T['border']};
        {"box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.05);" if is_dark else "box-shadow: 0 1px 3px rgba(0,0,0,0.08);"}
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        {"border-color: " + T['accent'] + "; box-shadow: 0 0 30px rgba(56, 189, 248, 0.15);" if is_dark else "box-shadow: 0 4px 12px rgba(0,0,0,0.1);"}
        transform: translateY(-2px);
    }}
    
    /* ============================================ */
    /* 버튼 스타일 */
    /* ============================================ */
    div[data-testid="column"] button {{
        background: {T['accent']} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 48px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        {"box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3);" if is_dark else "box-shadow: 0 2px 8px rgba(13, 148, 136, 0.2);"}
        transition: all 0.2s ease !important;
    }}
    
    div[data-testid="column"] button:hover {{
        background: {T['accent_light']} !important;
        transform: translateY(-2px) !important;
        {"box-shadow: 0 8px 25px rgba(56, 189, 248, 0.4) !important;" if is_dark else "box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3) !important;"}
    }}
    
    /* ============================================ */
    /* 입력 필드 */
    /* ============================================ */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input, .stTextArea textarea {{
        background: {"rgba(15, 30, 60, 0.6)" if is_dark else "#ffffff"} !important;
        color: {T['text_primary']} !important;
        border: 1px solid {T['border']} !important;
        border-radius: 10px !important;
    }}
    
    .stTextInput input:focus {{
        border-color: {T['accent']} !important;
        {"box-shadow: 0 0 15px rgba(56, 189, 248, 0.2) !important;" if is_dark else ""}
    }}
    
    /* ============================================ */
    /* 탭 스타일 */
    /* ============================================ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: {"rgba(15, 30, 60, 0.5)" if is_dark else "#f1f5f9"};
        padding: 6px;
        border-radius: 14px;
        {"backdrop-filter: blur(10px);" if is_dark else ""}
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 10px;
        padding: 10px 16px;
        border: none;
        color: {T['text_secondary']} !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: {"rgba(56, 189, 248, 0.1)" if is_dark else "rgba(13, 148, 136, 0.08)"};
        color: {T['text_primary']} !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {T['accent']} !important;
        color: white !important;
        {"box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3);" if is_dark else ""}
    }}
    
    /* ============================================ */
    /* 사이드바 */
    /* ============================================ */
    section[data-testid="stSidebar"] {{
        background: {"#0f1e3c" if is_dark else "#ffffff"} !important;
        border-right: 1px solid {T['border']};
    }}
    
    section[data-testid="stSidebar"] * {{
        color: {T['text_primary']} !important;
    }}
    
    /* ============================================ */
    /* 체크박스 */
    /* ============================================ */
    .stCheckbox label span {{
        color: {T['text_primary']} !important;
    }}
    
    /* ============================================ */
    /* 스크롤바 */
    /* ============================================ */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: {"#0a1628" if is_dark else "#f1f5f9"}; }}
    ::-webkit-scrollbar-thumb {{ 
        background: {T['accent']};
        border-radius: 4px;
    }}
    
    /* 선택 색상 */
    ::selection {{
        background: {T['accent']};
        color: white;
    }}
    
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 데이터 초기화 (시트에서 먼저 시도 후 없으면 기본값)
# ---------------------------------------------------------
# 앱 시작 시 한 번만 시트에서 데이터를 불러옴
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    
    # 1단계: 기본값 설정 (시트 로드 실패 대비)
    st.session_state.semester_progress = {
        "1-1 (2026 Spring)": {
            "기초C프로그래밍": True, "컴퓨터구조": False, "자바프로그래밍": False, 
            "데이터통신": False, "자료구조(Core)": False, "캡스톤디자인1": False
        },
        "1-2 (2026 Fall)": {
            "데이터베이스(Core)": False, "정보보호학개론": False, "운영체제": False, 
            "논리회로": False, "소프트웨어공학": False, "캡스톤디자인2": False
        },
        "2-1 (2027 Spring)": {
            "네트워크보안": False, "컴퓨터네트워크": False, "운영체제보안": False, 
            "진로지도": False, "데이터베이스보안": False
        },
        "2-2 (2027 Fall)": {
            "알고리즘(7급)": False, "졸업지도": False, "리눅스보안": False, "SW취약점분석": False
        }
    }
    st.session_state.monthly_goals = pd.DataFrame([
        {"Goal": "C언어 포인터 완벽 이해", "Done": True},
        {"Goal": "매일 아침 1시간 코딩", "Done": False},
        {"Goal": "전공 서적 1권 완독", "Done": False}
    ])
    st.session_state.weekly_tasks = pd.DataFrame([
        {"Day": "Mon", "Task": "자료구조 강의", "Done": True},
        {"Day": "Tue", "Task": "알고리즘 풀이", "Done": True},
        {"Day": "Wed", "Task": "복습", "Done": False},
        {"Day": "Thu", "Task": "프로젝트", "Done": False},
        {"Day": "Fri", "Task": "스터디", "Done": False}
    ])
    st.session_state.daily_time_logs = pd.DataFrame([
        {"StartTime": "09:00", "EndTime": "11:00", "Activity": "자료구조", "Category": "Study"},
        {"StartTime": "14:00", "EndTime": "16:00", "Activity": "코딩", "Category": "Practice"}
    ])
    st.session_state.study_sessions = pd.DataFrame([
        {"Name": "알고리즘", "Total": 10, "Done": 8},
        {"Name": "정보처리기사", "Total": 12, "Done": 3}
    ])
    st.session_state.project_data = pd.DataFrame([
        {"Subject": "캡스톤1", "Task": "기획안", "Total": 5, "Done": 5, "Deadline": "2026-03-15"},
        {"Subject": "자료구조", "Task": "연결리스트", "Total": 8, "Done": 2, "Deadline": "2026-03-20"}
    ])
    st.session_state.daily_memo = ""
    st.session_state.habits = pd.DataFrame([
        {"Name": "아침 운동", "Icon": "🏃", "Target": 7},
        {"Name": "독서 30분", "Icon": "📚", "Target": 5},
        {"Name": "물 2L 마시기", "Icon": "💧", "Target": 7}
    ])
    today = datetime.now().date()
    st.session_state.habit_logs = {
        "아침 운동": [str(today - timedelta(days=i)) for i in [1, 2, 4, 5]],
        "독서 30분": [str(today - timedelta(days=i)) for i in [0, 1, 3]],
        "물 2L 마시기": [str(today - timedelta(days=i)) for i in [0, 1, 2, 3, 4, 5, 6]]
    }

    # 2단계: 로컬 JSON에서 데이터 덮어쓰기 시도
    sync_load_data()


# ---------------------------------------------------------
# 4. 차트 생성 함수 (대시보드용)
# ---------------------------------------------------------
def draw_pie_chart(done, total, title):
    if total == 0: total = 1
    fig = go.Figure(data=[go.Pie(
        values=[done, total-done],
        hole=0.7,
        marker=dict(colors=[PURPLE_BTN, '#2f2f3d']),
        textinfo='none',
        hoverinfo='label+percent'
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=120,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(text=f"{int(done/total*100)}%", x=0.5, y=0.5, font_size=16, font_color='white', showarrow=False)]
    )
    return fig

def draw_bar_chart(df, x_col, y_col, title):
    fig = px.bar(df, x=x_col, y=y_col, color=y_col, 
                 color_discrete_sequence=[PURPLE_BTN])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=120,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, tickfont=dict(color='white', size=10)),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

# ---------------------------------------------------------
# 5. UI 구성
# ---------------------------------------------------------
# 사이드바 대신 상단 네비게이션 (모바일 친화적)
st.markdown("<h2 style='text-align:center; margin-bottom:10px;'>🧭 Navigators</h2>", unsafe_allow_html=True)
menu = st.tabs(["📊 대시보드", "📚 학기", "📅 월간", "📆 주간", "📝 데일리", "📖 스터디", "💼 프로젝트", "🎯 습관"])

# === [1] 대시보드 (통합 그래프) ===
with menu[0]:
    st.markdown("### 📊 Overall Progress")
    
    # Grid Layout for Mobile (2 columns per row)
    row1_c1, row1_c2 = st.columns(2)
    
    # 1. 학기 달성률
    with row1_c1:
        st.markdown(f"<div class='metric-card'><div style='text-align:center; margin-bottom:5px'>📚 학기 이수율</div>", unsafe_allow_html=True)
        total_sub = sum(len(v) for v in st.session_state.semester_progress.values())
        done_sub = sum(sum(1 for x in v.values() if x) for v in st.session_state.semester_progress.values())
        st.plotly_chart(draw_pie_chart(done_sub, total_sub, "Semester"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # 2. 월간 달성률
    with row1_c2:
        st.markdown(f"<div class='metric-card'><div style='text-align:center; margin-bottom:5px'>📅 이번달 목표</div>", unsafe_allow_html=True)
        m_df = st.session_state.monthly_goals
        st.plotly_chart(draw_pie_chart(len(m_df[m_df['Done']]), len(m_df), "Monthly"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    row2_c1, row2_c2 = st.columns(2)
    
    # 3. 주간 달성률
    with row2_c1:
        st.markdown(f"<div class='metric-card'><div style='text-align:center; margin-bottom:5px'>📆 주간 할일</div>", unsafe_allow_html=True)
        w_df = st.session_state.weekly_tasks
        st.plotly_chart(draw_pie_chart(len(w_df[w_df['Done']]), len(w_df), "Weekly"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. 데일리 공부시간 (Bar Chart)
    with row2_c2:
        st.markdown(f"<div class='metric-card'><div style='text-align:center; margin-bottom:5px'>📝 오늘 공부</div>", unsafe_allow_html=True)
        # 간단히 총 시간만 퍼센트로 시각화 (목표 6시간 가정)
        d_df = st.session_state.daily_time_logs
        total_min = 0
        for _, r in d_df.iterrows():
            try:
                t1 = datetime.strptime(r['StartTime'], "%H:%M")
                t2 = datetime.strptime(r['EndTime'], "%H:%M")
                total_min += (t2-t1).seconds//60
            except: pass
        st.plotly_chart(draw_pie_chart(total_min, 360, "Daily"), use_container_width=True) # 6시간 기준
        st.markdown(f"<div style='text-align:center; font-size:0.8rem'>{total_min//60}h {total_min%60}m</div></div>", unsafe_allow_html=True)
        
    row3_c1, row3_c2 = st.columns(2)
    
    # 5. 스터디 (Pie Chart - 총 진행률)
    with row3_c1:
        st.markdown(f"<div class='metric-card'><div style='text-align:center; margin-bottom:5px'>📖 스터디</div>", unsafe_allow_html=True)
        s_df = st.session_state.study_sessions
        s_done = s_df['Done'].sum() if 'Done' in s_df.columns else 0
        s_total = s_df['Total'].sum() if 'Total' in s_df.columns else 1
        st.plotly_chart(draw_pie_chart(int(s_done), int(s_total), "Study"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # 6. 프로젝트 (Pie Chart)
    with row3_c2:
        st.markdown(f"<div class='metric-card'><div style='text-align:center; margin-bottom:5px'>💼 프로젝트</div>", unsafe_allow_html=True)
        p_df = st.session_state.project_data
        p_done = p_df['Done'].sum() if 'Done' in p_df.columns else 0
        p_total = p_df['Total'].sum() if 'Total' in p_df.columns else len(p_df)
        st.plotly_chart(draw_pie_chart(int(p_done), int(p_total), "Project"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 7. 습관 트래커 (진행률 표시)
    row4_c1, row4_c2 = st.columns(2)
    with row4_c1:
        st.markdown(f"<div class='metric-card'><div style='text-align:center; margin-bottom:5px'>🎯 습관</div>", unsafe_allow_html=True)
        today_date = datetime.now().date()
        total_habits = len(st.session_state.habits)
        today_done = sum(1 for _, h in st.session_state.habits.iterrows() 
                        if str(today_date) in st.session_state.habit_logs.get(h['Name'], []))
        st.plotly_chart(draw_pie_chart(today_done, total_habits if total_habits > 0 else 1, "Habit"), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# === [2] 학기 관리 ===
with menu[1]:
    st.markdown("### 📚 Semester Curriculum")
    for sem, subjects in st.session_state.semester_progress.items():
        with st.expander(sem, expanded=True):
            cols = st.columns(2)
            for i, (sub, done) in enumerate(subjects.items()):
                checked = cols[i%2].checkbox(sub, value=done, key=f"sem_{sem}_{sub}")
                if checked != done:
                    st.session_state.semester_progress[sem][sub] = checked
                    sync_save_data()
                    st.rerun()

# === [3] 월간 관리 ===
with menu[2]:
    st.markdown("### 📅 Monthly Goals")
    
    # 토글 스위치 (추가 / 관리)
    col_t1, col_t2 = st.columns(2)
    show_add = col_t1.toggle("➕ 추가", key="m_add_t")
    show_manage = col_t2.toggle("⚙️ 관리", key="m_man_t")
    
    if show_add:
        with st.container(border=True):
            new_goal = st.text_input("목표 입력", key="m_input")
            if st.button("등록하기", use_container_width=True, key="m_save"):
                if new_goal:
                    st.session_state.monthly_goals = pd.concat([st.session_state.monthly_goals, pd.DataFrame([{"Goal":new_goal, "Done":False}])], ignore_index=True)
                    sync_save_data()
                    st.rerun()

    if show_manage:
        st.warning("항목을 삭제하려면 아래 버튼을 누르세요.")
        for i, row in st.session_state.monthly_goals.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"#### {row['Goal']}")
            # 여기가 바로 보라색 삭제 버튼이 적용되는 부분
            if c2.button("삭제", key=f"m_del_{i}"):
                st.session_state.monthly_goals = st.session_state.monthly_goals.drop(i).reset_index(drop=True)
                sync_save_data()
                st.rerun()
    else:
        # 일반 보기 모드 - 체크박스로 완료 토글
        for i, row in st.session_state.monthly_goals.iterrows():
            done = st.checkbox(f"🎯 {row['Goal']}", value=row['Done'], key=f"m_chk_{i}")
            if done != row['Done']:
                st.session_state.monthly_goals.at[i, 'Done'] = done
                sync_save_data()
                st.rerun()

# === [4] 주간 관리 ===
with menu[3]:
    st.markdown("### 📆 Weekly Tasks")
    
    col_t1, col_t2 = st.columns(2)
    show_add = col_t1.toggle("➕ 추가", key="w_add_t")
    show_manage = col_t2.toggle("⚙️ 관리", key="w_man_t")
    
    if show_add:
        with st.container(border=True):
            d = st.selectbox("요일", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
            t = st.text_input("할일 입력")
            if st.button("등록하기", use_container_width=True, key="w_save"):
                st.session_state.weekly_tasks = pd.concat([st.session_state.weekly_tasks, pd.DataFrame([{"Day":d, "Task":t, "Done":False}])], ignore_index=True)
                sync_save_data()
                st.rerun()
                
    if show_manage:
        for i, row in st.session_state.weekly_tasks.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{row['Day']}** : {row['Task']}")
            if c2.button("삭제", key=f"w_del_{i}"):
                st.session_state.weekly_tasks = st.session_state.weekly_tasks.drop(i).reset_index(drop=True)
                sync_save_data()
                st.rerun()
    else:
        # 일반 보기 모드 - 체크박스로 완료 토글
        for i, row in st.session_state.weekly_tasks.iterrows():
            done = st.checkbox(f"📅 {row['Day']} : {row['Task']}", value=row['Done'], key=f"w_chk_{i}")
            if done != row['Done']:
                st.session_state.weekly_tasks.at[i, 'Done'] = done
                sync_save_data()
                st.rerun()

# === [5] 데일리 ===
with menu[4]:
    st.markdown("### 📝 Daily Log")
    col_t1, col_t2 = st.columns(2)
    show_add = col_t1.toggle("➕ 추가", key="d_add_t")
    show_manage = col_t2.toggle("⚙️ 관리", key="d_man_t")
    
    if show_add:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            s = c1.text_input("시작", "09:00")
            e = c2.text_input("종료", "11:00")
            a = st.text_input("활동 내용")
            if st.button("기록하기", use_container_width=True):
                st.session_state.daily_time_logs = pd.concat([st.session_state.daily_time_logs, pd.DataFrame([{"StartTime":s, "EndTime":e, "Activity":a, "Category":"Study"}])], ignore_index=True)
                sync_save_data()
                st.rerun()
                
    if show_manage:
        for i, row in st.session_state.daily_time_logs.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"{row['StartTime']}~{row['EndTime']} : {row['Activity']}")
            if c2.button("삭제", key=f"d_del_{i}"):
                st.session_state.daily_time_logs = st.session_state.daily_time_logs.drop(i).reset_index(drop=True)
                sync_save_data()
                st.rerun()
    else:
        # 일반 보기 모드 (카드 스타일)
        for i, row in st.session_state.daily_time_logs.iterrows():
            st.markdown(f"<div class='metric-card' style='padding:12px; display:flex; align-items:center;'><span style='font-size:1rem;'>⏰ <b>{row['StartTime']} ~ {row['EndTime']}</b> : {row['Activity']}</span></div>", unsafe_allow_html=True)
        
    st.markdown("#### 📓 Memo")
    memo = st.text_area("", st.session_state.daily_memo, height=150)
    if memo != st.session_state.daily_memo:
        st.session_state.daily_memo = memo
        sync_save_data()

# === [6] 스터디 ===
with menu[5]:
    st.markdown("### 📖 스터디 플랜")
    col_t1, col_t2 = st.columns(2)
    show_add = col_t1.toggle("➕ 추가", key="s_add_t")
    show_manage = col_t2.toggle("⚙️ 관리", key="s_man_t")
    
    if show_add:
        with st.container(border=True):
            n = st.text_input("스터디 이름")
            t = st.number_input("목표 횟수", min_value=1, max_value=100, value=10)
            if st.button("생성하기", use_container_width=True):
                st.session_state.study_sessions = pd.concat([st.session_state.study_sessions, pd.DataFrame([{"Name":n, "Total":int(t), "Done":0}])], ignore_index=True)
                sync_save_data()
                st.rerun()
                
    if show_manage:
        for i, row in st.session_state.study_sessions.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{row['Name']}**")
            if c2.button("삭제", key=f"s_del_{i}"):
                st.session_state.study_sessions = st.session_state.study_sessions.drop(i).reset_index(drop=True)
                sync_save_data()
                st.rerun()
    else:
        # 일반 보기 모드 - 진행률 조절 가능
        for i, row in st.session_state.study_sessions.iterrows():
            pct = int(row['Done']/row['Total']*100) if row['Total'] > 0 else 0
            
            col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
            col1.markdown(f"**📖 {row['Name']}**")
            col2.markdown(f"<span style='color:{T['accent']}; font-weight:600;'>{int(row['Done'])}/{int(row['Total'])} ({pct}%)</span>", unsafe_allow_html=True)
            
            if col3.button("➖", key=f"s_minus_{i}"):
                st.session_state.study_sessions.at[i, 'Done'] = max(0, row['Done'] - 1)
                sync_save_data()
                st.rerun()
            
            if col4.button("➕", key=f"s_plus_{i}"):
                st.session_state.study_sessions.at[i, 'Done'] = min(row['Total'], row['Done'] + 1)
                sync_save_data()
                st.rerun()
            
            st.progress(pct / 100)

# === [7] 프로젝트 ===
with menu[6]:
    st.markdown("### 💼 Projects")
    col_t1, col_t2 = st.columns(2)
    show_add = col_t1.toggle("➕ 추가", key="p_add_t")
    show_manage = col_t2.toggle("⚙️ 관리", key="p_man_t")
    
    if show_add:
        with st.container(border=True):
            s = st.text_input("프로젝트명")
            t = st.text_input("세부 작업")
            total = st.number_input("목표 단계", min_value=1, max_value=50, value=5)
            d = st.date_input("마감일")
            if st.button("추가하기", use_container_width=True):
                st.session_state.project_data = pd.concat([st.session_state.project_data, pd.DataFrame([{"Subject":s, "Task":t, "Total":int(total), "Done":0, "Deadline":str(d)}])], ignore_index=True)
                sync_save_data()
                st.rerun()
                
    if show_manage:
        for i, row in st.session_state.project_data.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{row['Subject']}** : {row['Task']}")
            if c2.button("삭제", key=f"p_del_{i}"):
                st.session_state.project_data = st.session_state.project_data.drop(i).reset_index(drop=True)
                sync_save_data()
                st.rerun()
    else:
        # 일반 보기 모드 - 진행률 조절 가능
        for i, row in st.session_state.project_data.iterrows():
            total = int(row['Total']) if 'Total' in row else 1
            done = int(row['Done']) if isinstance(row['Done'], (int, float)) else (1 if row['Done'] else 0)
            pct = int(done/total*100) if total > 0 else 0
            
            col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
            col1.markdown(f"**💼 {row['Subject']}** : {row['Task']}")
            col2.markdown(f"<span style='color:{T['accent']}; font-weight:600;'>{done}/{total} ({pct}%)</span>", unsafe_allow_html=True)
            
            if col3.button("➖", key=f"p_minus_{i}"):
                st.session_state.project_data.at[i, 'Done'] = max(0, done - 1)
                sync_save_data()
                st.rerun()
            
            if col4.button("➕", key=f"p_plus_{i}"):
                st.session_state.project_data.at[i, 'Done'] = min(total, done + 1)
                sync_save_data()
                st.rerun()
            
            st.progress(pct / 100)
            st.caption(f"📅 마감: {row['Deadline']}")

# === [8] 습관 트래커 ===
with menu[7]:
    st.markdown("### 🎯 Habit Tracker")
    
    today = str(datetime.now().date())
    
    col_t1, col_t2 = st.columns(2)
    show_add = col_t1.toggle("➕ 추가", key="h_add_t")
    show_manage = col_t2.toggle("⚙️ 관리", key="h_man_t")
    
    if show_add:
        with st.container(border=True):
            icons = ["🏃", "📚", "💧", "🧘", "✍️", "🎵", "💪", "🥗", "😴", "🎯"]
            h_icon = st.selectbox("아이콘", icons)
            h_name = st.text_input("습관 이름")
            h_target = st.number_input("주간 목표 (회)", min_value=1, max_value=7, value=7)
            if st.button("추가하기", use_container_width=True, key="h_save"):
                if h_name:
                    st.session_state.habits = pd.concat([st.session_state.habits, pd.DataFrame([{"Name": h_name, "Icon": h_icon, "Target": int(h_target)}])], ignore_index=True)
                    st.session_state.habit_logs[h_name] = []
                    sync_save_data()
                    st.rerun()
    
    if show_manage:
        for i, row in st.session_state.habits.iterrows():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"{row['Icon']} **{row['Name']}**")
            if c2.button("삭제", key=f"h_del_{i}"):
                habit_name = row['Name']
                st.session_state.habits = st.session_state.habits.drop(i).reset_index(drop=True)
                if habit_name in st.session_state.habit_logs:
                    del st.session_state.habit_logs[habit_name]
                sync_save_data()
                st.rerun()
    else:
        # 습관별 체크인 UI
        for i, row in st.session_state.habits.iterrows():
            habit_name = row['Name']
            logs = st.session_state.habit_logs.get(habit_name, [])
            
            # 최근 7일 완료 횟수 계산 (스트릭 표시와 일치)
            seven_days_ago = datetime.now().date() - timedelta(days=6)
            recent_logs = [d for d in logs if d >= str(seven_days_ago)]
            done_count = len(recent_logs)
            target = int(row['Target'])
            pct = min(100, int(done_count / target * 100))
            
            # 오늘 체크 여부
            checked_today = today in logs
            
            st.markdown(f"---")
            col1, col2, col3 = st.columns([3, 2, 1])
            
            col1.markdown(f"### {row['Icon']} {habit_name}")
            col2.markdown(f"<span style='color:{T['accent']}; font-size:1.2rem;'>{done_count}/{target} 최근 7일</span>", unsafe_allow_html=True)
            
            # 체크인 버튼 (토글 가능)
            # 완료(Red)는 secondary 타입 + CSS, 미완료(SkyBlue)는 primary 타입
            btn_label = "✅ 완료" if checked_today else "체크인"
            
            # 색상 제어를 위한 글로벌 CSS (한 번만 선언해도 되지만 구조상 여기 유지)
            st.markdown(f"""
                <style>
                /* [미완료/하늘색] Primary 버튼 스타일 덮어쓰기 */
                div.stButton > button[kind="primary"] {{
                    background-color: {T['accent']} !important;
                    color: white !important;
                    border: none !important;
                    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3) !important;
                }}
                /* [완료/빨간색] Secondary 버튼 스타일 덮어쓰기 */
                div.stButton > button[kind="secondary"] {{
                    background-color: #FF4B4B !important;
                    color: white !important;
                    border: none !important;
                    box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3) !important;
                }}
                /* 호버 효과 */
                div.stButton > button:hover {{
                    opacity: 0.8 !important;
                    transform: translateY(-1px) !important;
                }}
                </style>
            """, unsafe_allow_html=True)

            if col3.button(btn_label, key=f"h_check_{i}", type="secondary" if checked_today else "primary", use_container_width=True):
                if habit_name not in st.session_state.habit_logs:
                    st.session_state.habit_logs[habit_name] = []
                
                if checked_today:
                    st.session_state.habit_logs[habit_name].remove(today)
                else:
                    if today not in st.session_state.habit_logs[habit_name]:
                        st.session_state.habit_logs[habit_name].append(today)
                sync_save_data()
                st.rerun()
            
            # 스트릭 (최근 7일 - 클릭하여 토글 가능)
            streak_cols = st.columns(7)
            for d in range(6, -1, -1):
                day = datetime.now().date() - timedelta(days=d)
                day_str = str(day)
                day_name = ["월", "화", "수", "목", "금", "토", "일"][day.weekday()]
                is_done = day_str in logs
                with streak_cols[6-d]:
                    # 완료된 날은 secondary(빨강), 미완료는 primary(하늘색)
                    s_label = f"{day_name}\n✓" if is_done else f"{day_name}\n-"
                    if st.button(s_label, key=f"h_day_{i}_{d}", type="secondary" if is_done else "primary", use_container_width=True):
                        if habit_name not in st.session_state.habit_logs:
                            st.session_state.habit_logs[habit_name] = []
                        
                        if is_done:
                            st.session_state.habit_logs[habit_name].remove(day_str)
                        else:
                            st.session_state.habit_logs[habit_name].append(day_str)
                        sync_save_data()
                        st.rerun()
            
            st.progress(pct / 100)