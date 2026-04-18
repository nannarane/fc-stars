import sqlite3
from typing import List, Dict, Optional
from repositories.base.schedule_repository import ScheduleRepository
from settings import SQLITE_DB_PATH


class SQLiteScheduleRepository(ScheduleRepository):
    def _conn(self):
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        self._ensure_match_type_column(conn)
        return conn

    def _ensure_match_type_column(self, conn):
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(match_teams)")
        columns = [row[1] for row in cur.fetchall()]
        if "match_type" not in columns:
            cur.execute("ALTER TABLE match_teams ADD COLUMN match_type TEXT DEFAULT '5:5'")
            conn.commit()

    def list_schedules(self) -> List[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            query = """
            SELECT
                s.id,
                s.type,
                s.date,
                s.location,
                s.result,
                mt.name AS opponent,
                mt.skill_level,
                mt.age_group,
                mt.match_type,
                mt.manner_score,
                COUNT(sp.member_id) AS participants
            FROM schedules s
            LEFT JOIN match_teams mt ON s.id = mt.schedule_id
            LEFT JOIN schedule_participants sp ON s.id = sp.schedule_id
            GROUP BY
                s.id, s.type, s.date, s.location, s.result,
                mt.name, mt.skill_level, mt.age_group, mt.match_type, mt.manner_score
            ORDER BY s.date DESC
            """
            cur.execute(query)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_schedule(self, schedule_id: str) -> Optional[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, type, date, location, result, created_at, updated_at
                FROM schedules
                WHERE id = ?
                """,
                (schedule_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_schedule(self, data: Dict) -> str:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO schedules (type, date, location, result)
                VALUES (?, ?, ?, ?)
                """,
                (
                    data["type"],
                    data["date"],
                    data["location"],
                    data.get("result"),
                ),
            )
            conn.commit()
            return str(cur.lastrowid)
        finally:
            conn.close()

    def update_schedule(self, schedule_id: str, data: Dict) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            fields = []
            params = []

            allowed = ["type", "date", "location", "result"]
            for key in allowed:
                if key in data and data[key] is not None:
                    fields.append(f"{key} = ?")
                    params.append(data[key])

            if not fields:
                return

            fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(schedule_id)

            cur.execute(
                f"""
                UPDATE schedules
                SET {", ".join(fields)}
                WHERE id = ?
                """,
                params,
            )
            conn.commit()
        finally:
            conn.close()

    def delete_schedule(self, schedule_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
            conn.commit()
        finally:
            conn.close()

    def get_match_team(self, schedule_id: str) -> Optional[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT name, skill_level, age_group, match_type, manner_score
                FROM match_teams
                WHERE schedule_id = ?
                """,
                (schedule_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def set_match_team(self, schedule_id: str, team_data: Dict) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE match_teams
                SET name = ?, skill_level = ?, age_group = ?, match_type = ?, manner_score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE schedule_id = ?
                """,
                (
                    team_data["name"],
                    team_data.get("skill_level"),
                    team_data.get("age_group"),
                    team_data.get("match_type", "5:5"),
                    team_data.get("manner_score"),
                    schedule_id,
                ),
            )
            if cur.rowcount == 0:
                cur.execute(
                    """
                    INSERT INTO match_teams (schedule_id, name, skill_level, age_group, match_type, manner_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        schedule_id,
                        team_data["name"],
                        team_data.get("skill_level"),
                        team_data.get("age_group"),
                        team_data.get("match_type", "5:5"),
                        team_data.get("manner_score"),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def delete_match_team(self, schedule_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM match_teams WHERE schedule_id = ?", (schedule_id,))
            conn.commit()
        finally:
            conn.close()

    def list_participants(self, schedule_id: str) -> List[Dict]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT
                    m.id AS member_id,
                    m.name,
                    m.position,
                    sp.goals,
                    sp.assists
                FROM schedule_participants sp
                JOIN members m ON sp.member_id = m.id
                WHERE sp.schedule_id = ?
                ORDER BY m.name
                """,
                (schedule_id,),
            )
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def set_participants(self, schedule_id: str, participants: List[Dict]) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM schedule_participants WHERE schedule_id = ?", (schedule_id,))

            for p in participants:
                if p.get("is_participating", True):
                    cur.execute(
                        """
                        INSERT INTO schedule_participants (schedule_id, member_id, goals, assists)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            schedule_id,
                            p["member_id"],
                            p.get("goals", 0),
                            p.get("assists", 0),
                        ),
                    )
            conn.commit()
        finally:
            conn.close()

    def add_participant(self, schedule_id: str, member_id: str, goals: int = 0, assists: int = 0) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO schedule_participants
                (schedule_id, member_id, goals, assists)
                VALUES (?, ?, ?, ?)
                """,
                (schedule_id, member_id, goals, assists),
            )
            conn.commit()
        finally:
            conn.close()

    def remove_participant(self, schedule_id: str, member_id: str) -> None:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                DELETE FROM schedule_participants
                WHERE schedule_id = ? AND member_id = ?
                """,
                (schedule_id, member_id),
            )
            conn.commit()
        finally:
            conn.close()