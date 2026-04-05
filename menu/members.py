import streamlit as st
import pandas as pd
from datetime import datetime
from database import add_member, update_member, delete_member

def show_member_management(members_df):
    st.header("👥 멤버 관리")
    st.markdown("팀 멤버를 추가하거나 정보를 수정/삭제하세요.")

    # 멤버 추가 폼
    with st.expander("새 멤버 추가", expanded=False):
        with st.form("add_member_form"):
            member_name = st.text_input("이름")
            member_birth = st.number_input("출생년도 (선택사항)", min_value=1900, max_value=datetime.now().year)
            member_position = st.selectbox("직책", ["선수", "주장", "부주장", "코치", "매니저"])
            member_assists = st.number_input("어시스트 수", min_value=0, value=0)

            member_submitted = st.form_submit_button("멤버 추가")
            if member_submitted and member_name:
                try:
                    add_member(member_name, member_birth if member_birth else None, member_position, member_assists)
                    st.success("멤버가 성공적으로 추가되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"멤버 추가 실패: {e}")

    # 기존 멤버 관리
    st.subheader("기존 멤버 관리")
    if not members_df.empty:
        selected_member = st.selectbox(
            "관리할 멤버 선택",
            options=members_df["id"].tolist(),
            format_func=lambda x: f"{members_df[members_df['id']==x]['name'].iloc[0]} ({members_df[members_df['id']==x]['position'].iloc[0]})"
        )

        if selected_member:
            member_info = members_df[members_df["id"] == selected_member].iloc[0]

            col1, col2 = st.columns(2)
            with col1:
                if st.button("멤버 삭제", type="secondary"):
                    try:
                        delete_member(selected_member)
                        st.success("멤버가 삭제되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"멤버 삭제 실패: {e}")

            with col2:
                with st.expander("멤버 정보 수정", expanded=False):
                    with st.form(f"edit_member_{selected_member}"):
                        edit_name = st.text_input("이름", member_info["name"])
                        edit_birth = st.number_input("출생년도", min_value=1900, max_value=datetime.now().year, value=int(member_info["birth_year"]) if member_info["birth_year"] and not pd.isna(member_info["birth_year"]) else None)
                        edit_position = st.selectbox("직책", ["선수", "주장", "부주장", "코치", "매니저"],
                                                   index=["선수", "주장", "부주장", "코치", "매니저"].index(member_info["position"]) if member_info["position"] in ["선수", "주장", "부주장", "코치", "매니저"] else 0)
                        edit_assists = st.number_input("어시스트 수", min_value=0, value=int(member_info["assists"]) if member_info["assists"] and not pd.isna(member_info["assists"]) else 0)

                        edit_member_submitted = st.form_submit_button("수정 저장")
                        if edit_member_submitted and edit_name:
                            try:
                                update_member(selected_member, edit_name, edit_birth if edit_birth else None, edit_position, edit_assists)
                                st.success("멤버 정보가 수정되었습니다!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"멤버 수정 실패: {e}")
    else:
        st.info("등록된 멤버가 없습니다.")