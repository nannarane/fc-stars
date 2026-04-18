# utils/factory.py
from settings import USE_FIRESTORE
from firebase_init import init_firebase

from repositories.sqlite.account_repository import SQLiteAccountRepository
from repositories.sqlite.member_repository import SQLiteMemberRepository
from repositories.sqlite.schedule_repository import SQLiteScheduleRepository
from repositories.sqlite.post_repository import SQLitePostRepository

from repositories.firestore.account_repository import FirestoreAccountRepository
from repositories.firestore.member_repository import FirestoreMemberRepository
from repositories.firestore.schedule_repository import FirestoreScheduleRepository
from repositories.firestore.post_repository import FirestorePostRepository

_firestore_db = None


def _get_firestore_db():
    global _firestore_db
    if _firestore_db is None:
        _firestore_db = init_firebase()
    return _firestore_db


def get_account_repository():
    return FirestoreAccountRepository(_get_firestore_db()) if USE_FIRESTORE else SQLiteAccountRepository()


def get_member_repository():
    return FirestoreMemberRepository(_get_firestore_db()) if USE_FIRESTORE else SQLiteMemberRepository()


def get_schedule_repository():
    return FirestoreScheduleRepository(_get_firestore_db()) if USE_FIRESTORE else SQLiteScheduleRepository()


def get_post_repository():
    return FirestorePostRepository(_get_firestore_db()) if USE_FIRESTORE else SQLitePostRepository()
