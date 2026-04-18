from __future__ import annotations

from typing import List, Dict, Optional

from firebase_admin import firestore
from repositories.base.schedule_repository import ScheduleRepository


class FirestoreScheduleRepository(ScheduleRepository):
    def __init__(self, db):
        self.db = db

    def list_schedules(self) -> List[Dict]:
        docs = self.db.collection("schedules").order_by(
            "date", direction=firestore.Query.DESCENDING
        ).stream()

        result = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id

            participants = list(
                self.db.collection("schedules")
                .document(doc.id)
                .collection("participants")
                .stream()
            )
            data["participants"] = len(participants)

            team = data.get("matchTeam")
            if isinstance(team, dict):
                data["opponent"] = team.get("name")
                data["skill_level"] = team.get("skill_level") or team.get("skillLevel")
                data["age_group"] = team.get("age_group") or team.get("ageGroup")                
                data["manner_score"] = team.get("manner_score") or team.get("mannerScore")
            else:
                data["opponent"] = None
                data["skill_level"] = None
                data["age_group"] = None
                data["manner_score"] = None

            result.append(data)

        return result

    def get_schedule(self, schedule_id: str) -> Optional[Dict]:
        doc = self.db.collection("schedules").document(schedule_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    def create_schedule(self, data: Dict) -> str:
        """
        Firestore schedules/{scheduleId}
        - 첫 write 시 문서 생성
        - matchTeam은 문서 내부 중첩 객체로 저장
        """
        doc_ref = self.db.collection("schedules").document()
        doc_ref.set(
            {
                "type": data["type"],
                "date": data["date"],
                "matchType": data["match_type"] if data["type"] == "match" else None,
                "location": data["location"],
                "result": data.get("result"),
                "matchTeam": data.get("match_team"),
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )
        return doc_ref.id

    def update_schedule(self, schedule_id: str, data: Dict) -> None:
        mapping = {
            "type": "type",
            "date": "date",
            "location": "location",
            "match_type": "matchType",
            "result": "result",
            "match_team": "matchTeam",
        }

        updates = {}
        for key, value in data.items():
            if key in mapping and value is not None:
                updates[mapping[key]] = value
        
        if updates:
            updates["updatedAt"] = firestore.SERVER_TIMESTAMP
            self.db.collection("schedules").document(schedule_id).update(updates)

    def delete_schedule(self, schedule_id: str) -> None:
        schedule_ref = self.db.collection("schedules").document(schedule_id)

        participants = schedule_ref.collection("participants").stream()
        batch = self.db.batch()

        for doc in participants:
            batch.delete(doc.reference)

        batch.delete(schedule_ref)
        batch.commit()

    def get_match_team(self, schedule_id: str) -> Optional[Dict]:
        doc = self.db.collection("schedules").document(schedule_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        return data.get("matchTeam")

    def set_match_team(self, schedule_id: str, team_data: Dict) -> None:
        self.db.collection("schedules").document(schedule_id).update(
            {
                "matchTeam": {
                    "name": team_data["name"],
                    "skill_level": team_data.get("skill_level"),
                    "age_group": team_data.get("age_group"),                    
                    "manner_score": team_data.get("manner_score"),
                },
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )

    def delete_match_team(self, schedule_id: str) -> None:
        self.db.collection("schedules").document(schedule_id).update(
            {
                "matchTeam": firestore.DELETE_FIELD,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )

    def list_participants(self, schedule_id: str) -> List[Dict]:
        docs = (
            self.db.collection("schedules")
            .document(schedule_id)
            .collection("participants")
            .stream()
        )

        result = []
        for doc in docs:
            data = doc.to_dict()
            data["member_id"] = doc.id
            result.append(data)
        return result

    def set_participants(self, schedule_id: str, participants: List[Dict]) -> None:
        schedule_ref = self.db.collection("schedules").document(schedule_id)
        participants_ref = schedule_ref.collection("participants")

        batch = self.db.batch()

        existing = participants_ref.stream()
        for doc in existing:
            batch.delete(doc.reference)

        for p in participants:
            if p.get("is_participating", True):
                member_id = str(p["member_id"])
                batch.set(
                    participants_ref.document(member_id),
                    {
                        "goals": p.get("goals", 0),
                        "assists": p.get("assists", 0),
                        "isParticipating": True,
                        "updatedAt": firestore.SERVER_TIMESTAMP,
                    },
                )

        batch.commit()

    def add_participant(self, schedule_id: str, member_id: str, goals: int = 0, assists: int = 0) -> None:
        self.db.collection("schedules").document(schedule_id).collection("participants").document(str(member_id)).set(
            {
                "goals": goals,
                "assists": assists,
                "isParticipating": True,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            }
        )

    def remove_participant(self, schedule_id: str, member_id: str) -> None:
        self.db.collection("schedules").document(schedule_id).collection("participants").document(str(member_id)).delete()