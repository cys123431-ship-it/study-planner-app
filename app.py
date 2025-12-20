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
# 2. 테마 시스템 및 디자인
# ---------------------------------------------------------
if 'theme' not in st.session_state:
    st.session_state.theme = 'auto'

# 색상 팔레트 정의
THEMES = {
    'light': {
        'bg_main': '#f8f9fa',
        'bg_sidebar': '#ffffff',
        'bg_card': '#ffffff',
        'text_primary': '#1a1a2e',
        'text_secondary': '#6c757d',
        'border': '#e0e0e0',
        'card_shadow': 'rgba(0, 0, 0, 0.08)',
    },
    'dark': {
        'bg_main': '#0a0a12',
        'bg_sidebar': '#121220',
        'bg_card': '#1a1a2e', 
        'text_primary': '#ffffff', 
        'text_secondary': '#b0b0c0',
        'border': '#3a3a5a',
        'card_shadow': 'rgba(0, 0, 0, 0.4)',
    }
}

ACCENT_COLOR = "#6C63FF"
ACCENT_DARK = "#5449CC"

def get_theme():
    if st.session_state.theme == 'auto': return 'light'
    return st.session_state.theme

theme = get_theme()
T = THEMES[theme]

# ---------------------------------------------------------
# [핵심 수정] CSS 스타일링
# ---------------------------------------------------------
# 다크 모드일 때 삭제 버튼 디자인을 이미지와 똑같이 강제 적용
dark_mode_button_css = """
    /* 다크모드 삭제 버튼 (마지막 컬럼의 버튼) 스타일 강제 적용 */
    div[data-testid="column"]:last-child button {
        background-color: #161622 !important;   /* 아주 어두운 남색 배경 */
        color: #ffffff !important;              /* 완전 흰색 텍스트 */
        border: 1px solid #3a3a5a !important;   /* 은은한 테두리 */
        border-radius: 8px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        font-weight: 700 !important;            /* 글자 굵게 */
        letter-spacing: 0.5px !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    /* 버튼 내부 텍스트(p태그)도 강제로 흰색 */
    div[data-testid="column"]:last-child button p,
    div[data-testid="column"]:last-child button div {
        color: #ffffff !important;
    }

    /* 호버 효과: 약간 밝아지며 텍스트에 붉은빛(삭제 경고) */
    div[data-testid="column"]:last-child button:hover {
        background-color: #1e1e2e !important;
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.2) !important; /* 붉은 글로우 효과 */
    }
    
    div[data-testid="column"]:last-child button:hover p {
        color: #ff4b4b !important;
    }
"""

light_mode_button_css = """
    div[data-testid="column"]:last-child button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="column"]:last-child button:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
        background-color: #fff5f5 !important;
    }
"""

