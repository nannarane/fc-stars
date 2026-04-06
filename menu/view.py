import streamlit as st
import pandas as pd
from database import get_schedule_participants
from streamlit_calendar import calendar

def show_schedule_view(schedule_df, members_df):
    st.header("📅 일정")
    st.markdown("매치 및 연습 경기 일정을 확인하세요.")

    # 필터링 옵션들
    with st.expander("🔍 검색", expanded=True):
        col1, col2 = st.columns(2)
        col3, col4, col5 = st.columns(3)

        with col1:
            selected_types = st.multiselect(
                "일정 종류",
                options=["⚽ Match", "🏃 Practice"],
                default=["⚽ Match", "🏃 Practice"],
                key="view_types"
            )

        with col2:
            # 날짜 범위 필터
            if not schedule_df.empty:
                min_date = schedule_df["Date"].min()
                max_date = schedule_df["Date"].max()
                date_range = st.date_input(
                    "날짜 범위",
                    value=(min_date, max_date),
                    key="view_date_range"
                )
            else:
                date_range = st.date_input("날짜 범위", key="view_date_range")

        with col3:
            # 상대팀 필터
            if not schedule_df.empty:
                opponent_options = ["전체"] + sorted(schedule_df["Opponent"].dropna().unique().tolist())
                selected_opponents = st.multiselect(
                    "상대팀",
                    options=opponent_options,
                    default=["전체"],
                    key="view_opponents"
                )
            else:
                selected_opponents = ["전체"]

        with col4:
            # 장소 필터
            if not schedule_df.empty:
                location_options = ["전체"] + sorted(schedule_df["Location"].dropna().unique().tolist())
                selected_locations = st.multiselect(
                    "장소",
                    options=location_options,
                    default=["전체"],
                    key="view_locations"
                )
            else:
                selected_locations = ["전체"]

        with col5:
            # 결과 필터
            if not schedule_df.empty:
                result_options = ["전체"] + sorted(schedule_df["Result"].dropna().unique().tolist())
                selected_results = st.multiselect(
                    "결과",
                    options=result_options,
                    default=["전체"],
                    key="view_results"
                )
            else:
                selected_results = ["전체"]

    # 상세 정보 보기 체크박스 (필터 밖)
    show_details = st.checkbox("상세 정보 보기", value=True)

    # 필터링 적용
    filtered_df = schedule_df[
        (schedule_df["Type"].isin(selected_types))
        & (schedule_df["Date"] >= date_range[0])
        & (schedule_df["Date"] <= date_range[1])
    ]

    # 상대팀 필터 적용
    if "전체" not in selected_opponents and selected_opponents:
        filtered_df = filtered_df[filtered_df["Opponent"].isin(selected_opponents)]

    # 장소 필터 적용
    if "전체" not in selected_locations and selected_locations:
        filtered_df = filtered_df[filtered_df["Location"].isin(selected_locations)]

    # 결과 필터 적용
    if "전체" not in selected_results and selected_results:
        filtered_df = filtered_df[filtered_df["Result"].isin(selected_results)]

    # 달력 표시
    if not filtered_df.empty:
        events = []
        for _, row in filtered_df.iterrows():
            title = f"{row['Type']} - {row['Location']}"
            if row['Type'] == '⚽ Match':
                title += f" vs {row['Opponent']}"
            events.append({
                "title": title,
                "start": str(row['Date']),
                "end": str(row['Date']),
                "allDay": True,
            })
        calendar(events=events, options={"initialView": "dayGridMonth"}, key="schedule_calendar")

    # 요약 정보
    st.subheader(f"📊 총 {len(filtered_df)}개 일정")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("매치 수", int((filtered_df["Type"] == "⚽ Match").sum()))
    with col2:
        st.metric("연습 수", int((filtered_df["Type"] == "🏃 Practice").sum()))
    with col3:
        total_participants = filtered_df["Participants"].sum()
        st.metric("총 참석자", int(total_participants))

    if filtered_df.empty:
        st.warning("조건에 맞는 일정이 없습니다.")
    else:
        display_df = filtered_df.copy()
        if not show_details:
            display_df = display_df[["Date", "Type", "Opponent", "Location", "Result", "Participants"]]
        else:
            # 상세 보기 시에도 ID는 제외
            display_df = display_df[["Date", "Type", "Opponent", "Location", "Result", "Participants", "Skill_Level", "Age_Group", "Manner_Score"]]
        st.dataframe(
            display_df.sort_values("Date", ascending=False).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.DateColumn("날짜"),
                "Type": st.column_config.TextColumn("종류"),
                "Opponent": st.column_config.TextColumn("상대팀"),
                "Location": st.column_config.TextColumn("장소"),
                "Result": st.column_config.TextColumn("결과"),
                "Participants": st.column_config.NumberColumn("참석자"),
                "Skill_Level": st.column_config.TextColumn("실력"),
                "Age_Group": st.column_config.TextColumn("연령대"),
                "Manner_Score": st.column_config.NumberColumn("매너점수")
            }
        )

        with st.expander("일정 상세 보기", expanded=True):
            for _, row in filtered_df.sort_values("Date", ascending=False).iterrows():
                st.markdown(
                    f"**{row['Date']}** — {row['Type']} / {row['Location']}"
                )
                if row['Type'] == '⚽ Match':
                    st.write(f"상대팀: {row['Opponent']} (실력: {row['Skill_Level']}, 연령대: {row['Age_Group']}, 매너점수: {row['Manner_Score']})")
                st.write(f"결과: {row['Result'] or '진행 예정'} | 참석자: {row['Participants']}명")

                # 참석자 상세 정보 표시
                participants = get_schedule_participants(row['ID'])
                if participants:
                    with st.expander(f"참석자 목록 ({len(participants)}명)", expanded=False):
                        for p in participants:
                            goals_info = f" (골: {p['goals']})" if p['goals'] > 0 else ""
                            st.write(f"- {p['name']} ({p['position']}){goals_info}")

                st.divider()