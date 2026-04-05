import streamlit as st
import pandas as pd
import altair as alt
from database import get_member_stats

def show_member_stats(members_data):
    st.header("📊 멤버 통계")
    member_stats = get_member_stats()
    if member_stats:
        stats_df = pd.DataFrame(member_stats)
        # NULL 값을 0으로 변환 (경기당 골/어시스트가 표시되도록)
        stats_df['goals_per_match'] = stats_df['goals_per_match'].fillna(0)
        stats_df['assists_per_match'] = stats_df['assists_per_match'].fillna(0)
        st.dataframe(
            stats_df,
            use_container_width=True,
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
            }
        )

        # 막대 그래프 추가
        st.subheader("📈 통계 그래프")

        # 그래프 타입 선택
        chart_type = st.selectbox(
            "그래프 타입 선택",
            ["출석일수", "총 골 수", "총 어시스트 수", "경기당 골", "경기당 어시스트"],
            key="chart_type"
        )

        # Altair를 사용한 막대 그래프
        if chart_type == "출석일수":
            chart = alt.Chart(stats_df).mark_bar(color='skyblue').encode(
                x=alt.X('name:N', title='멤버 이름', sort='-y', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('attendance_days:Q', title='출석일수', axis=alt.Axis(labelAngle=0)),
                tooltip=['name:N', 'position:N', 'attendance_days:Q']
            ).properties(
                title="멤버별 출석일수",
                width='container',
                height=400
            )
        elif chart_type == "총 골 수":
            chart = alt.Chart(stats_df).mark_bar(color='lightgreen').encode(
                x=alt.X('name:N', title='멤버 이름', sort='-y', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('goals:Q', title='총 골 수', axis=alt.Axis(labelAngle=0)),
                tooltip=['name:N', 'position:N', 'goals:Q']
            ).properties(
                title="멤버별 총 골 수",
                width='container',
                height=400
            )
        elif chart_type == "총 어시스트 수":
            chart = alt.Chart(stats_df).mark_bar(color='purple').encode(
                x=alt.X('name:N', title='멤버 이름', sort='-y', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('assists:Q', title='총 어시스트 수', axis=alt.Axis(labelAngle=0)),
                tooltip=['name:N', 'position:N', 'assists:Q']
            ).properties(
                title="멤버별 총 어시스트 수",
                width='container',
                height=400
            )
        elif chart_type == "경기당 골":
            chart = alt.Chart(stats_df).mark_bar(color='orange').encode(
                x=alt.X('name:N', title='멤버 이름', sort='-y', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('goals_per_match:Q', title='경기당 골', axis=alt.Axis(labelAngle=0)),
                tooltip=['name:N', 'position:N', 'goals_per_match:Q']
            ).properties(
                title="멤버별 경기당 골",
                width='container',
                height=400
            )
        else:  # 경기당 어시스트
            chart = alt.Chart(stats_df).mark_bar(color='pink').encode(
                x=alt.X('name:N', title='멤버 이름', sort='-y', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('assists_per_match:Q', title='경기당 어시스트', axis=alt.Axis(labelAngle=0)),
                tooltip=['name:N', 'position:N', 'assists_per_match:Q']
            ).properties(
                title="멤버별 경기당 어시스트",
                width='container',
                height=400
            )

        st.altair_chart(chart, use_container_width=True)

        # 멤버별 상세 정보
        with st.expander("멤버 상세 정보", expanded=False):
            for member in members_data:
                with st.container():
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        st.subheader(f"{member['name']}")
                        st.caption(f"직책: {member['position']}")
                        if member['birth_year']:
                            st.caption(f"출생년도: {member['birth_year']}년")
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