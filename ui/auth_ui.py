import time

import streamlit as st

from services.auth_service import login_user
from services.account_service import signup_user
from utils.auth_guard import check_name_validity, check_password_strength, is_valid_email
from utils.session_store import (
    save_refresh_token,
    clear_refresh_token
)



def get_login_ui(cookies=None):

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("로그인")    

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("이메일", key="login_email", help="이메일 주소를 입력해주세요.")
            password = st.text_input("비밀번호", type="password", key="login_password", help="비밀번호를 입력해주세요.")
            submitted = st.form_submit_button("로그인", type="primary", help="이메일과 비밀번호를 입력해주세요.")

            if submitted:
                try:
                    if is_valid_email(email) is False:
                        st.error("유효한 이메일 주소를 입력해주세요.")
                        #st.toast("유효한 이메일 주소를 입력해주세요.", icon=":material/calendar_today:")
                        return

                    with st.spinner("Loading... Please wait!"):
                        time.sleep(2)  # Simulate a long process
                        user = login_user(email, password)
                        st.session_state.current_user = user

                        if cookies is not None and user.get("refresh_token"):
                            save_refresh_token(cookies, user["refresh_token"])

                        st.success("Login Successful!")
                        #st.toast("Login Successful!", icon="✅")
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(str(e))


def get_signup_ui():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("회원가입")

        with st.form("signup_form", clear_on_submit=False):
            email = st.text_input("이메일", key="signup_email", help="이메일 주소를 입력해주세요.")
            name = st.text_input("이름", key="signup_name", help="이름은 2~10자 사이로 입력해주세요.")
            password = st.text_input("비밀번호", type="password", key="signup_password", help="8자 이상 14자 미만, 대소문자, 숫자, 특수문자를 포함해야 합니다.")
            submitted = st.form_submit_button("회원가입", type="primary", help="이메일과 이름, 비밀번호를 입력해주세요.")

            if submitted:                
                try:                    
                    # email 유효성 체크
                    if is_valid_email(email) is False:
                        st.error("유효한 이메일 주소를 입력해주세요.")
                        return                    
                
                    # 이름 유효성 체크
                    if check_name_validity(name) is False:
                        st.error("이름은 2~10자 사이로 입력해주세요.")
                        return
                    
                    if password:
                        password = password.strip()
                        results = check_password_strength(password)
    
                        if all(results.values()):
                            signup_user(email, password, name)
                            st.success("회원가입이 완료되었습니다.")
                            st.toast("관리자 승인 후 이용 가능합니다.")
                        else:
                            print(results)
                            for msg, checked in results.items():
                                print(msg)
                                if checked is False:
                                    st.error(f"비밀번호는 {msg} 조건을 만족해야 합니다.")
                                    return

                            st.error("비밀번호는 8자 이상 14자 미만, 대소문자, 숫자, 특수문자를 조건을 만족해야 합니다.")
                            return
                    else:
                        st.error("비밀번호는 8자 이상 14자 미만, 대소문자, 숫자, 특수문자를 조건을 만족해야 합니다.")
                    
                except Exception as e:
                    st.error(str(e))


def get_logout_ui(cookies=None):
    if st.sidebar.button("", icon=":material/logout:", help="로그아웃"):
        if cookies is not None:        
            clear_refresh_token(cookies)

        st.session_state.pop("current_user", None)
        st.session_state["logout_requested"] = True


        st.rerun()  
    