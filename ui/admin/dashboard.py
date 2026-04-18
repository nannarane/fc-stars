import time

import streamlit as st
import pandas as pd 
import streamlit as st

from database import (
    add_guest_member,
    add_match_team,
    add_participant,
    add_schedule,
    delete_guest_member,
    delete_match_team,
    delete_schedule,
    get_schedule_participants_detailed,
    update_match_team, 
    update_schedule,
    update_schedule_participants,
    get_members
)

from services.account_service import approve_user, reject_user

from utils.auth_guard import require_role

from utils.factory import (
    get_member_repository, 
    get_schedule_repository,
    get_account_repository
)

require_role("admin")

from settings import USE_FIRESTORE

schedule_repo = get_schedule_repository()
members_repo = get_member_repository()
account_repo = get_account_repository()


def admin_panel():
    # 성공/에러 메시지 표시
    if "success_message" in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message
    if "error_message" in st.session_state:
        st.error(st.session_state.error_message)
        del st.session_state.error_message

    # Set page config title and favicon    
    st.header("📝 관리자 대시보드")
    st.caption("관리자 권한이 필요한 기능들을 한 곳에서 관리할 수 있습니다.")
    st.write(" ") # 빈 줄 추가

    st.divider()
    set_schedule_management_tab()

    #tab_login, tab_signup = st.tabs(["일정 관리", "승인 요청 관리"])

    #with tab_login:
    #    set_schedule_management_tab()

    #with tab_signup:
    #    set_approval_management_tab()


