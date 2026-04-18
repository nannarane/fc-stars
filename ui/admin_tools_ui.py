import streamlit as st

from settings import USE_FIRESTORE
from sqlite_init import initialize_dev_database
from firebase_init import init_firebase
from firestore_seed import seed_firestore_full_sample
from utils.auth_guard import require_role


def render_admin_tools():
    require_role("admin")

    st.header("Admin Tools")
    st.warning("이 페이지의 버튼은 데이터 초기화 또는 시드를 수행합니다.")

    if USE_FIRESTORE:
        st.subheader("Firestore 샘플 시드")
        st.caption("Firebase Auth 사용자 + accounts/members/schedules 문서를 함께 생성합니다.")

        reset_docs = st.checkbox(
            "기존 Firestore 샘플 문서를 삭제 후 다시 생성",
            value=True,
            help="체크하면 기존 accounts/members/schedules 및 participants를 삭제한 뒤 다시 시드합니다.",
        )

        if st.button("Firestore 샘플 시드 실행"):
            try:
                with st.spinner("Firestore 시드 중..."):
                    db = init_firebase()
                    email_to_uid = seed_firestore_full_sample(
                        db,
                        reset_firestore_docs=reset_docs,
                    )

                st.success("Firestore 시드가 완료되었습니다.")
                st.json(email_to_uid)
            except Exception as e:
                st.error(f"Firestore 시드 실패: {e}")

    else:
        st.subheader("SQLite 초기화")
        st.caption("dev 환경에서만 실행됩니다.")

        reset_db = st.checkbox(
            "DB 파일 삭제 후 재생성",
            value=False,
            help="체크하면 SQLite DB 파일을 삭제 후 다시 생성하고 샘플 데이터를 적재합니다.",
        )

        if st.button("SQLite 초기화 / 시드 실행"):
            try:
                with st.spinner("SQLite 초기화 중..."):
                    initialize_dev_database(reset=reset_db, seed=True, verbose=True)

                st.success("SQLite 초기화가 완료되었습니다.")
            except Exception as e:
                st.error(f"SQLite 초기화 실패: {e}")