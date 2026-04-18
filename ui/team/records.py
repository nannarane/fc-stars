import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from settings import USE_FIRESTORE
from utils.factory import get_member_repository

# ALTair 차트 높이 설정
ALTAIR_CHART_HEIGHT = 380

member_repo = get_member_repository()
member_stats = member_repo.list_members()

# 게스트 멤버는 기록에서 제외
member_stats_no_guest = [
    member for member in member_stats
    if not member.get("isGuest", member.get("is_guest", False))
]

member_stats = member_stats_no_guest

st.header("📊 기록")
st.caption("팀원들의 경기 기록과 통계를 확인할 수 있습니다. ( 모든 기록은 매치 출석일 기준으로 계산되며, 게스트는 기록에서 제외됩니다. )")
st.write(" ") # 빈 줄 추가

if member_stats:
    stats_df = pd.DataFrame(member_stats)
    
    if USE_FIRESTORE:
        # NULL 값을 0으로 변환 (경기당 골/어시스트 계산용)
        stats_df['attendance_days'] = stats_df['attendanceDays'].fillna(0)
        attendance_nonzero = stats_df['attendance_days'].replace(0, np.nan)
        stats_df['goals_per_match'] = (stats_df['goals'] / attendance_nonzero).round(2).fillna(0)
        stats_df['assists_per_match'] = (stats_df['assists'] / attendance_nonzero).round(2).fillna(0)
    else:
        # NULL 값을 0으로 변환 (경기당 골/어시스트가 표시되도록)
        stats_df['goals_per_match'] = stats_df['goals_per_match'].fillna(0)
        stats_df['assists_per_match'] = stats_df['assists_per_match'].fillna(0)

    st.dataframe(
        stats_df,
        width="stretch",
        hide_index=True,
        column_config={            
            "name": st.column_config.TextColumn("이름"),
            "position": st.column_config.TextColumn("직책"),
            "attendance_days": st.column_config.NumberColumn("출석일수"),
            "goals": st.column_config.NumberColumn("총 골 수"),
            "assists": st.column_config.NumberColumn("총 어시스트 수"),
            "goals_per_match": st.column_config.NumberColumn(
                "경기당 골",
                format="%.2f"
            ),
            "assists_per_match": st.column_config.NumberColumn(
                "경기당 어시스트",
                format="%.2f"
            )            
        },
        column_order=["name", "position", "attendance_days", "goals", "assists", "goals_per_match", "assists_per_match"]
    )

    st.divider()

    # 막대 그래프 추가
    st.subheader("📈 통계")
    st.caption("유형별 통계를 시각적으로 확인할 수 있습니다.")
    
    # 그래프 타입 선택
    chart_type = st.selectbox(
        "유형",
        ["출석일수", "총 골 수", "총 어시스트 수", "경기당 골", "경기당 어시스트"],
        key="chart_type",
        label_visibility="hidden"
    )

    st.divider()

    # Altair를 사용한 막대 그래프
    if chart_type == "출석일수":
        chart = alt.Chart(stats_df).mark_bar(color='skyblue').encode(
            x=alt.X('name:N', title='이름', sort='-y', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('attendance_days:Q', title='출석일수', axis=alt.Axis(labelAngle=0)),
            tooltip=['name:N', 'position:N', 'attendance_days:Q']
        ).properties(
            title="출석일수",
            width='container',
            height=ALTAIR_CHART_HEIGHT
        )
    elif chart_type == "총 골 수":
        chart = alt.Chart(stats_df).mark_bar(color='lightgreen').encode(
            x=alt.X('name:N', title='이름', sort='-y', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('goals:Q', title='총 골 수', axis=alt.Axis(labelAngle=0)),
            tooltip=['name:N', 'position:N', 'goals:Q']
        ).properties(
            title="총 골 수",
            width='container',
            height=ALTAIR_CHART_HEIGHT
        )
    elif chart_type == "총 어시스트 수":
        chart = alt.Chart(stats_df).mark_bar(color='purple').encode(
            x=alt.X('name:N', title='이름', sort='-y', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('assists:Q', title='총 어시스트 수', axis=alt.Axis(labelAngle=0)),
            tooltip=['name:N', 'position:N', 'assists:Q']
        ).properties(
            title="총 어시스트 수",
            width='container',
            height=ALTAIR_CHART_HEIGHT
        )
    elif chart_type == "경기당 골":
        chart = alt.Chart(stats_df).mark_bar(color='orange').encode(
            x=alt.X('name:N', title='이름', sort='-y', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('goals_per_match:Q', title='경기당 골', axis=alt.Axis(labelAngle=0)),
            tooltip=['name:N', 'position:N', 'goals_per_match:Q']
        ).properties(
            title="경기당 골",
            width='container',
            height=ALTAIR_CHART_HEIGHT
        )
    else:  # 경기당 어시스트
        chart = alt.Chart(stats_df).mark_bar(color='pink').encode(
            x=alt.X('name:N', title='이름', sort='-y', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('assists_per_match:Q', title='경기당 어시스트', axis=alt.Axis(labelAngle=0)),
            tooltip=['name:N', 'position:N', 'assists_per_match:Q']
        ).properties(
            title="경기당 어시스트",
            width='container',
            height=ALTAIR_CHART_HEIGHT
        )

    st.altair_chart(chart, width="stretch")

    st.divider()

    st.subheader("👤 팀원 기록 정보")
    st.caption("각 팀원의 상세한 기록과 통계를 확인할 수 있습니다.")
    st.write(" ") # 빈 줄 추가

    # 팀원 상세 정보
    with st.expander("기록 정보", expanded=False, icon="ℹ️"):
        for member in member_stats:
            if USE_FIRESTORE:
                # NULL 값을 0으로 변환 (경기당 골/어시스트가 표시되도록)
                member['attendance_days'] = member['attendanceDays'] if member['attendanceDays'] is not None else 0
            with st.container():
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.subheader(f"{member['name']}")
                    st.caption(f"직책: {member['position']}")                    
                    st.caption(f"출생년도: {member['birthYear'] if member['isGuest'] == False else ""}")
                with col2:
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("출석일수", member['attendance_days'])
                    with m2:
                        st.metric("총 골 수", member['goals'])
                    with m3:
                        st.metric("총 어시스트 수", member['assists'])
                    with m4:
                        goals_per_match = member['goals'] / member['attendance_days'] if member['attendance_days'] > 0 else 0
                        assists_per_match = member['assists'] / member['attendance_days'] if member['attendance_days'] > 0 else 0
                        st.metric("경기당 골/어시", f"{goals_per_match:.1f}/{assists_per_match:.1f}")
            st.divider()
else:
    st.info("멤버 데이터가 없습니다.")