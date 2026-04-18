import streamlit as st
from streamlit_calendar import calendar
import pandas as pd 

from utils.factory import get_member_repository, get_schedule_repository

def set_schedule_page():
    
    st.header("📅 일정")
    st.caption("매치 및 연습 경기 일정을 확인하세요.")
    st.write(" ") # 빈 줄 추가

    schedule_repo = get_schedule_repository()
    members_repo = get_member_repository()


    # 데이터베이스에서 팀원 데이터 불러오기
    members_data = members_repo.list_members()
    members_dict = {m["id"]: m for m in members_data}


    # 데이터베이스에서 일정 데이터 불러오기
    schedules_data = schedule_repo.list_schedules()

    schedule_df = pd.DataFrame([
        {
            "ID": s["id"],
            "Date": s["date"],
            "Type": "⚽ Match" if s["type"] == "match" else "🏃Practice",
            "Opponent": s["matchTeam"]["name"] if s["type"] == "match" else s["opponent"] or "",
            "Location": s["location"],
            "Result": s["result"] or "",
            "Participants": s["participants"],
            "Match_Type": s["matchType"] if s["type"] == "match" else "",
            "Skill_Level": s["matchTeam"].get("skill_level") if s["type"] == "match" and isinstance(s.get("matchTeam"), dict) else s["skill_level"] or "",
            "Age_Group": s["matchTeam"].get("age_group") if s["type"] == "match" and isinstance(s.get("matchTeam"), dict) else s["age_group"] or "",
            "Manner_Score": s["matchTeam"].get("manner_score") if s["type"] == "match" and isinstance(s.get("matchTeam"), dict) else s["manner_score"] or 0,
        }
        for s in schedules_data
    ])

    
    # 필터링 옵션들
    with st.expander("🔍 검색", expanded=True):
        col1, col2 = st.columns(2)
        col3, col4, col5 = st.columns(3)

        with col1:
            selected_types = st.multiselect(
                "일정 종류",
                options=["⚽ Match", "🏃Practice"],
                default=["⚽ Match", "🏃Practice"],
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

    st.divider()

    

    if len(date_range) != 2:
        st.toast("검색 범위 종료일을 선택하세요")
        return

    #schedule_df["Date"] = pd.to_datetime(schedule_df["Date"], errors="coerce").dt.date
    schedule_df_date = pd.to_datetime(schedule_df["Date"], errors="coerce").dt.date


    # 필터링 적용
    filtered_df = schedule_df[
        (schedule_df["Type"].isin(selected_types))
        & (schedule_df_date >= date_range[0])
        & (schedule_df_date <= date_range[1])
    ]

    # 상대팀 필터 적용u8
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
            title = f"{row['Type']}"
            if row['Type'] == '⚽ Match' and row.get('Match_Type'):
                title += f" ({row['Match_Type']})"
            title += f" - {row['Location']}"
            if row['Type'] == '⚽ Match':
                title += f" vs {row['Opponent']}"
            events.append({
                "title": title,
                "start": str(row['Date']),
                "end": str(row['Date']),
                "allDay": True,
            })
        
        custom_css = """
            /* 일요일 날짜 및 헤더 빨간색 */
            .fc-day-sun .fc-col-header-cell-cushion,
            .fc-day-sun .fc-daygrid-day-number {
                color: red !important;
            }
            
            /* 토요일 날짜 및 헤더 파란색 */
            .fc-day-sat .fc-col-header-cell-cushion,
            .fc-day-sat .fc-daygrid-day-number {
                color: blue !important;
            }
        """

        # 달력 생성
        calendar(
            events=events, 
            options={
                "timeZone": "Asia/Seoul",
                "locale": "ko",                
                "initialView": "dayGridMonth"                
            },
            custom_css=custom_css,
            key="schedule_calendar"
        )


    st.divider()

    # 요약 정보
    st.subheader(f"📊 최근 {len(filtered_df)}개 일정")

    st.write(" ") # 빈 줄 추가

    # 상세 정보 보기 체크박스 (필터 밖)
    show_details = st.checkbox("상세 정보 보기", value=True)

    st.divider()

    col1, col2, col3, col4 = st.columns(4, vertical_alignment="center")    
    with col1:
        st.metric("매치 수", int((filtered_df["Type"] == "⚽ Match").sum()))
    with col2:
        st.metric("연습 수", int((filtered_df["Type"] == "🏃Practice").sum()))
    with col3:
        total_participants = filtered_df["Participants"].sum()
        st.metric("총 참석자", int(total_participants))

    st.write(" ") # 빈 줄 추가

    if filtered_df.empty:
        st.warning("조건에 맞는 일정이 없습니다.")
    else:
        display_df = filtered_df.copy()
        if not show_details:
            display_df = display_df[["Date", "Type", "Opponent", "Match_Type", "Location", "Result", "Participants"]]
        else:
            # 상세 보기 시에도 ID는 제외
            display_df = display_df[["Date", "Type", "Opponent", "Match_Type", "Location", "Result", "Participants", "Skill_Level", "Age_Group", "Manner_Score"]]
        st.dataframe(
            display_df.sort_values("Date", ascending=False).reset_index(drop=True),
            width="stretch",
            hide_index=True,
            column_config={                
                "Date": st.column_config.DatetimeColumn("날짜", format="YYYY-MM-DD (ddd) HH:mm "),
                "Type": st.column_config.TextColumn("종류"),
                "Opponent": st.column_config.TextColumn("상대팀"),
                "Match_Type": st.column_config.TextColumn("매치 유형"),
                "Location": st.column_config.TextColumn("장소"),
                "Result": st.column_config.TextColumn("결과"),
                "Participants": st.column_config.NumberColumn("참석자"),
                "Skill_Level": st.column_config.TextColumn("실력"),
                "Age_Group": st.column_config.TextColumn("연령대"),
                "Manner_Score": st.column_config.NumberColumn("매너점수")
            }
        )

        st.divider()
        st.write(" ") # 빈 줄 추가

        with st.expander("일정 상세 보기", expanded=True, icon="📅"):
            for _, row in filtered_df.sort_values("Date", ascending=False).iterrows():
                #st.markdown(f"##### {row['Type']} - {row['Location']} ( {row['Date'].strftime('%Y-%m-%d %H:%M')} )")
                st.markdown(f"##### {row['Type']} ( {row['Date'].strftime('%Y-%m-%d %H:%M')} )")

                detail_shcedules_markdown = [f"- 장소: {row['Location']}"]

                if row['Type'] == '⚽ Match':
                    match_result = "진행 예정" if row['Result'] == "" else str.capitalize(row['Result'])
                    match_type_text = f"{row['Match_Type']} " if row.get('Match_Type') else ""
                    detail_shcedules_markdown.append(f"- 매치유형: {match_type_text}")
                    detail_shcedules_markdown.append(f"- 상대: {row['Opponent']} ( {row['Age_Group']} / {row['Skill_Level']} / ⭐ {row['Manner_Score']})")
                    detail_shcedules_markdown.append(f"- 결과: **{match_result}**")
                 
                detail_shcedules_markdown.append(f"- 인원: {row['Participants']}명")
                st.markdown("\n".join(detail_shcedules_markdown))  

                # 참석자 상세 정보 표시
                participants = schedule_repo.list_participants(row['ID'])
                #print(participants)
                if participants:
                    with st.expander(f"참석자 ({len(participants)}명)", expanded=False, icon="👥"):
                        participants_list = []
                        for p in participants:
                            match_record_info = f"**( {p['goals']} Goal" if p['goals'] > 0 else ""

                            if match_record_info == "":
                                match_record_info += f"**( {p['assists']} Assist " if p['assists'] > 0 else ""
                            else:
                                match_record_info += f", {p['assists']} Assist " if p['assists'] > 0 else ""
                            
                            match_record_info += "" if match_record_info == "" else ")**"

                            is_guest = members_dict.get(p['member_id'], {}).get('isGuest', False)
                            
                            if is_guest:
                                str_guest = "(Guest) "
                            else:
                                str_guest = ""

                            participants_list.append(f"- {members_dict.get(p['member_id'], {}).get('name', 'Unknown')} {str_guest}{match_record_info}")
                            #participants_list.append(f"- {members_dict.get(p['member_id'], {}).get('name', 'Unknown')} ({members_dict.get(p['member_id'], {}).get('position', 'Unknown')}){match_record_info}")
                            #participants_list.append(f"- {members_dict.get(p['member_id'], {}).get('name', 'Unknown')} {match_record_info}")
                
                        st.markdown("\n".join(participants_list))                

                st.divider()


set_schedule_page()