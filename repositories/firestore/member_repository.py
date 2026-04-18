from __future__ import annotations

from typing import List, Dict, Optional

from firebase_admin import firestore
from repositories.base.member_repository import MemberRepository


class FirestoreMemberRepository(MemberRepository):
    def __init__(self, db):
        self.db = db

    def list_members(self) -> List[Dict]:
        docs = self.db.collection("members").order_by("name").stream()
        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            result.append(data)
        return result

    def get_member(self, member_id: str) -> Optional[Dict]:
        doc = self.db.collection("members").document(member_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    def create_member(self, data: Dict) -> str:
        """
        Firestore members/{memberId}
        - 첫 write 시 문서 생성
        - auto-id 사용
        """
        doc_ref = self.db.collection("members").document()
        doc_ref.set(
            {
                "name": data["name"],
                "birthYear": data.get("birth_year"),
                "position": data.get("position"),
                "attendanceDays": data.get("attendance_days", 0),
                "goals": data.get("goals", 0),
                "assists": data.get("assists", 0),
                "isGuest": data.get("is_guest", False),
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )
        return doc_ref.id

    def update_member(self, member_id: str, data: Dict) -> None:
        mapping = {
            "name": "name",
            "birth_year": "birthYear",
            "position": "position",
            "attendance_days": "attendanceDays",
            "goals": "goals",
            "assists": "assists",
            "is_guest": "isGuest",
        }

        updates = {}
        for key, value in data.items():
            if key in mapping and value is not None:
                updates[mapping[key]] = value

        if updates:
            updates["updatedAt"] = firestore.SERVER_TIMESTAMP
            self.db.collection("members").document(member_id).update(updates)

    def delete_member(self, member_id: str) -> None:
        self.db.collection("members").document(member_id).delete()

    def add_guest_member(self, name: str, position: str = "게스트") -> str:
        doc_ref = self.db.collection("members").document()
        doc_ref.set(
            {
                "name": name,
                "position": position,
                "isGuest": True,
                "attendanceDays": 1,
                "goals": 0,
                "assists": 0,
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )
        return doc_ref.id

    def delete_guest_member(self, member_id: str) -> None:
        doc = self.db.collection("members").document(member_id).get()
        if not doc.exists:
            raise ValueError("멤버를 찾을 수 없습니다.")
        data = doc.to_dict()
        
        if not data.get("isGuest", False):
            raise ValueError("게스트 멤버가 아닙니다.")
        self.db.collection("members").document(member_id).delete()