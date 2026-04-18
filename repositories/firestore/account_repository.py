# repositories/firestore/account_repository.py
from __future__ import annotations

from typing import Optional, Dict, List

from firebase_admin import firestore
from repositories.base.account_repository import AccountRepository


class FirestoreAccountRepository(AccountRepository):
    def __init__(self, db):
        self.db = db

    def create_account(self, data: Dict) -> str:
        uid = data.get("uid")
        doc_ref = (
            self.db.collection("accounts").document(uid)
            if uid
            else self.db.collection("accounts").document()
        )

        doc_ref.set(
            {
                "email": data["email"],
                "displayName": data.get("display_name"),
                "role": data.get("role", "user"),
                "status": data.get("status", "pending"),
                "memberId": data.get("member_id"),
                "firebaseUid": data.get("firebase_uid"),
                "approvedBy": None,
                "approvedAt": None,
                "lastLoginAt": None,
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )
        return doc_ref.id

    def list_accounts(
        self,
        status: Optional[str] = None,
        role: Optional[str] = None,
    ) -> List[Dict]:
        """
        인덱스 의존성 '0' 목표:
        - Firestore에서는 collection 전체를 stream()
        - status / role 필터는 Python에서 처리
        - 정렬도 Python에서 처리
        """
        docs = self.db.collection("accounts").stream()

        result: List[Dict] = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id

            if status is not None and data.get("status") != status:
                continue

            if role is not None and data.get("role") != role:
                continue

            result.append(data)

        def sort_key(item: Dict):
            created_at = item.get("createdAt")
            updated_at = item.get("updatedAt")

            # Firestore Timestamp / datetime / None 모두 안전하게 처리
            base = created_at or updated_at
            if hasattr(base, "timestamp"):
                return (base.timestamp(), item.get("id", ""))
            return (0, item.get("id", ""))

        result.sort(key=sort_key, reverse=True)
        return result

    def get_account_by_email(self, email: str) -> Optional[Dict]:
        docs = (
            self.db.collection("accounts")
            .where("email", "==", email)
            .limit(1)
            .stream()
        )
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None

    def get_account_by_uid(self, uid: str) -> Optional[Dict]:
        doc = self.db.collection("accounts").document(uid).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    def approve_account(self, account_id: str, approver_id: str) -> None:
        self.db.collection("accounts").document(account_id).update(
            {
                "status": "approved",
                "approvedBy": approver_id,
                "approvedAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )

    def reject_account(self, account_id: str, approver_id: str) -> None:
        self.db.collection("accounts").document(account_id).update(
            {
                "status": "rejected",
                "approvedBy": approver_id,
                "approvedAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )

    def suspend_account(self, account_id: str, approver_id: str) -> None:
        self.db.collection("accounts").document(account_id).update(
            {
                "status": "suspended",
                "approvedBy": approver_id,
                "approvedAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )

    def update_last_login(self, account_id: str) -> None:
        self.db.collection("accounts").document(account_id).update(
            {
                "lastLoginAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )