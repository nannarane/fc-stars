from __future__ import annotations

from typing import Dict

import bcrypt
import requests
import streamlit as st
from firebase_admin import auth

from settings import USE_FIRESTORE
from utils.factory import get_account_repository


def _account_repo():
    return get_account_repository()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    if not hashed or not hashed.startswith("$2"):
        raise ValueError("저장된 비밀번호 해시 형식이 bcrypt가 아닙니다.")
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def sqlite_login(email: str, password: str) -> Dict:
    account_repo = _account_repo()
    account = account_repo.get_account_by_email(email)

    if not account:
        raise ValueError("계정을 찾을 수 없습니다.")

    if not verify_password(password, account["password_hash"]):
        raise ValueError("비밀번호가 올바르지 않습니다.")

    if account.get("status") != "approved":
        raise ValueError(f"계정 상태가 승인 상태가 아닙니다. ({account.get('status')})")

    account_repo.update_last_login(str(account["id"]))

    return {
        "uid": str(account["id"]),
        "email": account["email"],
        "role": account.get("role", "user"),
        "id_token": None,
        "refresh_token": None,
    }


def firebase_login(email: str, password: str) -> Dict:
    api_key = st.secrets.get("firebase_api_key")
    if not api_key:
        raise ValueError("firebase_api_key가 secrets.toml에 없습니다.")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    res = requests.post(
        url,
        json={
            "email": email,
            "password": password,
            "returnSecureToken": True,
        },
        timeout=20,
    )

    if res.status_code != 200:
        try:
            err = res.json().get("error", {}).get("message", "LOGIN_FAILED")
        except Exception:
            err = "LOGIN_FAILED"
        raise ValueError(f"로그인 실패: {err}")

    return res.json()


def refresh_id_token(refresh_token: str) -> Dict:
    api_key = st.secrets.get("firebase_api_key")
    if not api_key:
        raise ValueError("firebase_api_key가 secrets.toml에 없습니다.")

    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    res = requests.post(
        url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=20,
    )

    if res.status_code != 200:
        raise ValueError(f"Refresh token 갱신 실패: {res.text}")

    return res.json()


def verify_token(id_token: str, clock_skew_seconds: int = 10) -> Dict:
    return auth.verify_id_token(
        id_token,
        clock_skew_seconds=clock_skew_seconds,
    )


def restore_user_from_refresh_token(refresh_token: str) -> Dict:
    """
    쿠키에 저장된 refresh token으로 자동 로그인 복원.
    - refresh token으로 새 id token 발급
    - clock skew 10초 허용으로 verify
    - Firestore account + claims 동기화 후 세션 복원
    """
    account_repo = _account_repo()

    try:
        tokens = refresh_id_token(refresh_token)
        id_token = tokens["id_token"]

        decoded = verify_token(id_token, clock_skew_seconds=10)
        uid = decoded["uid"]

        from services.account_service import sync_claims_on_login
        account = sync_claims_on_login(uid)

        if not account:
            raise ValueError("계정 프로필을 찾을 수 없습니다.")

        if account.get("status") != "approved":
            raise ValueError(f"계정 상태가 승인 상태가 아닙니다. ({account.get('status')})")

        return {
            "uid": uid,
            "email": account["email"],
            "role": account.get("role", "user"),
            "id_token": id_token,
            "refresh_token": tokens.get("refresh_token", refresh_token),
        }

    except Exception as e:
        print(f"[AUTH] auto-login restore failed: {e}")
        raise


def login_user(email: str, password: str) -> Dict:
    if not USE_FIRESTORE:
        return sqlite_login(email, password)

    result = firebase_login(email, password)
    decoded = verify_token(result["idToken"])
    uid = decoded["uid"]

    from services.account_service import sync_claims_on_login

    account = sync_claims_on_login(uid)
    if not account:
        raise ValueError("계정 프로필을 찾을 수 없습니다.")

    if account.get("status") != "approved":
        raise ValueError(f"계정 상태가 승인 상태가 아닙니다. ({account.get('status')})")

    return {
        "uid": uid,
        "email": account["email"],
        "role": account.get("role", "user"),
        "id_token": result["idToken"],
        "refresh_token": result.get("refreshToken"),
    }