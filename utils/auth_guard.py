import streamlit as st
import re


def require_auth():
    """
    로그인 여부 확인.
    """
    user = st.session_state.get("current_user")
    if not user:
        st.warning("로그인이 필요합니다.")
        st.stop()


def require_role(*roles: str):
    """
    특정 role 이상만 접근 가능하도록 제한.
    예:
      require_role("admin")
      require_role("admin", "operator")
    """
    require_auth()

    user = st.session_state.get("current_user") or {}
    user_role = user.get("role")

    if user_role not in roles:
        st.error("권한이 없습니다.")
        st.stop()


def is_authenticated() -> bool:
    """
    로그인 여부를 불리언으로 확인할 때 사용.
    """
    return bool(st.session_state.get("current_user"))


def has_role(*roles: str) -> bool:
    """
    현재 사용자의 role이 허용 목록에 포함되는지 확인할 때 사용.
    """
    user = st.session_state.get("current_user") or {}
    return user.get("role") in roles

def is_valid_email(email):
    # 간단한 이메일 정규식 패턴
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    return False

def check_password_strength(password):
    # 유효성 조건 설정
    password_len = len(password)
    length_error = password_len < 8 or password_len > 14
    digit_error = re.search(r"\d", password) is None
    uppercase_error = re.search(r"[A-Z]", password) is None
    lowercase_error = re.search(r"[a-z]", password) is None
    symbol_error = re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~]", password) is None
    
    # 에러 메시지 리스트
    errors = {
        "8자 이상 14 미만": not length_error,
        "숫자 포함": not digit_error,
        "대문자 포함": not uppercase_error,
        "소문자 포함": not lowercase_error,
        "특수문자 포함": not symbol_error,
    }
    return errors

# ID 유효성 검사
def check_id_validity(user_id):
    # 조건: 영문 소문자와 숫자만 허용, 길이는 4자 이상 12자 이하
    regex = r'^[a-z0-9]{4,12}$'
    if re.match(regex, user_id):
        return True
    return False

# 이름 유효성 검사
def check_name_validity(user_name):
    clean_name = user_name.strip()
    if not (2 <= len(clean_name) <= 10):
        return False
    else:
        return True
    
# 역할 표시 함수
def get_role_display(role):
    role_map = {
        "admin": "관리자",
        "operator": "운영자",
        "user": "일반"
    }
    return role_map.get(role, "일반")


# 역할 선택을 위한 데이터
def get_role_map_data():
    return [
        ("일반", "user"),
        ("관리자", "admin"),
        ("운영자", "operator"),
    ]