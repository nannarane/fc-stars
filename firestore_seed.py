from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from firebase_admin import auth, firestore


# --------------------------------------------------
# Seed data
# --------------------------------------------------
MEMBERS_SEED: List[Dict[str, Any]] = [
    {"id": 1, "name": "박준환", "birth_year": 1983, "position": "주장",   "attendance_days": 2, "goals": 5, "assists": 3, "is_guest": False},
    {"id": 2, "name": "윤여준", "birth_year": 1986, "position": "부주장", "attendance_days": 2,  "goals": 3, "assists": 4, "is_guest": False},
    {"id": 3, "name": "한은주", "birth_year": 1986, "position": "매니저", "attendance_days": 2, "goals": 3, "assists": 3, "is_guest": False},
    {"id": 4, "name": "박정환", "birth_year": 1986, "position": "선수",   "attendance_days": 2,  "goals": 6, "assists": 2, "is_guest": False},
    {"id": 5, "name": "조한도", "birth_year": 1986, "position": "코치",   "attendance_days": 2,  "goals": 3, "assists": 5, "is_guest": False},
    {"id": 6, "name": "구자인", "birth_year": 1986, "position": "선수",   "attendance_days": 1,  "goals": 2, "assists": 2, "is_guest": False},
    {"id": 7, "name": "유상빈", "birth_year": 1982, "position": "게스트", "attendance_days": 1,  "goals": 0, "assists": 0, "is_guest": True},
]

SCHEDULES_SEED: List[Dict[str, Any]] = [
    {
        "id": 1,
        "type": "match",
        "match_type": "6:6",
        "date": datetime(2026, 3, 6, 22, 0, 0),
        "location": "언더플레이 풋살파크",
        "result": "win",
        "match_team": {
            "name": "행축즐축",
            "skill_level": "초급",
            "age_group": "30대",
            "manner_score": 4.5,
        },
        "participants": [
            {"member_id": 1, "goals": 3, "assists": 2},
            {"member_id": 2, "goals": 2, "assists": 2},
            {"member_id": 3, "goals": 2, "assists": 2},
            {"member_id": 4, "goals": 3, "assists": 2},
            {"member_id": 5, "goals": 1, "assists": 3},
            {"member_id": 6, "goals": 2, "assists": 2}
        ],
    },
    {
        "id": 2,
        "type": "training",
        "match_type": None,
        "date": datetime(2026, 3, 20, 22, 0, 0),
        "location": "구리 대복풋살장",
        "result": None,
        "match_team": None,
        "participants": [
            {"member_id": 1, "goals": 0, "assists": 0},
            {"member_id": 2, "goals": 0, "assists": 0},
            {"member_id": 3, "goals": 0, "assists": 0},
            {"member_id": 5, "goals": 0, "assists": 0},
            {"member_id": 7, "goals": 0, "assists": 0},
        ],
    },
    {
        "id": 3,
        "type": "match",
        "match_type": "6:6",
        "date": datetime(2026, 4, 3, 20, 0, 0),
        "location": "백봉풋살장",
        "result": "loss",
        "match_team": {
            "name": "레알브로스",
            "skill_level": "초급",
            "age_group": "30대",
            "manner_score": 4.0,
        },
        "participants": [
            {"member_id": 1, "goals": 2, "assists": 1},
            {"member_id": 2, "goals": 1, "assists": 2},
            {"member_id": 3, "goals": 1, "assists": 1},
            {"member_id": 4, "goals": 3, "assists": 0},
            {"member_id": 5, "goals": 2, "assists": 2},
        ],
    },
    {
        "id": 4,
        "type": "training",
        "match_type": None,
        "date": datetime(2026, 4, 17, 21, 0, 0),
        "location": "힐링FC풋살장",
        "result": None,
        "match_team": None,
        "participants": [
            {"member_id": 1, "goals": 0, "assists": 0},
            {"member_id": 2, "goals": 0, "assists": 0},
            {"member_id": 3, "goals": 0, "assists": 0},
            {"member_id": 4, "goals": 0, "assists": 0},
            {"member_id": 5, "goals": 0, "assists": 0},
        ],
    },
]

POSTS_SEED: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "풋살 기초 기술",
        "content": "풋살에서 가장 중요한 기초 기술들을 정리해봤습니다. 정확한 킥, 스톱, 드리블이 모든 것의 기본입니다.",
        "author_uid": "fcstars-user1",
        "category": "기술",
        "isPinned": True,
        "comments": [
            {"author_uid": "fcstars-user2", "content": "정말 도움이 되는 정보네요!"},
            {"author_uid": "fcstars-user1", "content": "감사합니다!"}
        ]
    },
    {
        "id": 2,
        "title": "경기 후 스트레칭 팁",
        "content": "경기 후 근육 피로를 빠르게 풀기 위한 스트레칭 루틴을 공유합니다. 5분 만에 할 수 있습니다.",
        "author_uid": "fcstars-user2",
        "category": "팁",
        "isPinned": False,
        "comments": [
            {"author_uid": "fcstars-user1", "content": "이거 정말 좋네요!"}
        ]
    },
    {
        "id": 3,
        "title": "이번 주 경기 분석",
        "content": "지난 경기에서 우리 팀의 장점과 개선할 점을 분석해보았습니다. 다음 경기에 참고하시기 바랍니다.",
        "author_uid": "fcstars-user1",
        "category": "일반",
        "isPinned": False,
        "comments": []
    }
]

# Auth 사용자: fixed uid 권장
AUTH_USERS_SEED: List[Dict[str, Any]] = [
    {
        "uid": "fcstars-admin",
        "email": "admin@fcstars.com",
        "password": "admin1234!",
        "display_name": "FC Stars Admin",
        "role": "admin",
        "status": "approved",
        "member_id": None,
        "disabled": False,
    },
    {
        "uid": "fcstars-operator",
        "email": "operator@fcstars.com",
        "password": "operator1234!",
        "display_name": "FC Stars Operator",
        "role": "operator",
        "status": "approved",
        "member_id": None,
        "disabled": False,
    },
    {
        "uid": "fcstars-user1",
        "email": "user1@fcstars.com",
        "password": "user1!234",
        "display_name": "박준환",
        "role": "user",
        "status": "approved",
        "member_id": 1,
        "disabled": False,
    },
    {
        "uid": "fcstars-user2",
        "email": "user2@fcstars.com",
        "password": "user2!234",
        "display_name": "윤여준",
        "role": "user",
        "status": "pending",
        "member_id": 2,
        "disabled": False,
    },
    {
        "uid": "fcstars-user3",
        "email": "user3@fcstars.com",
        "password": "user3!234",
        "display_name": "이방인",
        "role": "user",
        "status": "rejected",
        "member_id": 3,
        "disabled": False,
    },
]


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def _delete_collection(db, collection_name: str, batch_size: int = 100) -> None:
    while True:
        docs = list(db.collection(collection_name).limit(batch_size).stream())
        if not docs:
            break

        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
        batch.commit()


def _delete_schedule_participants(db, batch_size: int = 100) -> None:
    schedules = list(db.collection("schedules").stream())
    for schedule_doc in schedules:
        while True:
            participants = list(schedule_doc.reference.collection("participants").limit(batch_size).stream())
            if not participants:
                break

            batch = db.batch()
            for pdoc in participants:
                batch.delete(pdoc.reference)
            batch.commit()


def _delete_posts_and_comments(db, batch_size: int = 100) -> None:
    posts = list(db.collection("posts").stream())
    for post_doc in posts:
        # 각 post 문서 아래의 comments 서브컬렉션 삭제
        while True:
            comments = list(post_doc.reference.collection("comments").limit(batch_size).stream())
            if not comments:
                break

            batch = db.batch()
            for comment_doc in comments:
                batch.delete(comment_doc.reference)
            batch.commit()


def _reset_firestore_docs(db) -> None:
    _delete_schedule_participants(db)
    _delete_posts_and_comments(db)
    _delete_collection(db, "accounts")
    _delete_collection(db, "members")
    _delete_collection(db, "schedules")


def _upsert_auth_user(seed: Dict[str, Any]) -> str:
    """
    Auth 사용자 upsert.
    - 기존 이메일이 있으면 업데이트
    - 없으면 uid를 고정해서 생성
    """
    try:
        existing = auth.get_user_by_email(seed["email"])
        user = auth.update_user(
            existing.uid,
            display_name=seed.get("display_name"),
            password=seed["password"],
            disabled=seed.get("disabled", False),
            email_verified=True,
        )
        uid = user.uid
    except Exception:
        user = auth.create_user(
            uid=seed["uid"],
            email=seed["email"],
            display_name=seed.get("display_name"),
            password=seed["password"],
            disabled=seed.get("disabled", False),
            email_verified=True,
        )
        uid = user.uid

    claims = {"role": seed["role"]} if seed.get("status") == "approved" else {}
    auth.set_custom_user_claims(uid, claims)
    return uid


def _upsert_account_doc(db, uid: str, seed: Dict[str, Any]) -> None:
    db.collection("accounts").document(uid).set(
        {
            "email": seed["email"],
            "displayName": seed.get("display_name"),
            "role": seed["role"],
            "status": seed["status"],
            "memberId": seed.get("member_id"),
            "firebaseUid": uid,
            "approvedBy": None if seed.get("status") != "approved" else "seed",
            "approvedAt": firestore.SERVER_TIMESTAMP if seed.get("status") == "approved" else None,
            "lastLoginAt": None,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )


# --------------------------------------------------
# Main seed
# --------------------------------------------------
def seed_firestore_full_sample(db, *, reset_firestore_docs: bool = True) -> Dict[str, str]:
    """
    Firestore 문서 + Firebase Auth 사용자까지 함께 시드합니다.

    생성 구조:
      - Auth users
      - accounts/{uid}
      - members/{id}
      - schedules/{id}
      - schedules/{id}/participants/{member_id}

    반환값:
      email -> uid 매핑
    """
    if reset_firestore_docs:
        _reset_firestore_docs(db)

    # 1) members
    member_batch = db.batch()
    for m in MEMBERS_SEED:
        ref = db.collection("members").document(str(m["id"]))
        member_batch.set(
            ref,
            {
                "name": m["name"],
                "birthYear": m["birth_year"],
                "position": m["position"],
                "attendanceDays": m["attendance_days"],
                "goals": m["goals"],
                "assists": m["assists"],
                "isGuest": m["is_guest"],
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            },
        )
    member_batch.commit()

    # 2) schedules + participants
    schedule_batch = db.batch()
    for s in SCHEDULES_SEED:
        sref = db.collection("schedules").document(str(s["id"]))
        schedule_batch.set(
            sref,
            {
                "type": s["type"],
                "matchType": s["match_type"] if s["type"] == "match" else None,
                "date": s["date"],
                "location": s["location"],
                "result": s["result"],
                "matchTeam": s["match_team"],
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            },
        )

        for p in s["participants"]:
            pref = sref.collection("participants").document(str(p["member_id"]))
            schedule_batch.set(
                pref,
                {
                    "goals": p["goals"],
                    "assists": p["assists"],
                    "isParticipating": True,
                    "updatedAt": firestore.SERVER_TIMESTAMP,
                },
            )
    schedule_batch.commit()

    # 3) Auth users + accounts docs
    email_to_uid: Dict[str, str] = {}
    for a in AUTH_USERS_SEED:
        uid = _upsert_auth_user(a)
        _upsert_account_doc(db, uid, a)
        email_to_uid[a["email"]] = uid

    # 4) posts + comments
    for post in POSTS_SEED:
        post_ref = db.collection("posts").document(str(post["id"]))
        post_ref.set({
            "title": post["title"],
            "content": post["content"],
            "author_id": post["author_uid"],
            "category": post["category"],
            "isPinned": post["isPinned"],
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        })
        
        # 각 post에 대한 comments 추가
        for comment in post.get("comments", []):
            post_ref.collection("comments").document().set({
                "author_id": comment["author_uid"],
                "content": comment["content"],
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            })

    return email_to_uid


# --------------------------------------------------
# Basic seed (for initialization)
# --------------------------------------------------
BASIC_MEMBERS_SEED: List[Dict[str, Any]] = [
    {"id": 1, "name": "박준환", "birth_year": 1983, "position": "주장",   "attendance_days": 0, "goals": 0, "assists": 0, "is_guest": False},
    {"id": 2, "name": "윤여준", "birth_year": 1986, "position": "부주장", "attendance_days": 0,  "goals": 0, "assists": 0, "is_guest": False},
    {"id": 3, "name": "한은주", "birth_year": 1986, "position": "매니저", "attendance_days": 0, "goals": 0, "assists": 0, "is_guest": False},
    {"id": 4, "name": "박정환", "birth_year": 1986, "position": "선수",   "attendance_days": 0,  "goals": 0, "assists": 0, "is_guest": False},
    {"id": 5, "name": "조한도", "birth_year": 1986, "position": "코치",   "attendance_days": 0,  "goals": 0, "assists": 0, "is_guest": False},
    {"id": 6, "name": "구자인", "birth_year": 1986, "position": "선수",   "attendance_days": 0,  "goals": 0, "assists": 0, "is_guest": False},
    {"id": 7, "name": "유상빈", "birth_year": 1982, "position": "게스트", "attendance_days": 0,  "goals": 0, "assists": 0, "is_guest": True},
]

BASIC_AUTH_USERS_SEED: List[Dict[str, Any]] = [
    {
        "uid": "fcstars-admin",
        "email": "admin@fcstars.com",
        "password": "admin1234!",
        "display_name": "FC Stars Admin",
        "role": "admin",
        "status": "approved",
        "member_id": None,
        "disabled": False,
    }
]

BASIC_SCHEDULES_SEED: List[Dict[str, Any]] = [
    {
        "id": 2,
        "type": "training",
        "match_type": None,
        "date": datetime(2026, 4, 19, 9, 0, 0),
        "location": "다산 LS 풋살파크 트레이닝존",
        "result": None,
        "match_team": None,
        "participants": [
            {"member_id": 1, "goals": 0, "assists": 0},
            {"member_id": 2, "goals": 0, "assists": 0},
            {"member_id": 3, "goals": 0, "assists": 0},
            {"member_id": 4, "goals": 0, "assists": 0},
            {"member_id": 5, "goals": 0, "assists": 0},
            {"member_id": 6, "goals": 0, "assists": 0},
        ],
    }
]


BASIC_POSTS_SEED: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "환영합니다!",
        "content": "FC Stars 팀에 환영합니다. 이 게시판에서 팀 소식, 팁, 정보를 공유하세요.",
        "author_uid": "fcstars-admin",
        "category": "일반",
        "isPinned": True,
        "comments": []
    }
]


def seed_firestore_basic_sample(db, *, reset_firestore_docs: bool = True) -> Dict[str, str]:
    """
    Firestore 기본 초기화: 기존 데이터를 삭제하고 기본 데이터로 설정합니다.

    생성 구조:
      - Auth users (admin only)
      - accounts/{uid}
      - members/{id} (기본 멤버들, 통계 0)
      - schedules/{id} (기본 training 하나)
      - schedules/{id}/participants/{member_id}

    반환값:
      email -> uid 매핑
    """
    if reset_firestore_docs:
        _reset_firestore_docs(db)

    # 1) members
    member_batch = db.batch()
    for m in BASIC_MEMBERS_SEED:
        ref = db.collection("members").document(str(m["id"]))
        member_batch.set(
            ref,
            {
                "name": m["name"],
                "birthYear": m["birth_year"],
                "position": m["position"],
                "attendanceDays": m["attendance_days"],
                "goals": m["goals"],
                "assists": m["assists"],
                "isGuest": m["is_guest"],
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            },
        )
    member_batch.commit()

    # 2) schedules + participants
    schedule_batch = db.batch()
    for s in BASIC_SCHEDULES_SEED:
        sref = db.collection("schedules").document(str(s["id"]))
        schedule_batch.set(
            sref,
            {
                "type": s["type"],
                "matchType": s.get("match_type"),
                "date": s["date"],
                "location": s["location"],
                "result": s["result"],
                "matchTeam": s["match_team"],
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            },
        )

        for p in s["participants"]:
            pref = sref.collection("participants").document(str(p["member_id"]))
            schedule_batch.set(
                pref,
                {
                    "goals": p["goals"],
                    "assists": p["assists"],
                    "isParticipating": True,
                    "updatedAt": firestore.SERVER_TIMESTAMP,
                },
            )
    schedule_batch.commit()

    # 3) Auth users + accounts docs
    email_to_uid: Dict[str, str] = {}
    for a in BASIC_AUTH_USERS_SEED:
        uid = _upsert_auth_user(a)
        _upsert_account_doc(db, uid, a)
        email_to_uid[a["email"]] = uid

    # 4) posts + comments
    for post in BASIC_POSTS_SEED:
        post_ref = db.collection("posts").document(str(post["id"]))
        post_ref.set({
            "title": post["title"],
            "content": post["content"],
            "author_id": post["author_uid"],
            "category": post["category"],
            "isPinned": post["isPinned"],
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        })
        
        # 각 post에 대한 comments 추가
        for comment in post.get("comments", []):
            post_ref.collection("comments").document().set({
                "author_id": comment["author_uid"],
                "content": comment["content"],
                "createdAt": firestore.SERVER_TIMESTAMP,
                "updatedAt": firestore.SERVER_TIMESTAMP,
            })

    return email_to_uid