# 현재 테마에 맞는 버튼 CSS 선택
current_button_css = dark_mode_button_css if theme == 'dark' else light_mode_button_css

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {{
        --bg-main: {T['bg_main']};
        --text-primary: {T['text_primary']};
    }}
    
    /* 기본 배경 및 텍스트 설정 */
    .stApp {{
        background-color: {T['bg_main']} !important;
        color: {T['text_primary']} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    /* 다크모드일 때 모든 텍스트 강제 흰색 (브라우저 기본값 덮어쓰기) */
    {'p, span, h1, h2, h3, h4, label, .stMarkdown, .stMarkdown p { color: #ffffff !important; }' if theme == 'dark' else ''}

    /* 사이드바 */
    section[data-testid="stSidebar"] {{
        background-color: {T['bg_sidebar']} !important;
        border-right: 1px solid {T['border']};
    }}
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {{
        color: {T['text_primary']} !important;
    }}
    
    /* 메뉴(라디오 버튼) 스타일 */
    .stRadio > div > label {{
        background: {T['bg_card']};
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 4px;
        border: 1px solid transparent;
        transition: all 0.2s;
    }}
    .stRadio > div > label:hover {{
        border-color: {ACCENT_COLOR};
    }}
    .stRadio > div > label[data-checked="true"] {{
        background: linear-gradient(135deg, {ACCENT_COLOR}, {ACCENT_DARK});
        color: white !important;
    }}
    .stRadio > div > label[data-checked="true"] span {{
        color: white !important;
    }}

    /* 카드 스타일 */
    .card {{
        background-color: {T['bg_card']};
        border: 1px solid {T['border']};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px {T['card_shadow']};
    }}
    
    /* 메인 버튼 스타일 */
    .stButton > button {{
        background: {ACCENT_COLOR};
        color: white !important;
        border: none;
        height: 45px;
        font-weight: 600;
        border-radius: 8px;
    }}

    /* 데이터프레임 및 인풋 필드 */
    [data-testid="stDataFrame"], .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
        background-color: {T['bg_card']} !important;
        color: {T['text_primary']} !important;
        border-color: {T['border']} !important;
    }}
    
    /* 삭제 버튼 스타일 주입 (가장 마지막에 적용) */
    {current_button_css}
    
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 데이터 (Session State)
# ---------------------------------------------------------
if 'project_data' not in st.session_state:
    st.session_state.project_data = pd.DataFrame([
        {"Subject": "캡스톤디자인1", "Task": "주제 선정 및 기획안 작성", "Done": True, "Deadline": "2026-03-15", "Priority": "High"},
        {"Subject": "자료구조", "Task": "연결 리스트 구현 실습", "Done": False, "Deadline": "2026-03-20", "Priority": "Medium"},
        {"Subject": "개인공부", "Task": "정보처리기사 실기 기출 1회독", "Done": False, "Deadline": "2026-04-15", "Priority": "High"},
    ])

if 'monthly_goals' not in st.session_state:
    st.session_state.monthly_goals = pd.DataFrame([
        {"Goal": "C언어 포인터 완벽 이해", "Done": True},
        {"Goal": "매일 아침 1시간 코딩", "Done": False},
        {"Goal": "전공 서적 1권 완독", "Done": False},
    ])

if 'weekly_tasks' not in st.session_state:
    st.session_state.weekly_tasks = pd.DataFrame([
        {"Day": "Mon", "Task": "자료구조 강의 수강", "Done": True},
        {"Day": "Tue", "Task": "알고리즘 문제 3개 풀기", "Done": True},
        {"Day": "Wed", "Task": "정처기 요약본 암기", "Done": False},
        {"Day": "Thu", "Task": "프로젝트 코드 리팩토링", "Done": False},
        {"Day": "Fri", "Task": "주간 복습", "Done": False},
    ])

if 'daily_time_logs' not in st.session_state:
    st.session_state.daily_time_logs = pd.DataFrame([
        {"StartTime": "09:00", "EndTime": "11:00", "Activity": "자료구조 인강", "Category": "Study"},
        {"StartTime": "14:00", "EndTime": "17:00", "Activity": "코딩 실습", "Category": "Practice"},
    ])

if 'study_sessions' not in st.session_state:
    st.session_state.study_sessions = pd.DataFrame([
        {"Name": "알고리즘 스터디", "Schedule": "매주 화요일 19:00", "TotalSessions": 10, "CompletedSessions": 8, "Status": "Active"},
        {"Name": "정처기 스터디", "Schedule": "매주 목요일 20:00", "TotalSessions": 12, "CompletedSessions": 3, "Status": "Active"},
    ])

if 'semester_progress' not in st.session_state:
    st.session_state.semester_progress = {
        "1-1 (2026 Spring)": {"기초C프로그래밍": False, "자바프로그래밍": False, "자료구조(Core)": False, "컴퓨터구조": False, "데이터통신": False, "캡스톤디자인1": False},
        "1-2 (2026 Fall)": {"데이터베이스(Core)": False, "운영체제": False, "소프트웨어공학": False, "정보보호학개론": False, "논리회로": False, "캡스톤디자인2": False},
        "2-1 (2027 Spring)": {"네트워크보안": False, "운영체제보안": False, "데이터베이스보안": False, "컴퓨터네트워크": False, "진로지도": False},
        "2-2 (2027 Fall)": {"알고리즘(7급)": False, "리눅스보안": False, "SW취약점분석": False, "졸업지도": False}
    }