def set_schedule_management_tab():

    #st.write(" ") # 빈 줄 추가
    st.subheader("일정 추가")
    st.write(" ") # 빈 줄 추가
    
    # 일정 추가 폼
    with st.expander("일정 추가", expanded=False, icon="➕"):
        schedule_type = st.selectbox("일정 종류", ["match", "training"], key="new_schedule_type")

        with st.form("add_schedule_form"):
            schedule_date = st.datetime_input("날짜", format="YYYY/MM/DD")
            schedule_location = st.text_input("장소")

            opponent_name = ""
            skill_level = ""
            age_group = ""
            match_type = ""
            manner_score = 0.0
            result = ""

            if schedule_type == "match":
                col1, col2 = st.columns(2)
                with col1:
                    opponent_name = st.text_input("상대팀 이름")
                    skill_level = st.selectbox("실력 수준", ["초보", "중급", "고급"], key="new_schedule_skill_level")
                    match_type = st.selectbox("매치 타입", ["5:5", "6:6", "7:7"], index=1, key="new_schedule_match_type")
                with col2:
                    age_group = st.selectbox("연령대", ["20대", "30대", "40대+"], index=1, key="new_schedule_age_group")
                    manner_score = st.slider("매너 점수", 0.0, 5.0, 3.0, 0.1, key="new_schedule_manner_score")
                result = st.selectbox("결과", ["", "win", "loss", "draw"], key="new_schedule_result")

            submitted = st.form_submit_button("일정 추가", type="primary")
            if submitted:
                try:
                    if USE_FIRESTORE:
                        schedule_data = {
                            "type": schedule_type,
                            "date": schedule_date,
                            "location": schedule_location,
                            "result": result or None
                        }
                        if schedule_type == "match":
                            schedule_data["match_type"] = match_type
                        
                        schedule_id = schedule_repo.create_schedule(schedule_data)

                        if schedule_type == "match":
                            schedule_repo.set_match_team(
                                schedule_id=schedule_id,
                                team_data = {
                                    "name": opponent_name,
                                    "skill_level": skill_level,
                                    "age_group": age_group,
                                    "manner_score": manner_score
                                }
                            )
                            
                    else:
                        schedule_id = add_schedule(schedule_type, str(schedule_date), schedule_location, result or None)                      

                        if schedule_type == "match":
                            add_match_team(schedule_id, opponent_name, skill_level, age_group, manner_score)

                    st.session_state.success_message = "일정이 성공적으로 추가되었습니다!"
                    st.rerun()

                except Exception as e:
                    st.session_state.error_message = f"일정 추가 실패: {e}"
                    st.rerun()

    st.divider()

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


    # 일정 수정/삭제
    st.subheader("일정 수정 / 삭제")
    st.caption("등록된 일정을 수정하거나 삭제할 수 있습니다.")
    st.write(" ") # 빈 줄 추가

    #row['Date'].strftime('%Y-%m-%d %H:%M')

    if not schedule_df.empty:        
        selected_schedule = st.selectbox(
            "일정 선택",
            options=schedule_df["ID"].tolist(),
            format_func=lambda x: f"{schedule_df[schedule_df['ID']==x]['Type'].iloc[0]} - {schedule_df[schedule_df['ID']==x]['Location'].iloc[0]} ( {schedule_df[schedule_df['ID']==x]['Date'].iloc[0].strftime('%Y-%m-%d (%a) %H:%M')} )",
            #label_visibility="hidden"
        )

        if selected_schedule:
            schedule_info = schedule_df[schedule_df["ID"] == selected_schedule].iloc[0]

            st.write(" ") # 빈 줄 추가
            with st.expander("상세 일정", expanded=False, icon="ℹ️"):
                with st.form(f"edit_schedule_{selected_schedule}"):
                    edit_type = st.selectbox(
                        "종류",
                        ["match", "training"],
                        index=0 if schedule_info["Type"] == "⚽ Match" else 1,
                        key=f"edit_schedule_type_{selected_schedule}",
                        disabled=True
                    )                    
                    edit_date = st.datetime_input("날짜", schedule_info["Date"], format="YYYY/MM/DD")
                    edit_location = st.text_input("장소", schedule_info["Location"])

                    if edit_type == "match":
                        edit_opponent = st.text_input("상대팀 이름", schedule_info["Opponent"])
                        match_type_options = ["5:5", "6:6", "7:7"]
                        current_match_type = schedule_info.get("Match_Type") or "6:6"
                        if current_match_type not in match_type_options:
                            match_type_options.insert(0, current_match_type)
                        edit_match_type = st.selectbox(
                            "매치 타입",
                            match_type_options,
                            index=match_type_options.index(current_match_type)
                        )

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

                    edit_submitted = st.form_submit_button("일정 수정")
                    if edit_submitted:
                        try:
                            if USE_FIRESTORE:
                                if edit_type == "match":
                                    match_type = edit_match_type
                                    match_team = {
                                        "name": edit_opponent,
                                        "skill_level": edit_skill_level,
                                        "age_group" : edit_age_group,
                                        "manner_score": edit_manner_score
                                    }
                                else:
                                    match_type = None
                                    match_team = {}

                                # 업데이트할 필드만 포함하는 딕셔너리 생성
                                update_data = {
                                    "type": edit_type,
                                    "date": edit_date,
                                    "location": edit_location,
                                    "match_type": match_type,
                                    "result": edit_result or None,
                                    "matchTeam": match_team
                                }
                                
                                # 일정 업데이트
                                schedule_repo.update_schedule(selected_schedule, update_data)

                                if edit_type == "match":
                                    schedule_repo.set_match_team(selected_schedule, match_team)
                                else:
                                    schedule_repo.delete_match_team(selected_schedule)
                            else:
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
    
        st.write(" ") # 빈 줄 추가

        if st.button("일정 삭제", type="primary"):
            try:                
                if USE_FIRESTORE:
                    schedule_repo.delete_schedule(selected_schedule)
                else:
                    delete_schedule(selected_schedule)
                    
                st.session_state.success_message = "일정이 삭제되었습니다!"
                st.rerun()
            except Exception as e:
                st.session_state.error_message = f"일정 삭제 실패: {e}"
                st.rerun()

    else:
        st.info("등록된 일정이 없습니다.")

    st.divider()

    # 참석자 관리
    st.write(" ") # 빈 줄 추가
    st.subheader("참석자 관리")
    st.caption("일정별 멤버 참석 상태와 골 관리를 할 수 있습니다.")
    st.write(" ") # 빈 줄 추가

    if not schedule_df.empty:
        manage_schedule = st.selectbox(
            "일정 선택",
            options=schedule_df["ID"].tolist(),
            format_func=lambda x: f"{schedule_df[schedule_df['ID']==x]['Type'].iloc[0]} - {schedule_df[schedule_df['ID']==x]['Location'].iloc[0]} ( {schedule_df[schedule_df['ID']==x]['Date'].iloc[0].strftime('%Y-%m-%d (%a) %H:%M')} )",
            key="manage_schedule"
        )        

        st.write(" ") # 빈 줄 추가

        if manage_schedule:
            schedule_type = schedule_df[schedule_df["ID"] == manage_schedule]["Type"].iloc[0]
            is_match = schedule_type == "⚽ Match"

            # 참석자 데이터 가져오기
            if USE_FIRESTORE:
                participants_data = schedule_repo.list_participants(manage_schedule)
            else:
                participants_data = get_schedule_participants_detailed(manage_schedule)


            # 전체 멤버 목록 가져오기
            if USE_FIRESTORE:
                members_data = members_repo.list_members()
            else:
                members_data = get_members()
            
            # 현재 참석자의 member_id들 추출
            current_participant_ids = {p['member_id'] for p in participants_data}
            
            # 아직 참석하지 않은 멤버들 찾기
            non_participants = [m for m in members_data if m['id'] not in current_participant_ids]
            
            # 참석자 목록에 미참석 멤버 추가
            if non_participants:
                for non_participant in non_participants:
                    participants_data.append({
                        'member_id': non_participant['id'],
                        'goals': 0,
                        'assists': 0,
                        'isParticipating': False,
                        'is_participating': False,
                        'name': non_participant['name'],
                        'position': non_participant['position']
                    })
            
            if participants_data:
                # 게스트 참석자 추가
                with st.expander("게스트 참석자 추가", expanded=False, icon="➕"):
                    with st.form(f"add_guest_{manage_schedule}"):
                        guest_name = st.text_input("이름")
                        guest_position = st.selectbox("포지션", ["게스트", "선수", "코치", "매니저"])

                        guest_submitted = st.form_submit_button("게스트 추가", type="primary")
                        if guest_submitted and guest_name:
                            try:
                                if USE_FIRESTORE:                                    
                                    guest_id = members_repo.add_guest_member(guest_name, guest_position)
                                                                      
                                    schedule_repo.add_participant(manage_schedule, guest_id, 0, 0)

                                else:
                                    guest_id = add_guest_member(guest_name, guest_position)
                                    # 새 게스트를 참석자로 추가
                                    add_participant(manage_schedule, guest_id, 0)

                                st.session_state.success_message = f"게스트 '{guest_name}'이(가) 추가되었습니다."

                                participants_data = schedule_repo.list_participants(manage_schedule)
                                members_data = members_repo.list_members()
                                
                                joined_add_guest_participants = _get_updated_participants_after_update(participants_data, members_data)

                                st.session_state[f"participants_{manage_schedule}"] = joined_add_guest_participants.copy()
                                st.rerun()

                            except Exception as e:
                                st.session_state.error_message = f"게스트 추가 실패: {e}"
                                st.rerun()

                st.write(" ") # 빈 줄 추가
                st.write(" ") # 빈 줄 추가
                st.write("##### 참석 여부 및 기록 관리")
                st.caption("참석 여부 및 매치 / 연습 경기 기록을 관리할 수 있습니다.")
   
                st.divider()
                
                h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([1, 1, 1, 1, 0.5, 0.5], vertical_alignment="bottom")
                with h_col1:
                    st.markdown("**이름**")
                with h_col2:
                    h_sub_col2_1, h_sub_col2_2, h_sub_col2_3 = st.columns([1.5, 1, 1.5], vertical_alignment="center")
                    with h_sub_col2_2:
                        if is_match:
                            st.markdown("**Goal**")
                        else:
                            st.markdown("**DESC**")
                with h_col3:
                    h_sub_col3_1, h_sub_col3_2, h_sub_col3_3 = st.columns([1.5, 1, 1.5], vertical_alignment="center")
                    with h_sub_col3_2:
                        if is_match:
                            st.markdown("**Assist**")
                with h_col4:
                    h_sub_col4_1, h_sub_col4_2, h_sub_col4_3 = st.columns([0.4, 1, 0.4], vertical_alignment="center")
                    with h_sub_col4_2:
                        if is_match:
                            st.markdown("**Record**")
                with h_col5:
                    st.markdown("**참석**")
                with h_col6:
                    if is_match:
                        st.markdown("**비고**")

                  
                st.divider()

                # 세션 상태에 참석자 데이터 저장 (수정용)
                if f"participants_{manage_schedule}" not in st.session_state:
                    st.session_state[f"participants_{manage_schedule}"] = participants_data.copy()

                updated_participants = []
                
                # members_dict 생성 (한 번만 생성)
                members_dict = {m["id"]: m for m in members_data}              
                
                # 참석자 목록 시나리오
                # 기본적으로 맴버 목록을 가져온다. 그리고 현재 일정의 참석자 데이터와 매칭하여 참석 여부와 기록을 보여준다.
                # 참석자 데이터에 없는 맴버는 참석하지 않은 것으로 간주하여 목록에 추가한다.
                # 관리자는 체크박스를 통해 참석 여부를 수정하고, 골과 어시스트 수를 입력할 수 있다. 
                # 저장 버튼을 누르면 변경된 세션 상태에 대한 참가자 목록을 업데이트한다.
                # st.session_state[f"participants_{manage_schedule}"] = updated_participants.copy()
                # 세션데이터를 업데이트 후, 데이터베이스에 업데이트한다.
                # 참석자 목록에는 게스트도 포함되며, 게스트는 삭제할 수 있는 버튼이 추가로 표시된다. 게스트를 삭제하면 해당 게스트 멤버도 삭제된다.
                # 참석자 목록 상단에는 현재 참석 인원 수와 총 골 수, 총 어시스트 수 등의 요약 정보가 표시된다. (매치인 경우)
                # 참석자 목록은 일정 유형에 따라 골과 어시스트 입력란이 다르게 표시된다. 
                # 매치인 경우 골과 어시스트 입력란이 나타나고, 연습인 경우에는 참석 여부만 관리할 수 있다. (참석한 인원 수로 연습 참석 정도를 간단히 표현)
                
                  

                for participant in st.session_state[f"participants_{manage_schedule}"]:
                #for i, participant in enumerate(st.session_state[f"participants_{manage_schedule}"]):
                    # 게스트인지 확인 (members_dict에서 찾아보기)
                    #print("참석자 정보 >>>>>>")
                    #print(participant)
                    
                    if USE_FIRESTORE:
                        participant_member_info = members_dict.get(participant['member_id'])
                        
                        if participant_member_info is not None:
                            participant["name"] = participant_member_info["name"]
                            participant["position"] = participant_member_info["position"]
                            participant["is_participating"] = participant.get("isParticipating", False)
                        
                    else:
                        participant_member_info = members_dict.get(participant['member_id'])
                    
                    if USE_FIRESTORE:
                        is_guest = any(m['id'] == participant['member_id'] and m.get('isGuest', False) for m in members_data)
                    else:
                        is_guest = any(m['id'] == participant['member_id'] and m.get('is_guest', False) for m in members_data)


                    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 0.5, 0.5], vertical_alignment="center")
                    with col1:
                        is_participating = st.checkbox(
                            f"{participant['name']} ({participant['position']})",
                            value=bool(participant['is_participating']),
                            key=f"participate_{manage_schedule}_{participant['member_id']}"
                        )

                    with col2:
                        sub_col2_1, sub_col2_2, sub_col2_3 = st.columns([0.5, 3, 0.5], vertical_alignment="center")
                        with sub_col2_2:
                            if is_match and is_participating:
                                goals = st.number_input(
                                    "Goal",
                                    min_value=0,
                                    max_value=99,
                                    value=int(participant['goals'] or 0),
                                    key=f"goals_{manage_schedule}_{participant['member_id']}",
                                    label_visibility="collapsed"
                                )
                            else:
                                goals = 0
                                sub_col2_2_1, sub_col2_2_2, sub_col2_3_3 = st.columns([1, 1, 1], vertical_alignment="center")
                                with sub_col2_2_2:
                                    st.caption("참석 안함" if not is_participating else "연습")

                    with col3:
                        sub_col3_1, sub_col3_2, sub_col3_3 = st.columns([0.5, 3, 0.5], vertical_alignment="center")
                        with sub_col3_2:
                            if is_match and is_participating:
                                assists = st.number_input(
                                    "Assist",
                                    min_value=0,
                                    max_value=99,
                                    value=int(participant.get('assists', 0) or 0),
                                    key=f"assists_{manage_schedule}_{participant['member_id']}",
                                    label_visibility="collapsed"
                                )
                            else:
                                assists = 0
                                st.caption("")

                    with col4:
                        sub_col4_1, sub_col4_2, sub_col4_3 = st.columns([0.5, 3, 0.5], vertical_alignment="center")
                        with sub_col4_2:
                            if is_match and is_participating:
                                member_record = ''
                                if goals > 0:
                                    member_record += f"{goals} Goal"
                                
                                if assists > 0:
                                    if goals > 0:
                                        member_record += ' / '
                                    member_record += f"{assists} Assist"
                                if member_record != '':
                                    st.markdown(f"**{member_record}**")
                            else:
                                st.write("")  # 빈 공간

                    with col5:
                        status_icon = "✅" if is_participating else "❌"
                        st.markdown(status_icon)

                    with col6:
                        if is_guest and st.button("❌", key=f"delete_guest_{manage_schedule}_{participant['member_id']}", help="게스트 삭제", type="tertiary"):
                            try:
                                if USE_FIRESTORE:                                    
                                    schedule_repo.remove_participant(manage_schedule, participant['member_id'])
                                    members_repo.delete_guest_member(participant['member_id'])
                                else:
                                    delete_guest_member(participant['member_id'])

                                with st.spinner("Loading... Please wait!"):
                                    time.sleep(2)  # Simulate a long process

                                st.session_state.success_message = f"게스트 '{participant['name']}'이(가) 삭제되었습니다!"

                                participants_data = schedule_repo.list_participants(manage_schedule)
                                members_data = members_repo.list_members()

                                delete_guest_participants = _get_updated_participants_after_update(participants_data, members_data)

                                st.session_state[f"participants_{manage_schedule}"] = delete_guest_participants.copy()

                                st.rerun()
                            except Exception as e:
                                st.session_state.error_message = f"삭제 실패: {e}"
                                st.rerun()

                    updated_participants.append({
                        'member_id': participant['member_id'],
                        'name': participant['name'],
                        'position': participant['position'],
                        'is_participating': is_participating,
                        'isParticipating': is_participating,
                        'goals': goals,
                        'assists': assists
                    })

                st.write(" ") # 빈 줄 추가

                # 저장 버튼
                if st.button("참석자 저장", type="primary", key=f"save_{manage_schedule}"):
                    try:

                        #print("참석자 저장")
                        #print(updated_participants)

                        #print("세션")
                        #print(st.session_state[f"participants_{manage_schedule}"])                        

                        joined_updated_participants = _get_updated_participants_after_update(updated_participants, members_data)
                        #print("업데이트 후 참석자 목록")
                        #print(joined_updated_participants)
                        #return

                        # 원래 참가자 상태 복사 (통계 비교용)
                        original_participants = [p.copy() for p in st.session_state.get(f"participants_{manage_schedule}", [])]
                        original_participants_dict = {p['member_id']: p for p in original_participants}

                        # 세션 상태 업데이트
                        st.session_state[f"participants_{manage_schedule}"] = joined_updated_participants.copy()

                        # 데이터베이스 업데이트
                        if USE_FIRESTORE:
                            schedule_repo.set_participants(manage_schedule, updated_participants)
                        else:
                            update_schedule_participants(manage_schedule, updated_participants)

                        st.session_state.success_message = "참석자 정보가 저장되었습니다!"

                        if is_match:
                            # 멤버 통계 업데이트 (출석일수, 골 수, 어시스트 수)
                            for participant in updated_participants:
                                if participant['is_participating']:
                                    member_id = participant['member_id']
                                    previous_participant = original_participants_dict.get(member_id)

                                    # 게스트는 통계 업데이트 제외
                                    member_info = members_dict.get(member_id)
                                    is_guest = member_info.get('is_guest', False) if not USE_FIRESTORE else member_info.get('isGuest', False)
                                    if member_info and is_guest:
                                        continue

                                    # 출석일수 증가 (이전에 참석하지 않았던 경우)
                                    attendance_increment = 0
                                    if not previous_participant or not previous_participant.get('is_participating', False):
                                        attendance_increment = 1

                                    # 골 수 증가
                                    goals_increment = participant['goals'] - (previous_participant.get('goals', 0) if previous_participant else 0)

                                    # 어시스트 수 증가
                                    assists_increment = participant.get('assists', 0) - (previous_participant.get('assists', 0) if previous_participant else 0)

                                    # 멤버 통계 업데이트
                                    if attendance_increment > 0 or goals_increment != 0 or assists_increment != 0:
                                        current_member = members_repo.get_member(member_id)
                                        if current_member:
                                            update_data = {}
                                            if attendance_increment > 0:
                                                update_data['attendance_days'] = current_member.get('attendance_days', 0) + attendance_increment
                                            if goals_increment != 0:
                                                update_data['goals'] = current_member.get('goals', 0) + goals_increment
                                            if assists_increment != 0:
                                                update_data['assists'] = current_member.get('assists', 0) + assists_increment

                                            if update_data:
                                                members_repo.update_member(member_id, update_data)

                        st.rerun()
                    except Exception as e:
                        st.session_state.error_message = f"저장 실패: {e}"
                        st.rerun()


                # 현재 참석자 요약
                participating_count = sum(1 for p in updated_participants if p['is_participating'])
                total_goals = sum(p['goals'] for p in updated_participants if p['is_participating'] and is_match)
                total_assists = sum(p['assists'] for p in updated_participants if p['is_participating'] and is_match)

                st.write("---")
                st.write(" ") # 빈 줄 추가
                st.write("##### 참석 인원 합계")
                st.caption("총 참석 인원 및 팀원 참석 인원 합계")
                st.write(" ") # 빈 줄 추가

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
                st.write("---")       
            
    else:
        st.info("참석자를 관리할 일정이 없습니다.")


