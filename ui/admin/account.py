import streamlit as st
import pandas as pd
from datetime import datetime

from utils.auth_guard import (
    get_role_display,
    get_role_map_data,
    require_role
)
from utils.factory import get_account_repository
from settings import USE_FIRESTORE

if USE_FIRESTORE:
    account_repo = get_account_repository()
    accounts_data = account_repo.list_accounts()
else:
    # SQLite의 경우 계정 데이터를 가져오는 로직 추가 필요
    accounts_data = []

accounts_df = pd.DataFrame(accounts_data) if accounts_data else pd.DataFrame()


def set_account_page():
    require_role("admin")

    # 성공/에러 메시지 표시
    if "account_success_message" in st.session_state:
        st.success(st.session_state.account_success_message)
        del st.session_state.account_success_message
    if "account_error_message" in st.session_state:
        st.error(st.session_state.account_error_message)
        del st.session_state.account_error_message

    st.header("🔐 계정 관리")
    st.caption("사용자 계정을 승인하거나 권한을 관리할 수 있습니다.")
    

    st.divider()

    # 계정 통계    
    col1, col2, col3, col4 = st.columns(4)

    total_accounts = len(accounts_data)
    pending_count = len([acc for acc in accounts_data if acc.get("status") == "pending"])
    approved_count = len(
        [acc for acc in accounts_data if acc.get("status") == "approved"]
    )
    other_count = total_accounts - pending_count - approved_count

    with col1:
        st.metric("전체 계정", total_accounts)
    with col2:
        st.metric("대기 중", pending_count)
    with col3:
        st.metric("승인됨", approved_count)
    with col4:
        st.metric("기타", other_count)

    st.write(" ")
    st.write(" ")
    

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["승인 대기", "승인 완료", "승인 거절"])

    # 탭1: 대기 중인 계정 (pending)
    with tab1:
        st.write(" ")
        st.subheader("승인 대기")
        st.caption("새로 가입한 계정을 승인하거나 거절할 수 있습니다.")
        st.write(" ")
        st.write(" ")

        pending_accounts = [
            acc for acc in accounts_data if acc.get("status") == "pending"
        ]

        if pending_accounts:
            pending_df = pd.DataFrame(pending_accounts)

            st.divider()
            cols = st.columns([1.5, 1, 1.5, 0.5])
            with cols[0]:
                st.write("**이메일**")
            with cols[1]:
                st.write("**이름**")
            with cols[2]:
                st.write("**가입일**")
            with cols[3]:
                sub3_col1, sub3_col2, sub_col3 = st.columns([1, 1, 1])
                with sub3_col2:
                    st.write("**작업**")

            st.divider()

            for account in pending_accounts:
                cols = st.columns([1.5, 1, 1.5, 0.5])
                with cols[0]:
                    st.write(account.get("email", "-"))
                with cols[1]:
                    st.write(account.get("displayName", "-"))
                with cols[2]:
                    created_at = account.get("createdAt")
                    if created_at:
                        if hasattr(created_at, "strftime"):
                            st.write(created_at.strftime("%Y-%m-%d %H:%M:%S"))
                        else:
                            st.write(str(created_at)[:10])
                    else:
                        st.write("-")

                with cols[3]:
                    col_approve, col_reject = st.columns(2)
                    with col_approve:
                        if st.button(
                            "승인",
                            key=f"approve_{account['id']}",
                            width="stretch",
                            type="primary",
                        ):
                            try:
                                if USE_FIRESTORE:
                                    # 현재 로그인한 사용자 ID를 approver_id로 사용
                                    approver_id = st.session_state.get(
                                        "user_id", "admin"
                                    )
                                    account_repo.approve_account(
                                        account["id"], approver_id
                                    )
                                st.session_state.account_success_message = (
                                    f"{account['email']} 계정이 승인되었습니다."
                                )
                                st.rerun()
                            except Exception as e:
                                st.session_state.account_error_message = (
                                    f"승인 실패: {e}"
                                )
                                st.rerun()
                    with col_reject:
                        if st.button(
                            "거절",
                            key=f"reject_{account['id']}",
                            width="stretch"
                        ):
                            try:
                                if USE_FIRESTORE:
                                    approver_id = st.session_state.get(
                                        "user_id", "admin"
                                    )
                                    account_repo.reject_account(
                                        account["id"], approver_id
                                    )
                                st.session_state.account_success_message = (
                                    f"{account['email']} 계정이 거절되었습니다."
                                )
                                st.rerun()
                            except Exception as e:
                                st.session_state.account_error_message = (
                                    f"거절 실패: {e}"
                                )
                                st.rerun()
        else:
            st.info("대기 중인 계정이 없습니다.")

    # 탭2: 승인된 계정 (approved)
    with tab2:
        st.write(" ")
        st.subheader("승인 완료")
        st.caption("활성화된 사용자의 권한을 관리할 수 있습니다.")
        st.write(" ")
        st.write(" ")

        st.divider()

        approved_accounts = [
            acc for acc in accounts_data if acc.get("status") == "approved"
        ]

        if approved_accounts:
            approved_df = pd.DataFrame(approved_accounts)

            cols = st.columns([3, 2, 1, 1, 0.5])
            with cols[0]:
                st.write("**이메일**")
            with cols[1]:
                st.write("**이름**")
            with cols[2]:
                st.write("**역할**")
            with cols[3]:
                st.write("**상태**")
            with cols[4]:
                st.write("**작업**")

            st.divider()

            for account in approved_accounts:
                cols = st.columns([3, 2, 1, 1, 0.5])
                with cols[0]:
                    st.write(account.get("email", "-"))
                with cols[1]:
                    st.write(account.get("displayName", "-"))
                with cols[2]:
                    st.write(get_role_display(account.get("role", "user")))
                with cols[3]:
                    st.write("활성")
                with cols[4]:
                    if st.button(
                        "EDIT",
                        key=f"manage_{account['id']}",
                        help="계정 관리",
                        width="content",
                        type="primary"
                    ):
                        st.session_state.selected_account = account["id"]

                # 계정 관리 패널
                if st.session_state.get("selected_account") == account["id"]:
                    st.write(" ")
                    with st.container(border=True, horizontal_alignment="right"):

                        if st.button(
                            "❌",
                            key=f"close_{account['id']}",
                            width="content",
                            type="tertiary"
                        ):
                            del st.session_state.selected_account
                            st.rerun()
                        
                        st.subheader(f"Edit Account: {account['email']}", divider=True)
                        st.write(" ")
                        #st.write("**계정 관리**")

                        is_unchanged = False
                        is_account_updated = False

                        sub_name_col, sub_role_col, sub_save_col = st.columns([3, 3, 0.3], vertical_alignment="bottom")
                        with sub_name_col:
                            new_name = st.text_input(
                                "이름",
                                value=account.get("displayName", ""),
                                key=f"name_{account['id']}",
                            )

                        role_options = get_role_map_data()
                        
                        role_labels = [label for label, _ in role_options]
                        role_values = [value for _, value in role_options]

                        with sub_role_col:
                            selected_role_label = st.selectbox(
                                "역할",
                                role_labels,
                                index=role_values.index(account.get("role", "user")),
                                key=f"role_{account['id']}",
                            )
                            new_role = role_values[role_labels.index(selected_role_label)]

                        with sub_save_col:
                            if st.button(
                                "수정",
                                key=f"save_account_{account['id']}",
                                type="primary",
                                use_container_width=True,
                            ):
                                updates = {}
                                if new_name != account.get("displayName", ""):
                                    updates["displayName"] = new_name
                                if new_role != account.get("role", "user"):
                                    updates["role"] = new_role

                                if updates:
                                    try:
                                        if USE_FIRESTORE:
                                            updates["updatedAt"] = (
                                                __import__("firebase_admin")
                                                .firestore.SERVER_TIMESTAMP
                                            )
                                            account_repo.db.collection(
                                                "accounts"
                                            ).document(account["id"]).update(updates)

                                        changed_fields = []
                                        if "displayName" in updates:
                                            changed_fields.append("이름")
                                        if "role" in updates:
                                            changed_fields.append("역할")

                                        #st.session_state.account_success_message = (
                                        #    f"{account['email']}의 {' 및 '.join(changed_fields)}이(가) 변경되었습니다."
                                        #)
                                        is_account_updated = True
                                        
                                    except Exception as e:
                                        st.session_state.account_error_message = (
                                            f"계정 수정 실패: {e}"
                                        )
                                        st.rerun()
                                else:
                                    is_unchanged = True
                                    #st.session_state.account_error_message = ("변경된 내용이 없습니다.")                                    

                                    #st.rerun()

                        #st.write(" ")
                        st.divider()

                        if st.button(
                            "⛔ 계정 정지",
                            key=f"suspend_{account['id']}",
                            width="stretch",
                            type="primary"
                        ):
                            try:
                                if USE_FIRESTORE:
                                    approver_id = st.session_state.get(
                                        "user_id", "admin"
                                    )
                                    account_repo.suspend_account(
                                        account["id"], approver_id
                                    )
                                st.session_state.account_success_message = (
                                    f"{account['email']} 계정이 정지되었습니다."
                                )
                                st.rerun()
                            except Exception as e:
                                st.session_state.account_error_message = (
                                    f"계정 정지 실패: {e}"
                                )
                                st.rerun()

                        st.write(" ")

                        if is_unchanged:
                            st.error("변경된 내용이 없습니다.")

                        if is_account_updated:
                            st.success("계정 정보가 업데이트되었습니다.")

                        st.write(" ")

        else:
            st.info("승인된 계정이 없습니다.")

    # 탭3: 거절/정지된 계정
    with tab3:
        st.write(" ")
        st.subheader("거절 계정")
        st.caption("승인이 거절되었거나 정지된 계정입니다.")
        st.write(" ")
        st.write(" ")

        st.divider()

        other_accounts = [
            acc
            for acc in accounts_data
            if acc.get("status") in ["rejected", "suspended"]
        ]

        if other_accounts:
            cols = st.columns([3, 2, 1.5, 0.5])
            with cols[0]:
                st.write("**이메일**")
            with cols[1]:
                st.write("**이름**")
            with cols[2]:
                st.write("**상태**")
            with cols[3]:
                st.write("**작업**")

            st.divider()

            for account in other_accounts:
                cols = st.columns([3, 2, 1.5, 0.5])
                with cols[0]:
                    st.write(account.get("email", "-"))
                with cols[1]:
                    st.write(account.get("displayName", "-"))
                with cols[2]:
                    status = account.get("status", "unknown")
                    status_display = "거절" if status == "rejected" else "정지"
                    st.write(status_display)
                with cols[3]:
                    if st.button(
                        "↩",
                        help="재심사",
                        key=f"reconsider_{account['id']}",
                        width="content",
                        type="primary"
                    ):
                        try:
                            if USE_FIRESTORE:
                                account_repo.db.collection(
                                    "accounts"
                                ).document(account["id"]).update(
                                    {
                                        "status": "pending",
                                        "updatedAt": __import__(
                                            "firebase_admin"
                                        ).firestore.SERVER_TIMESTAMP,
                                    }
                                )
                            st.session_state.account_success_message = (
                                f"{account['email']} 계정이 재심사 상태로 변경되었습니다."
                            )
                            st.rerun()
                        except Exception as e:
                            st.session_state.account_error_message = (
                                f"상태 변경 실패: {e}"
                            )
                            st.rerun()
        else:
            st.info("거절되었거나 정지된 계정이 없습니다.")


set_account_page()
