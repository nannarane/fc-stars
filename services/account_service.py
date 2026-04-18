# services/account_service.py
from __future__ import annotations

from typing import Optional, Dict, Any

from firebase_admin import auth

from settings import USE_FIRESTORE
from utils.factory import get_account_repository


def _account_repo():
    return get_account_repository()


def signup_user(email: str, password: str, name: str) -> str:
    """
    dev(SQLite):
      - bcrypt hash로 accounts 생성
      - 승인 완료 상태로 바로 생성

    prod(Firebase Auth + Firestore):
      - Firebase Auth 사용자 생성
      - Firestore accounts/{uid} 생성
      - pending 상태로 생성
    """
    account_repo = _account_repo()

    if not USE_FIRESTORE:
        from services.auth_service import hash_password

        account_id = account_repo.create_account({
            "email": email,
            "password_hash": hash_password(password),
            "role": "user",
            "status": "approved",
        })
        return account_id

    user = auth.create_user(email=email, password=password)

    account_repo.create_account({
        "uid": user.uid,
        "email": email,
        "display_name": name,
        "role": "user",
        "status": "pending",
        "firebase_uid": user.uid,
    })

    return user.uid


def approve_user(uid: str, role: str, approver_id: str) -> None:
    """
    사용자 승인.
    1) account status 승인
    2) Firebase custom claims 반영(prod만)
    """
    account_repo = _account_repo()
    account_repo.approve_account(uid, approver_id)

    if USE_FIRESTORE:
        try:
            auth.set_custom_user_claims(uid, {
                "role": role
            })
        except Exception as e:
            print(f"[WARN] set_custom_user_claims failed uid={uid}: {e}")


def reject_user(uid: str, approver_id: str) -> None:
    """
    사용자 거절.
    """
    account_repo = _account_repo()
    account_repo.reject_account(uid, approver_id)

    if USE_FIRESTORE:
        try:
            auth.set_custom_user_claims(uid, {})
        except Exception as e:
            print(f"[WARN] clear custom claims failed uid={uid}: {e}")


def suspend_user(uid: str, approver_id: str) -> None:
    """
    사용자 정지.
    """
    account_repo = _account_repo()
    account_repo.suspend_account(uid, approver_id)

    if USE_FIRESTORE:
        try:
            auth.set_custom_user_claims(uid, {})
        except Exception as e:
            print(f"[WARN] clear custom claims failed uid={uid}: {e}")


def sync_claims_on_login(uid: str) -> Optional[Dict[str, Any]]:
    """
    로그인 시 claims 자동 복구.
    Firestore를 source of truth로 사용합니다.
    """
    account_repo = _account_repo()
    account = account_repo.get_account_by_uid(uid)

    if not account:
        print(f"[AUTH] account not found uid={uid}")
        return None

    if account.get("status") != "approved":
        print(f"[AUTH] skip sync (status={account.get('status')}) uid={uid}")
        return account

    if not USE_FIRESTORE:
        return account

    try:
        user = auth.get_user(uid)
    except Exception as e:
        print(f"[WARN] firebase user not found uid={uid}: {e}")
        return account

    current_claims = user.custom_claims or {}
    current_role = current_claims.get("role")
    firestore_role = account.get("role", "user")

    if current_role != firestore_role:
        print(f"[SYNC] fixing claims uid={uid} {current_role} -> {firestore_role}")
        try:
            auth.set_custom_user_claims(uid, {"role": firestore_role})
        except Exception as e:
            print(f"[ERROR] claims sync failed uid={uid}: {e}")
    else:
        print(f"[SYNC] claims ok uid={uid} role={current_role}")

    return account