# 일정의 참석자 목록을 업데이트 후, 참가자 목록을 재설정하는 함수
def _get_updated_participants_after_update(updated_participants, members_data):
    
    # 업데이트된 참가자 목록에서 member_id들 추출
    updated_participant_ids = {p['member_id'] for p in updated_participants}
    
    # 아직 참석하지 않은 멤버들 찾기
    non_participants = [m for m in members_data if m['id'] not in updated_participant_ids]
    
    # 참석자 목록에 미참석 멤버 추가
    if non_participants:
        for non_participant in non_participants:
            updated_participants.append({
                'member_id': non_participant['id'],
                'goals': 0,
                'assists': 0,
                'isParticipating': False,
                'is_participating': False,
                'name': non_participant['name'],
                'position': non_participant['position']
            })
    
    return updated_participants

# 가입 승인 처리 탭
def set_approval_management_tab():
    st.write(" ") # 빈 줄 추가
    st.write(" ") # 빈 줄 추가
    st.caption("가입 신청한 계정들을 승인하거나 거절할 수 있습니다.")
          

    pending_accounts = account_repo.list_accounts(status="pending")

    if not pending_accounts:
        st.write(" ") # 빈 줄 추가
        st.info("현재 승인 대기 중인 계정이 없습니다.")
        return
    else:
        st.divider()

        cols = st.columns([2, 2, 3, 0.5, 0.5]) # 각 열의 너비 비율 조절
        fields = ["이메일", "이름", "신청일", "승인", "거절"]

        for col, field in zip(cols, fields):
            col.markdown(f"**{field}**")
        
        st.divider()
        

        for acc in pending_accounts:
            col1, col2, col3, col_btn1, col_btn2 = st.columns([2, 2, 3, 0.5, 0.5])

            col1.write(acc["email"])
            col2.write(acc["displayName"])
            col3.write(acc["createdAt"].strftime("%Y-%m-%d %H:%M:%S"))
            
               
            if col_btn1.button("승인", key=f"approve_{acc['id']}", type="primary"):
                approve_user(acc["id"], "user", "admin")
                st.rerun()

            if col_btn2.button("거절", key=f"reject_{acc['id']}"):
                reject_user(acc["id"], "admin")
                st.rerun()


admin_panel()