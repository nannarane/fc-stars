import sqlite3
from typing import List, Dict, Optional
from repositories.base.member_repository import MemberRepository
from settings import SQLITE_DB_PATH


class SQLiteMemberRepository(MemberRepository):
    def _conn(self):
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def list_members(self) -> List[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, name, birth_year, position,
                       attendance_days, goals, assists, is_guest,
                       created_at, updated_at
                FROM members
                ORDER BY name
                """
            )
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_member(self, member_id: str) -> Optional[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM members WHERE id = ?", (member_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_member(self, data: Dict) -> str:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO members (
                    name, birth_year, position,
                    attendance_days, goals, assists, is_guest
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["name"],
                    data.get("birth_year"),
                    data.get("position"),
                    data.get("attendance_days", 0),
                    data.get("goals", 0),
                    data.get("assists", 0),
                    int(data.get("is_guest", False)),
                ),
            )
            conn.commit()
            return str(cur.lastrowid)
        finally:
            conn.close()

    def update_member(self, member_id: str, data: Dict) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            fields = []
            params = []

            allowed = [
                "name",
                "birth_year",
                "position",
                "attendance_days",
                "goals",
                "assists",
                "is_guest",
            ]

            for key in allowed:
                if key in data and data[key] is not None:
                    fields.append(f"{key} = ?")
                    params.append(int(data[key]) if key == "is_guest" else data[key])

            if not fields:
                return

            fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(member_id)

            cur.execute(
                f"""
                UPDATE members
                SET {", ".join(fields)}
                WHERE id = ?
                """,
                params,
            )
            conn.commit()
        finally:
            conn.close()

    def delete_member(self, member_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()
        finally:
            conn.close()

    def add_guest_member(self, name: str, position: str = "게스트") -> str:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO members (name, position, is_guest)
                VALUES (?, ?, 1)
                """,
                (name, position),
            )
            conn.commit()
            return str(cur.lastrowid)
        finally:
            conn.close()

    def delete_guest_member(self, member_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT is_guest FROM members WHERE id = ?", (member_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("멤버를 찾을 수 없습니다.")
            if not row["is_guest"]:
                raise ValueError("게스트 멤버가 아닙니다.")
            cur.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()
        finally:
            conn.close()