import streamlit as st
from typing import List


def check_admin_permissions() -> bool:
    """
    현재 사용자가 관리자 권한이 있는지 확인하는 함수입니다.
    실제 구현에서는 사용자 인증 시스템과 연동하여 권한을 확인해야 합니다.
    여기서는 간단히 세션 상태를 이용하여 관리자 여부를 체크합니다.
    """
    if not st.session_state.get("is_admin", False):
        st.error("⚠️ 관리자 권한이 필요합니다. 접근이 제한됩니다.")
        return False
    return True


def require_admin():
    """
    관리자 권한이 필요한 기능을 실행하기 전에 호출하는 데코레이터입니다.
    권한이 없는 경우 해당 기능의 실행을 차단합니다.
    """
    if not st.session_state.get("is_admin", False):
        st.error("⚠️ 관리자 권한이 필요합니다. 접근이 제한됩니다.")
        st.info("관리자 권한이 없는 사용자는 이 기능을 사용할 수 없습니다.")
        st.stop()  # 권한이 없으면 실행을 중단합니다.

    if not check_admin_permissions():
        st.error("⚠️ 관리자 권한이 필요합니다. 접근이 제한됩니다.")
        st.info("관리자 권한이 없는 사용자는 이 기능을 사용할 수 없습니다.")
        st.stop()  # 권한이 없으면 실행을 중단합니다.


def get_allowed_pages(role: str) -> List[str]:
    """
    사용자 역할에 따라 접근 가능한 페이지 목록을 반환하는 함수입니다.
    실제 구현에서는 역할과 페이지 매핑을 데이터베이스나 설정 파일에서 관리할 수 있습니다.
    여기서는 간단한 예시로 하드코딩된 매핑을 사용합니다.
    """
    role_page_menu = {
        'anonymous': [
            "schedule"
        ],
        "admin": [
            "schedule",
            "members",
            "stats",
            "admin"
        ],
        "editor": [
            "schedule",
            "members",
            "stats"
        ],
        "viewer": [
            "schedule",
            "stats"
        ],
    }
    return role_page_menu.get(role, [])
