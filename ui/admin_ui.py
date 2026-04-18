# ui/admin_ui.py
import streamlit as st
from services.account_service import approve_user, reject_user
from utils.factory import get_account_repository
from utils.auth_guard import require_role

account_repo = get_account_repository()


def admin_panel():
    require_role("admin")

    st.subheader("승인 대기 계정")

    accounts = account_repo.list_accounts(status="pending")

    for acc in accounts:
        col1, col2, col3 = st.columns([4, 1, 1])

        col1.write(acc["email"])

        if col2.button("승인", key=f"approve_{acc['id']}"):
            approve_user(acc["id"], "user", "admin")
            st.rerun()

        if col3.button("거절", key=f"reject_{acc['id']}"):
            reject_user(acc["id"], "admin")
            st.rerun()