if 'daily_memo' not in st.session_state:
    st.session_state.daily_memo = ""

# ---------------------------------------------------------
# 4. 사이드바 UI
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"<h1 style='text-align:center; color:{T['text_primary']}'>🧭 Navigators</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{T['text_secondary']}; font-size:0.8rem'>CS Transfer Student</p>", unsafe_allow_html=True)
    
    # 테마 선택
    st.write("🎨 Theme")
    theme_options = {"🌙 Dark": "dark", "☀️ Light": "light", "🔄 Auto": "auto"}
    curr_theme_idx = list(theme_options.values()).index(st.session_state.theme)
    sel = st.radio("Theme", list(theme_options.keys()), index=curr_theme_idx, label_visibility="collapsed")
    
    if theme_options[sel] != st.session_state.theme:
        st.session_state.theme = theme_options[sel]
        st.rerun()
        
    st.divider()
    
    # D-Day
    d_day = (datetime(2026, 4, 15) - datetime.now()).days
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, {ACCENT_COLOR}, {ACCENT_DARK}); padding: 15px; border-radius: 12px; text-align: center; color: white;">
            <div style="font-size: 0.8rem; opacity: 0.9">📅 정보처리기사 실기</div>
            <div style="font-size: 1.8rem; font-weight: 800">D-{d_day}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    menu = st.radio("Menu", ["📚 Semester", "📅 Monthly", "📆 Weekly", "📝 Daily", "👥 Study", "💼 Project"], label_visibility="collapsed")

# ---------------------------------------------------------
# 5. 메인 콘텐츠
# ---------------------------------------------------------

# === [1] Semester ===
if menu == "📚 Semester":
    st.title("📚 2-Year Curriculum")
    total = sum(len(v) for v in st.session_state.semester_progress.values())
    done = sum(sum(1 for x in v.values() if x) for v in st.session_state.semester_progress.values())
    
    st.markdown(f"""
        <div style="background:linear-gradient(135deg, {ACCENT_COLOR}, {ACCENT_DARK}); padding:20px; border-radius:16px; text-align:center; color:white; box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);">
            <h2 style="margin:0; font-size:2.5rem; color:white !important;">{int(done/total*100)}%</h2>
            <p style="margin:0; opacity:0.9; color:white !important;">전체 이수율 ({done}/{total})</p>
        </div>
        <br>
    """, unsafe_allow_html=True)
    
    for sem, sub in st.session_state.semester_progress.items():
        s_done = sum(1 for v in sub.values() if v)
        with st.expander(f"{sem} — {int(s_done/len(sub)*100)}%"):
            cols = st.columns(3)
            for i, (k, v) in enumerate(sub.items()):
                st.session_state.semester_progress[sem][k] = cols[i%3].checkbox(k, value=v, key=f"{sem}_{k}")

# === [2] Monthly ===
elif menu == "📅 Monthly":
    st.title(f"📅 {datetime.now().strftime('%B %Y')}")
    df = st.session_state.monthly_goals
    done = len(df[df['Done']])
    
    c1, c2 = st.columns([1, 2])
    with c1:
        fig = go.Figure(data=[go.Pie(values=[done, len(df)-done], hole=0.75, marker_colors=[ACCENT_COLOR, T['border']], textinfo='none')])
        fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=180, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        c_a, c_b = st.columns(2)
        add = c_a.toggle("➕ 추가", key="m_add")
        manage = c_b.toggle("⚙️ 관리", key="m_man")
        
        if add:
            with st.form("new_month"):
                g = st.text_input("목표")
                if st.form_submit_button("등록") and g:
                    st.session_state.monthly_goals = pd.concat([df, pd.DataFrame([{"Goal": g, "Done": False}])], ignore_index=True)
                    st.rerun()
        
        if manage:
            st.info("🗑️ 삭제 버튼을 눌러 항목을 제거하세요.")
            for i, r in df.iterrows():
                mc1, mc2 = st.columns([4, 1])
                mc1.markdown(f"**{r['Goal']}**")
                # 여기서 CSS가 적용된 삭제 버튼이 렌더링됨
                if mc2.button("삭제", key=f"md_{i}", use_container_width=True):
                    st.session_state.monthly_goals = df.drop(i).reset_index(drop=True)
                    st.rerun()
        else:
            st.session_state.monthly_goals = st.data_editor(df, column_config={"Done": st.column_config.CheckboxColumn(width="small")}, hide_index=True, use_container_width=True)

