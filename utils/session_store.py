import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager


def get_cookie_jar():
    cookies = EncryptedCookieManager(
        prefix="fcstars",
        password=st.secrets["cookie_password"],
    )
    if not cookies.ready():
        st.stop()
    return cookies


def load_refresh_token(cookies) -> str | None:
    token = cookies.get("refresh_token")
    return token or None


def save_refresh_token(cookies, refresh_token: str) -> None:
    cookies["refresh_token"] = refresh_token
    cookies.save()


def clear_refresh_token(cookies) -> None:
    cookies["refresh_token"] = ""
    cookies.save()