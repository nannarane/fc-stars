import streamlit as st
import pandas as pd
from datetime import datetime

from database import add_member, delete_member, get_members, update_member
from utils.auth_guard import require_role

from utils.factory import (
    get_member_repository, 
    get_schedule_repository,
    get_account_repository
)

from settings import USE_FIRESTORE

if USE_FIRESTORE:
    members_repo = get_member_repository()
    account_repo = get_account_repository()

    members_data = members_repo.list_members()
else:
    members_data = get_members()

members_df = pd.DataFrame(members_data)


def set_member_page():
    require_role("admin")

    # 성공/에러 메시지 표시
    if "success_message" in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message
    if "error_message" in st.session_state:
        st.error(st.session_state.error_message)
        del st.session_state.error_message

    st.header("👥 팀원 관리")
    st.caption("팀원를 추가하거나 정보를 수정/삭제하세요.")
    st.write(" ") # 빈 줄 추가

    # 멤버 추가 폼
    with st.expander("팀원 추가", expanded=False, icon="➕"):
        with st.form("add_member_form"):
            member_name = st.text_input("이름")
            member_birth = st.number_input("출생년도 (선택사항)", min_value=1900, max_value=datetime.now().year)
            member_position = st.selectbox("직책", ["선수", "주장", "부주장", "코치", "매니저", "게스트"])
            member_submitted = st.form_submit_button("팀원 추가", type="primary")
            if member_submitted and member_name:
                try:
                    if USE_FIRESTORE:
                        members_repo.create_member({
                            "name": member_name,
                            "birthYear": member_birth,
                            "position": member_position,
                            "attendanceDays": 0,
                            "goals" : 0,
                            "assists" : 0,
                            "isGuest": True if member_position == "게스트" else False
                        })
                        """
                        "name": data["name"],
                        "birthYear": data.get("birth_year"),
                        "position": data.get("position"),
                        "attendanceDays": data.get("attendance_days", 0),
                        "goals": data.get("goals", 0),
                        "assists": data.get("assists", 0),
                        "isGuest": data.get("is_guest", False),
                        """
                    else:
                        add_member(member_name, member_birth if member_birth else None, member_position, 0)

                    st.session_state.success_message = "팀원이 성공적으로 추가되었습니다!"
                    st.rerun()
                except Exception as e:
                    st.session_state.error_message = f"팀원 추가 실패: {e}"
                    st.rerun()

    
    st.divider()

    # 기존 팀원 관리
    st.subheader("팀원 정보 관리")
    st.caption("팀원 목록에서 멤버를 선택하여 정보를 수정하거나 삭제할 수 있습니다.")
    st.write(" ") # 빈 줄 추가

    if not members_df.empty:
        selected_member = st.selectbox(
            "팀원 선택",
            options=members_df["id"].tolist(),
            format_func=lambda x: f"{members_df[members_df['id']==x]['name'].iloc[0]} ({members_df[members_df['id']==x]['position'].iloc[0]})"
        )

        st.write(" ") # 빈 줄 추가

        if selected_member:
            member_info = members_df[members_df["id"] == selected_member].iloc[0]                      
            
            with st.expander("상세 정보", expanded=False, icon="ℹ️"):
                with st.form(f"edit_member_{selected_member}"):
                    edit_name = st.text_input("이름", member_info["name"])
                    
                    if USE_FIRESTORE:
                        birth_value = pd.to_numeric(member_info.get("birthYear"), errors="coerce")
                    else:
                        birth_value = pd.to_numeric(member_info.get("birth_year"), errors="coerce")

                    edit_birth = st.number_input(
                        "출생년도",
                        min_value=1900,
                        max_value=datetime.now().year,
                        value=int(birth_value) if not pd.isna(birth_value) else None
                    )

                    edit_position = st.selectbox(
                        "직책",
                        ["선수", "주장", "부주장", "코치", "매니저", "게스트"],
                        index=["선수", "주장", "부주장", "코치", "매니저", "게스트"].index(member_info["position"]) if member_info["position"] in ["선수", "주장", "부주장", "코치", "매니저", "게스트"] else 0
                    )

                    goals_value = pd.to_numeric(member_info.get("goals"), errors="coerce")
                    assists_value = pd.to_numeric(member_info.get("assists"), errors="coerce")

                    edit_goals = st.number_input(
                        "골 수",
                        min_value=0,
                        value=int(goals_value) if not pd.isna(goals_value) else 0,
                        disabled=True
                    )

                    edit_assists = st.number_input(
                        "어시스트 수",
                        min_value=0,
                        value=int(assists_value) if not pd.isna(assists_value) else 0,
                        disabled=True
                    )

                    edit_member_submitted = st.form_submit_button("정보 수정")

                    if edit_member_submitted and edit_name:
                        try:
                            #data = {
                            #    "name": edit_name,
                            #    "birthYear": edit_birth,
                            #    "position": edit_position,
                            #    "goals": edit_goals,
                            #    "assists": edit_assists,
                            #    "isGuest": True if edit_position == "게스트" else False
                            #}
                            data = {
                                "name": edit_name,
                                "birth_year": edit_birth,
                                "position": edit_position,
                                "goals": edit_goals,
                                "assists": edit_assists,
                                "is_guest": True if edit_position == "게스트" else False
                            }
                            if USE_FIRESTORE:
                                members_repo.update_member(selected_member, data)
                            else:
                                update_member(selected_member, edit_name, edit_birth if edit_birth else None, edit_position, edit_assists)
                            
                            st.session_state.success_message = "팀원 정보가 성공적으로 수정되었습니다!"
                            st.rerun()
                        except Exception as e:
                            st.session_state.error_message = f"팀원 수정 실패: {e}"
                            st.rerun()

            st.write(" ") # 빈 줄 추가

            if st.button("팀원 삭제", type="primary"):
                try:
                    if USE_FIRESTORE:
                        members_repo.delete_member(selected_member)
                    else:
                        delete_member(selected_member)

                    st.session_state.success_message = "팀원이 삭제되었습니다!"
                    st.rerun()
                except Exception as e:
                    st.session_state.error_message = f"팀원 삭제 실패: {e}"
                    st.rerun()
    else:
        st.info("등록된 멤버가 없습니다.")



set_member_page()