# === [3] Weekly ===
elif menu == "📆 Weekly":
    st.title("📆 Weekly Tasks")
    df = st.session_state.weekly_tasks
    done_cnt = len(df[df['Done']])
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("진행률", f"{int(done_cnt/len(df)*100 if len(df) else 0)}%")
    c2.metric("완료", done_cnt)
    c3.metric("미완료", len(df)-done_cnt)
    
    st.divider()
    
    wa, wb = st.columns(2)
    add = wa.toggle("➕ 추가", key="w_add")
    manage = wb.toggle("⚙️ 관리", key="w_man")
    
    if add:
        with st.form("new_week"):
            col_a, col_b = st.columns([1, 3])
            d = col_a.selectbox("요일", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
            t = col_b.text_input("할일")
            if st.form_submit_button("등록") and t:
                st.session_state.weekly_tasks = pd.concat([df, pd.DataFrame([{"Day": d, "Task": t, "Done": False}])], ignore_index=True)
                st.rerun()

    if manage:
        st.info("🗑️ 삭제 버튼을 눌러 항목을 제거하세요.")
        for i, r in df.iterrows():
            wc1, wc2, wc3 = st.columns([1, 4, 1])
            wc1.write(r['Day'])
            wc2.write(r['Task'])
            if wc3.button("삭제", key=f"wd_{i}", use_container_width=True):
                st.session_state.weekly_tasks = df.drop(i).reset_index(drop=True)
                st.rerun()
    else:
        st.session_state.weekly_tasks = st.data_editor(
            df, 
            column_config={
                "Done": st.column_config.CheckboxColumn(width="small"),
                "Day": st.column_config.SelectboxColumn(options=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], width="small")
            }, 
            hide_index=True, 
            use_container_width=True
        )

# === [4] Daily ===
elif menu == "📝 Daily":
    st.title("📝 Daily Log")
    df = st.session_state.daily_time_logs
    
    da, db = st.columns(2)
    add = da.toggle("➕ 기록", key="d_add")
    manage = db.toggle("⚙️ 관리", key="d_man")
    
    if add:
        with st.form("new_log"):
            c1, c2 = st.columns(2)
            s = c1.text_input("시작", "09:00")
            e = c2.text_input("종료", "11:00")
            a = st.text_input("활동")
            cat = st.selectbox("분류", ["Study", "Practice", "Project"])
            if st.form_submit_button("저장") and a:
                st.session_state.daily_time_logs = pd.concat([df, pd.DataFrame([{"StartTime":s, "EndTime":e, "Activity":a, "Category":cat}])], ignore_index=True)
                st.rerun()
                
    if manage:
        st.info("🗑️ 삭제 버튼을 눌러 항목을 제거하세요.")
        for i, r in df.iterrows():
            dc1, dc2, dc3 = st.columns([2, 4, 1])
            dc1.write(f"{r['StartTime']}~{r['EndTime']}")
            dc2.write(f"[{r['Category']}] {r['Activity']}")
            if dc3.button("삭제", key=f"dd_{i}", use_container_width=True):
                st.session_state.daily_time_logs = df.drop(i).reset_index(drop=True)
                st.rerun()
    else:
        st.session_state.daily_time_logs = st.data_editor(df, hide_index=True, use_container_width=True)
        
    st.subheader("Today's Memo")
    st.session_state.daily_memo = st.text_area("Memo", st.session_state.daily_memo, height=150)

