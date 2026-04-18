import sqlite3
from typing import Optional, Dict, List

from repositories.base.account_repository import AccountRepository
from settings import SQLITE_DB_PATH


class SQLiteAccountRepository(AccountRepository):
    def _conn(self):
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def create_account(self, data: Dict) -> str:
        """
        data keys:
        - email (required)
        - display_name
        - password_hash (required in dev)
        - role: admin | operator | user
        - status: pending | approved | rejected | suspended
        - member_id
        - firebase_uid
        """
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO accounts (
                    member_id, email, display_name, password_hash,
                    role, status, firebase_uid
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get("member_id"),
                    data["email"],
                    data.get("display_name"),
                    data["password_hash"],
                    data.get("role", "user"),
                    data.get("status", "pending"),
                    data.get("firebase_uid"),
                ),
            )
            conn.commit()
            return str(cur.lastrowid)
        finally:
            conn.close()

    def list_accounts(
        self,
        status: Optional[str] = None,
        role: Optional[str] = None,
    ) -> List[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            query = """
                SELECT
                    id, member_id, email, display_name, role, status,
                    approved_by, approved_at, last_login_at,
                    firebase_uid, created_at, updated_at
                FROM accounts
                WHERE 1=1
            """
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)

            if role:
                query += " AND role = ?"
                params.append(role)

            query += " ORDER BY created_at DESC"

            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_account_by_email(self, email: str) -> Optional[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM accounts WHERE email = ?", (email,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_account_by_uid(self, uid: str) -> Optional[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM accounts WHERE firebase_uid = ?", (uid,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def approve_account(self, account_id: str, approver_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE accounts
                SET status = 'approved',
                    approved_by = ?,
                    approved_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (approver_id, account_id),
            )
            conn.commit()
        finally:
            conn.close()

    def reject_account(self, account_id: str, approver_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE accounts
                SET status = 'rejected',
                    approved_by = ?,
                    approved_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (approver_id, account_id),
            )
            conn.commit()
        finally:
            conn.close()

    def suspend_account(self, account_id: str, approver_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE accounts
                SET status = 'suspended',
                    approved_by = ?,
                    approved_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (approver_id, account_id),
            )
            conn.commit()
        finally:
            conn.close()

    def update_last_login(self, account_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE accounts
                SET last_login_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (account_id,),
            )
            conn.commit()
        finally:
            conn.close()