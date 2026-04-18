import streamlit as st
from utils.session_store import get_cookie_jar, load_refresh_token, save_refresh_token, clear_refresh_token
from services.auth_service import restore_user_from_refresh_token

from settings import USE_FIRESTORE, FAVICON_URL
from PIL import Image

from ui.auth_ui import (
    get_login_ui, 
    get_signup_ui, 
    get_logout_ui
)

from sqlite_init import initialize_dev_database
from firebase_init import init_firebase


# Get Cookie
cookies = get_cookie_jar()

favicon = Image.open(FAVICON_URL)

st.set_page_config(
    page_title="FC Stars", 
    layout="wide",
    page_icon=favicon
)

if "current_user" not in st.session_state:
    st.session_state.current_user = None

def hydrate_session_from_cookie():
    if st.session_state.get("current_user") is not None:
        return

    if st.session_state.get("logout_requested"):
        st.session_state.pop("logout_requested", None)
        return

    if not USE_FIRESTORE:
        return

    refresh_token = load_refresh_token(cookies)
    if not refresh_token:
        return

    try:
        user = restore_user_from_refresh_token(refresh_token)
        st.session_state.current_user = user

        new_refresh_token = user.get("refresh_token")
        if new_refresh_token and new_refresh_token != refresh_token:
            save_refresh_token(cookies, new_refresh_token)

    except Exception as e:
        print(f"[AUTH] auto-login restore failed: {e}")
        clear_refresh_token(cookies)


# Set Sidebar
def set_sidebar():
    user = st.session_state.get("current_user")
    
    login_page = st.Page(show_login_signup_screen, title="로그인", icon=":material/login:", visibility="hidden")    

    dashboard = st.Page(
        "ui/admin/dashboard.py", title="Dashboard", icon=":material/dashboard:"
    )
    members = st.Page("ui/admin/members.py", title="Members", icon=":material/group:")
    account = st.Page("ui/admin/account.py", title="Account", icon=":material/person_outline:")
    tools = st.Page("ui/admin/tools.py", title="Tools", icon=":material/build:")

    schedules = st.Page("ui/team/schedules.py", title="Schedules", icon=":material/calendar_today:", default=True)    
    records = st.Page("ui/team/records.py", title="Records", icon=":material/analytics:")
    board = st.Page("ui/team/board.py", title="Board", icon=":material/assignment:")

    menu_items = {}
    menu_items["Team"] = [schedules, records, board]

    if st.session_state.get("current_user"):
        if user["role"] == "admin":
            menu_items["Admin"] = [dashboard, members, account, tools]
        elif user["role"] == "operator":
            menu_items["Admin"] = [dashboard, members, account]        

        pg = st.navigation(
            menu_items
        )

        get_logout_ui(cookies)

    else:  
        pg = st.navigation([login_page])

    pg.run()
   


@st.cache_resource
def bootstrap():
    if not USE_FIRESTORE:
        initialize_dev_database(reset=False, seed=True)        
    else:
        init_firebase()


# UI Components
def show_login_signup_screen():    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Set page config title and favicon    
        st.title("FC Stars")

        tab_login, tab_signup = st.tabs(["로그인", "회원가입"])
        
        with tab_login:
            get_login_ui(cookies)

        with tab_signup:
            get_signup_ui()


# Main App
def main():
    bootstrap()

    # claims Sync
    hydrate_session_from_cookie()

    set_sidebar()


if __name__ == "__main__":
    main()