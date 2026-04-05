import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from database import (
    get_schedules_with_details, get_members, get_schedule_participants, get_member_stats,
    add_schedule, add_match_team, update_schedule, delete_schedule,
    add_member, update_member, delete_member,
    add_participant, remove_participant,
    get_schedule_participants_detailed, update_schedule_participants,
    add_guest_member, delete_guest_member
)

# 메뉴 모듈 import
from menu.view import show_schedule_view
from menu.schedule import show_schedule_management
from menu.members import show_member_management
from menu.stats import show_member_stats
from menu.admin import show_admin_menu

st.set_page_config(
    page_title="FC Stars⭐ - Management",    
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("FC Stars⭐ - Management System")
st.markdown("팀 일정 및 멤버 관리 시스템")

# 전체 UI 폰트 크기 조정 CSS
st.markdown("""
<style>
    /* 전체 폰트 크기 증가 */
    .main * {
        font-size: 16px !important;
    }
    
    /* 헤더 폰트 크기 조정 */
    h1 {
        font-size: 2.0em !important;
    }
    h2, h3, h4, h5, h6 {
        font-size: 1.3em !important;
    }
    
    /* 사이드바 폰트 크기 증가 */
    .sidebar .sidebar-content * {
        font-size: 16px !important;
    }
    
    /* 버튼 폰트 크기 증가 */
    .stButton button {
        font-size: 16px !important;
        padding: 8px 16px !important;
    }
    
    /* 데이터프레임 폰트 크기 증가 */
    .dataframe {
        font-size: 16px !important;
    }
    
    /* 입력 필드 폰트 크기 증가 */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        font-size: 16px !important;
    }
    
    /* 라벨 폰트 크기 증가 */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label {
        font-size: 16px !important;
    }
    
    /* 메트릭 폰트 크기 증가 */
    .metric-container {
        font-size: 16px !important;
    }
    
    /* 캡션 폰트 크기 증가 */
    .caption {
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 메뉴
with st.sidebar:  

    # 메뉴 버튼들
    menu_options = {
        "📅 일정 보기": "view",
        "⚽ 일정 관리": "schedule",
        "👥 멤버 관리": "members",
        "📊 통계": "stats",
        "🔧 관리자": "admin"
    }

    # 세션 상태에 선택된 메뉴 저장
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = "view"

    # 메뉴 버튼들 생성
    for menu_name, menu_key in menu_options.items():
        if st.button(menu_name, key=f"menu_{menu_key}",
                    use_container_width=True,
                    type="primary" if st.session_state.selected_menu == menu_key else "secondary"):
            st.session_state.selected_menu = menu_key
            st.rerun()

    menu_key = st.session_state.selected_menu

# 데이터베이스에서 일정 데이터 불러오기 (공통)
schedules_data = get_schedules_with_details()
schedule_df = pd.DataFrame([
    {
        "ID": s["id"],
        "Date": s["date"],
        "Type": "⚽ Match" if s["type"] == "match" else "🏃 Practice",
        "Opponent": s["opponent"] or "",
        "Location": s["location"],
        "Result": s["result"] or "",
        "Participants": s["participants"],
        "Skill_Level": s["skill_level"] or "",
        "Age_Group": s["age_group"] or "",
        "Manner_Score": s["manner_score"] or 0,
    }
    for s in schedules_data
])

# 멤버 데이터도 공통으로 불러오기
members_data = get_members()
members_df = pd.DataFrame(members_data)

# 메뉴에 따른 컨텐츠 표시
if menu_key == "view":
    show_schedule_view(schedule_df, members_df)

elif menu_key == "schedule":
    show_schedule_management(schedule_df, members_data)

elif menu_key == "members":
    show_member_management(members_df)

elif menu_key == "stats":
    show_member_stats(members_data)

elif menu_key == "admin":
    show_admin_menu()
