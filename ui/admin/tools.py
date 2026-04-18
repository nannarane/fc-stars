import streamlit as st

from settings import USE_FIRESTORE
from sqlite_init import initialize_dev_database
from firebase_init import init_firebase
from firestore_seed import seed_firestore_full_sample, seed_firestore_basic_sample
from utils.auth_guard import require_role


def render_admin_tools():
    require_role("admin")

    st.header("🔧 Admin Tools")
    
    st.write(" ") # 빈 줄 추가    
    st.caption("샘플 데이터 생성 및 초기화 도구를 사용할 수 있습니다.")
    st.write(" ") # 빈 줄 추가


    tab_init_data, tab_set_sample_data = st.tabs(["데이터 초기화", "샘플 데이터 생성"])

    with tab_init_data:
        init_data_tab()

    with tab_set_sample_data:
        set_sample_data_tab()


def set_sample_data_tab():

    if USE_FIRESTORE:
        st.write(" ") # 빈 줄 추가
        st.subheader("샘플 데이터 생성")
        st.write(" ") # 빈 줄 추가
        st.caption("accounts / members / schedules / participants 데이터 스키마 및 샘플 데이터를 함께 생성합니다.")
        st.write(" ") # 빈 줄 추가
        st.warning("샘플 데이터 설정은 아래 체크박스를 체크할 경우, 기존 데이터 초기화가 가능하니 주의가 필요합니다.")
        st.write(" ") # 빈 줄 추가

        reset_docs = st.checkbox(
            "기존 데이터를 삭제 후 다시 생성",
            value=True,
            help="체크하면 기존 accounts / members / schedules / participants를 삭제한 뒤 다시 설정합니다.",
        )

        st.write(" ") # 빈 줄 추가

        if st.button("샘플 데이터 설정", type="primary"):
            try:
                with st.spinner("데이터 초기화 중..."):
                    db = init_firebase()
                    email_to_uid = seed_firestore_full_sample(
                        db,
                        reset_firestore_docs=reset_docs,
                    )

                st.session_state.clear()
                st.success("샘플 데이터 설정 완료되었습니다.")
                st.json(email_to_uid)
            except Exception as e:
                st.error(f"샘플 데이터 설정 실패: {e}")

    else:
        st.write(" ") # 빈 줄 추가
        st.subheader("로컬 데이터베이스 초기화")
        st.write(" ") # 빈 줄 추가
        st.caption("dev 환경에서만 실행됩니다.")
        st.write(" ") # 빈 줄 추가

        reset_db = st.checkbox(
            "DB 파일 삭제 후 재생성",
            value=False,
            help="체크하면 로컬 데이터베이스 파일을 삭제 후 다시 생성하고 샘플 데이터를 적재합니다.",
        )

        if st.button("로컬 데이터베이스 초기화 / 시드 실행", type="primary"):
            try:
                with st.spinner("로컬 데이터베이스 초기화 중..."):
                    initialize_dev_database(reset=reset_db, seed=True, verbose=True)

                st.success("로컬 데이터베이스 초기화가 완료되었습니다.")
            except Exception as e:
                st.error(f"로컬 데이터베이스 초기화 실패: {e}")


def init_data_tab():
    st.write(" ") # 빈 줄 추가
    st.subheader("데이터 초기화")
    st.write(" ") # 빈 줄 추가
    st.caption("데이터베이스 스키마만 생성하고 샘플 데이터는 넣지 않습니다.")
    st.write(" ") # 빈 줄 추가

    if USE_FIRESTORE:
        #st.info("ℹ️ Firestore를 기본 데이터로 초기화합니다.")
        #st.write(" ") # 빈 줄 추가
        st.warning("⚠️ 기존 데이터를 모두 삭제하고 기본 데이터로 초기화하겠습니다.")
        st.write(" ") # 빈 줄 추가

        confirm_reset = st.checkbox(
            "기존 데이터를 삭제하고 기본 데이터로 초기화",
            value=False,
            help="체크하면 기존 accounts / members / schedules / participants를 삭제한 뒤 기본 데이터로 설정합니다.",
        )

        st.write(" ") # 빈 줄 추가

        if st.button("Firestore 초기화 (기본 데이터)", type="primary", disabled=not confirm_reset):
            try:
                with st.spinner("Firestore 초기화 중..."):
                    db = init_firebase()
                    email_to_uid = seed_firestore_basic_sample(
                        db,
                        reset_firestore_docs=True,
                    )

                st.session_state.clear()
                st.success("Firestore가 초기화되었습니다. (기본 데이터 설정)")
                st.info("이제 새로운 데이터를 입력할 수 있습니다.")
                st.json(email_to_uid)
            except Exception as e:
                st.error(f"Firestore 초기화 실패: {e}")
    else:
        st.info("ℹ️ 로컬 SQLite 데이터베이스를 스키마만 생성합니다.")
        st.write(" ") # 빈 줄 추가

        confirm_reset = st.checkbox(
            "⚠️ 기존 데이터를 모두 삭제하고 초기화하겠습니다",
            value=False,
            help="체크하면 로컬 데이터베이스 파일을 삭제 후 스키마만 생성합니다.",
        )

        st.write(" ") # 빈 줄 추가

        if st.button("데이터베이스 초기화 (스키마만)", type="primary", disabled=not confirm_reset):
            try:
                with st.spinner("데이터베이스 초기화 중..."):
                    initialize_dev_database(reset=True, seed=False, verbose=True)

                st.success("데이터베이스가 초기화되었습니다. (스키마만 생성)")
                st.info("이제 새로운 데이터를 입력할 수 있습니다.")
            except Exception as e:
                st.error(f"데이터베이스 초기화 실패: {e}")


render_admin_tools()
