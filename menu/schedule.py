import streamlit as st
import pandas as pd
from datetime import datetime
from database import (
    add_schedule, add_match_team, update_schedule, delete_schedule,
    get_match_team, update_match_team, delete_match_team,
    add_participant, remove_participant,
    get_schedule_participants_detailed, update_schedule_participants,
    add_guest_member, delete_guest_member
)

def show_schedule_management(schedule_df, members_data):
    # 성공/에러 메시지 표시
    if "success_message" in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message
    if "error_message" in st.session_state:
        st.error(st.session_state.error_message)
        del st.session_state.error_message

    st.header("⚽ 일정 관리")
    st.markdown("새 일정을 추가하거나 기존 일정을 수정/삭제하세요.")

    # 일정 추가 폼
    with st.expander("새 일정 추가", expanded=False):
        with st.form("add_schedule_form"):
            schedule_type = st.selectbox("일정 종류", ["match", "training"])
            schedule_date = st.date_input("날짜")
            schedule_location = st.text_input("장소")

            if schedule_type == "match":
                col1, col2 = st.columns(2)
                with col1:
                    opponent_name = st.text_input("상대팀 이름")
                    skill_level = st.selectbox("실력 수준", ["초보", "중급", "고급"])
                with col2:
                    age_group = st.selectbox("연령대", ["20대", "30대", "40대+"])
                    manner_score = st.slider("매너 점수", 0.0, 5.0, 3.0, 0.1)
                result = st.selectbox("결과", ["", "win", "loss", "draw"])
            else:
                opponent_name = ""
                skill_level = ""
                age_group = ""
                manner_score = 0.0
                result = ""

            submitted = st.form_submit_button("일정 추가")
            if submitted:
                try:
                    schedule_id = add_schedule(schedule_type, str(schedule_date), schedule_location, result or None)
                    if schedule_type == "match":
                        add_match_team(schedule_id, opponent_name, skill_level, age_group, manner_score)
                    st.session_state.success_message = "일정이 성공적으로 추가되었습니다!"
                    st.rerun()
                except Exception as e:
                    st.session_state.error_message = f"일정 추가 실패: {e}"
                    st.rerun()

    # 기존 일정 수정/삭제
    st.subheader("기존 일정 관리")
    if not schedule_df.empty:
        selected_schedule = st.selectbox(
            "수정할 일정 선택",
            options=schedule_df["ID"].tolist(),
            format_func=lambda x: f"{schedule_df[schedule_df['ID']==x]['Date'].iloc[0]} - {schedule_df[schedule_df['ID']==x]['Type'].iloc[0]}"
        )

        if selected_schedule:
            schedule_info = schedule_df[schedule_df["ID"] == selected_schedule].iloc[0]

            col1, col2 = st.columns(2)
            with col1:
                if st.button("일정 삭제", type="secondary"):
                    try:
                        delete_schedule(selected_schedule)
                        st.session_state.success_message = "일정이 삭제되었습니다!"
                        st.rerun()
                    except Exception as e:
                        st.session_state.error_message = f"일정 삭제 실패: {e}"
                        st.rerun()

            with col2:
                with st.expander("일정 수정", expanded=False):
                    with st.form(f"edit_schedule_{selected_schedule}"):
                        edit_type = st.selectbox("종류", ["match", "training"], index=0 if schedule_info["Type"] == "⚽ Match" else 1)
                        edit_date = st.date_input("날짜", schedule_info["Date"])
                        edit_location = st.text_input("장소", schedule_info["Location"])

                        if edit_type == "match":
                            edit_opponent = st.text_input("상대팀 이름", schedule_info["Opponent"])

                            skill_level_options = ["초보", "중급", "고급"]
                            current_skill = schedule_info.get("Skill_Level") or "중급"
                            if current_skill not in skill_level_options:
                                skill_level_options.insert(0, current_skill)
                            edit_skill_level = st.selectbox(
                                "실력 수준",
                                skill_level_options,
                                index=skill_level_options.index(current_skill)
                            )

                            age_group_options = ["20대", "30대", "40대+"]
                            current_age = schedule_info.get("Age_Group") or "30대"
                            if current_age not in age_group_options:
                                age_group_options.insert(0, current_age)
                            edit_age_group = st.selectbox(
                                "연령대",
                                age_group_options,
                                index=age_group_options.index(current_age)
                            )
                            edit_manner_score = st.slider(
                                "매너 점수",
                                0.0,
                                5.0,
                                float(schedule_info.get("Manner_Score") or 3.0),
                                0.1
                            )
                            edit_result = st.selectbox(
                                "결과", ["", "win", "loss", "draw"],
                                index=["", "win", "loss", "draw"].index(schedule_info["Result"] or "")
                            )
                        else:
                            edit_opponent = ""
                            edit_skill_level = ""
                            edit_age_group = ""
                            edit_manner_score = 0.0
                            edit_result = ""

                        edit_submitted = st.form_submit_button("수정 저장")
                        if edit_submitted:
                            try:
                                update_schedule(selected_schedule, edit_type, str(edit_date), edit_location, edit_result or None)
                                if edit_type == "match":
                                    update_match_team(selected_schedule, edit_opponent, edit_skill_level, edit_age_group, edit_manner_score)
                                else:
                                    delete_match_team(selected_schedule)
                                st.session_state.success_message = "일정이 수정되었습니다!"
                                st.rerun()
                            except Exception as e:
                                st.session_state.error_message = f"일정 수정 실패: {e}"
                                st.rerun()
    else:
        st.info("등록된 일정이 없습니다.")

    # 참석자 관리 섹션
    st.subheader("참석자 관리")
    st.markdown("일정별 멤버 참석 상태와 골 기록을 관리하세요.")

    if not schedule_df.empty:
        manage_schedule = st.selectbox(
            "참석자를 관리할 일정 선택",
            options=schedule_df["ID"].tolist(),
            format_func=lambda x: f"{schedule_df[schedule_df['ID']==x]['Date'].iloc[0]} - {schedule_df[schedule_df['ID']==x]['Type'].iloc[0]} - {schedule_df[schedule_df['ID']==x]['Location'].iloc[0]}",
            key="manage_schedule"
        )

        if manage_schedule:
            schedule_type = schedule_df[schedule_df["ID"] == manage_schedule]["Type"].iloc[0]
            is_match = schedule_type == "⚽ Match"

            st.write(f"**선택된 일정**: {schedule_df[schedule_df['ID']==manage_schedule]['Date'].iloc[0]} - {schedule_type}")

            # 참석자 데이터 가져오기
            participants_data = get_schedule_participants_detailed(manage_schedule)

            if participants_data:
                # 게스트 참석자 추가
                with st.expander("➕ 게스트 참석자 추가", expanded=False):
                    with st.form(f"add_guest_{manage_schedule}"):
                        guest_name = st.text_input("이름")
                        guest_position = st.selectbox("포지션", ["게스트", "선수", "코치", "매니저"])

                        guest_submitted = st.form_submit_button("게스트 추가")
                        if guest_submitted and guest_name:
                            try:
                                guest_id = add_guest_member(guest_name, guest_position)
                                # 새 게스트를 참석자로 추가
                                add_participant(manage_schedule, guest_id, 0)
                                st.session_state.success_message = f"게스트 '{guest_name}'이(가) 추가되었습니다!"
                                st.rerun()
                            except Exception as e:
                                st.session_state.error_message = f"게스트 추가 실패: {e}"
                                st.rerun()

                st.write("### 참석자 목록")

                # 세션 상태에 참석자 데이터 저장 (수정용)
                if f"participants_{manage_schedule}" not in st.session_state:
                    st.session_state[f"participants_{manage_schedule}"] = participants_data.copy()

                updated_participants = []

                for i, participant in enumerate(st.session_state[f"participants_{manage_schedule}"]):
                    # 게스트인지 확인 (members_data에서 찾아보기)
                    is_guest = any(m['id'] == participant['member_id'] and m.get('is_guest', False) for m in members_data)

                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

                    with col1:
                        is_participating = st.checkbox(
                            f"{participant['name']} ({participant['position']})",
                            value=bool(participant['is_participating']),
                            key=f"participate_{manage_schedule}_{participant['member_id']}"
                        )

                    with col2:
                        if is_match and is_participating:
                            goals = st.number_input(
                                "골",
                                min_value=0,
                                value=int(participant['goals'] or 0),
                                key=f"goals_{manage_schedule}_{participant['member_id']}",
                                label_visibility="collapsed"
                            )
                        else:
                            goals = 0
                            st.caption("참석 안함" if not is_participating else "연습")

                    with col3:
                        if is_match and is_participating:
                            assists = st.number_input(
                                "어시",
                                min_value=0,
                                value=int(participant.get('assists', 0) or 0),
                                key=f"assists_{manage_schedule}_{participant['member_id']}",
                                label_visibility="collapsed"
                            )
                        else:
                            assists = 0
                            st.caption("")

                    with col4:
                        status_icon = "✅" if is_participating else "❌"
                        if is_match and is_participating:
                            st.write(f"{status_icon} {goals}골 {assists}어시")
                        else:
                            st.write(status_icon)

                    with col5:
                        if is_guest and st.button("🗑️", key=f"delete_guest_{manage_schedule}_{participant['member_id']}", help="게스트 삭제"):
                            try:
                                delete_guest_member(participant['member_id'])
                                st.session_state.success_message = f"게스트 '{participant['name']}'이(가) 삭제되었습니다!"
                                st.rerun()
                            except Exception as e:
                                st.session_state.error_message = f"삭제 실패: {e}"
                                st.rerun()
                        else:
                            st.write("")  # 빈 공간

                    updated_participants.append({
                        'member_id': participant['member_id'],
                        'name': participant['name'],
                        'position': participant['position'],
                        'is_participating': is_participating,
                        'goals': goals,
                        'assists': assists
                    })

                # 저장 버튼
                if st.button("참석자 정보 저장", type="primary", key=f"save_{manage_schedule}"):
                    try:
                        # 세션 상태 업데이트
                        st.session_state[f"participants_{manage_schedule}"] = updated_participants.copy()

                        # 데이터베이스 업데이트
                        update_schedule_participants(manage_schedule, updated_participants)

                        st.session_state.success_message = "참석자 정보가 저장되었습니다!"

                        # 멤버 통계 업데이트 (출석일수, 골 수)
                        for participant in updated_participants:
                            if participant['is_participating']:
                                # 출석일수 증가 (중복 방지)
                                # 실제로는 일정 참석 시 출석일수를 증가시키는 로직이 필요하지만,
                                # 여기서는 간단히 참석자 수에 따라 업데이트
                                pass

                        st.rerun()
                    except Exception as e:
                        st.session_state.error_message = f"저장 실패: {e}"
                        st.rerun()

                # 현재 참석자 요약
                participating_count = sum(1 for p in updated_participants if p['is_participating'])
                total_goals = sum(p['goals'] for p in updated_participants if p['is_participating'] and is_match)
                total_assists = sum(p['assists'] for p in updated_participants if p['is_participating'] and is_match)

                st.write("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("참석자 수", f"{participating_count}/{len(updated_participants)}")
                with col2:
                    if is_match:
                        st.metric("총 골 수", total_goals)
                    else:
                        st.metric("연습 참석", participating_count)
                with col3:
                    if is_match:
                        st.metric("총 어시스트 수", total_assists)
            else:
                st.info("멤버 데이터가 없습니다.")
    else:
        st.info("참석자를 관리할 일정이 없습니다.")