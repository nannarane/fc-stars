# firebase_init.py
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

from settings import STREAMLIT_SECRETS_KEY


def init_firebase():
    """
    Streamlit secrets.toml 기반 Firebase Admin 초기화.
    prod에서만 호출하는 것을 권장합니다.
    """
    if not firebase_admin._apps:
        service_account = dict(st.secrets[STREAMLIT_SECRETS_KEY])
        cred = credentials.Certificate(service_account)
        firebase_admin.initialize_app(cred)

    return firestore.client()