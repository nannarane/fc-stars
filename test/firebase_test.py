import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

if not firebase_admin._apps:
    cred_dict = st.secrets["firebase_service_account"]   # dict-like
    cred = credentials.Certificate(dict(cred_dict))      # 문자열로 바꾸지 말 것
    firebase_admin.initialize_app(cred)

db = firestore.client()