# === [5] Study ===
elif menu == "👥 Study":
    st.title("👥 Study Sessions")
    df = st.session_state.study_sessions
    
    for i, r in df.iterrows():
        p = int(r['CompletedSessions']/r['TotalSessions']*100) if r['TotalSessions'] else 0
        st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between">
                    <h3 style="margin:0">{r['Name']}</h3>
                    <span style="background:{ACCENT_COLOR}30; color:{ACCENT_COLOR}; padding:2px 8px; border-radius:10px; font-size:0.8rem">{r['Status']}</span>
                </div>
                <p style="color:{T['text_secondary']}; margin:4px 0">{r['Schedule']}</p>
                <div style="background:{T['border']}; height:8px; border-radius:4px; margin-top:8px">
                    <div style="background:{ACCENT_COLOR}; width:{p}%; height:100%; border-radius:4px"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    sa, sb = st.columns(2)
    add = sa.toggle("➕ 추가", key="s_add")
    manage = sb.toggle("⚙️ 관리", key="s_man")
    
    if add:
        with st.form("new_study"):
            n = st.text_input("이름")
            sc = st.text_input("일정")
            if st.form_submit_button("생성") and n:
                st.session_state.study_sessions = pd.concat([df, pd.DataFrame([{"Name":n, "Schedule":sc, "TotalSessions":10, "CompletedSessions":0, "Status":"Active"}])], ignore_index=True)
                st.rerun()
                
    if manage:
        st.info("🗑️ 삭제 버튼을 눌러 항목을 제거하세요.")
        for i, r in df.iterrows():
            sc1, sc2, sc3 = st.columns([3, 3, 1])
            sc1.write(r['Name'])
            sc2.write(r['Schedule'])
            if sc3.button("삭제", key=f"sd_{i}", use_container_width=True):
                st.session_state.study_sessions = df.drop(i).reset_index(drop=True)
                st.rerun()
    else:
        st.session_state.study_sessions = st.data_editor(df, hide_index=True, use_container_width=True)

# === [6] Project ===
elif menu == "💼 Project":
    st.title("💼 Projects")
    df = st.session_state.project_data
    
    # Task Cards
    for i, r in df.iterrows():
        done_style = "opacity:0.6; text-decoration:line-through" if r['Done'] else ""
        st.markdown(f"""
            <div class="card" style="{done_style}">
                <span style="background:{T['border']}; font-size:0.7rem; padding:2px 6px; border-radius:4px">{r['Priority']}</span>
                <span style="float:right; font-weight:bold; color:{ACCENT_COLOR}">{r['Deadline']}</span>
                <h4 style="margin:8px 0; color:{T['text_primary']}">{r['Subject']}</h4>
                <p style="margin:0; color:{T['text_secondary']}">{r['Task']}</p>
            </div>
        """, unsafe_allow_html=True)
        
    pa, pb = st.columns(2)
    add = pa.toggle("➕ 추가", key="p_add")
    manage = pb.toggle("⚙️ 관리", key="p_man")
    
    if add:
        with st.form("new_proj"):
            s = st.text_input("과목")
            t = st.text_input("할일")
            if st.form_submit_button("추가") and s:
                st.session_state.project_data = pd.concat([df, pd.DataFrame([{"Subject":s, "Task":t, "Done":False, "Deadline":"2026-12-31", "Priority":"Medium"}])], ignore_index=True)
                st.rerun()
                
    if manage:
        st.info("🗑️ 삭제 버튼을 눌러 항목을 제거하세요.")
        for i, r in df.iterrows():
            pc1, pc2, pc3 = st.columns([2, 4, 1])
            pc1.write(r['Subject'])
            pc2.write(r['Task'])
            if pc3.button("삭제", key=f"pd_{i}", use_container_width=True):
                st.session_state.project_data = df.drop(i).reset_index(drop=True)
                st.rerun()
    else:
        st.session_state.project_data = st.data_editor(df, column_config={"Done":st.column_config.CheckboxColumn(width="small")}, hide_index=True, use_container_width=True)