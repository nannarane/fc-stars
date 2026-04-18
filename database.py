import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from settings import SQLITE_DB_PATH


def get_db_connection():
    """SQLite 데이터베이스 연결을 반환합니다."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row  # 컬럼명으로 접근 가능하게 설정
    return conn

def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = get_db_connection()
    try:
        with open('sql/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
        print("Database schema initialized successfully")
    except FileNotFoundError:
        print("Warning: schema.sql not found, skipping schema initialization")
    finally:
        conn.close()

def load_sample_data():
    """샘플 데이터 로드"""
    conn = get_db_connection()
    try:
        with open('sql/sample_data.sql', 'r', encoding='utf-8') as f:
            sample_sql = f.read()
        conn.executescript(sample_sql)
        conn.commit()
        print("Sample data loaded successfully")
    except FileNotFoundError:
        print("Warning: sample_data.sql not found, skipping sample data loading")
    finally:
        conn.close()

def get_schedules_with_details() -> List[Dict]:
    """일정 목록을 가져옵니다 (상대팀 정보 포함)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
        SELECT s.id, s.type, s.date, s.location, s.result,
               mt.name as opponent, mt.skill_level, mt.age_group, mt.match_type, mt.manner_score,
               COUNT(sp.member_id) as participants
        FROM schedules s
        LEFT JOIN match_teams mt ON s.id = mt.schedule_id
        LEFT JOIN schedule_participants sp ON s.id = sp.schedule_id
        GROUP BY s.id, s.type, s.date, s.location, s.result,
                 mt.name, mt.skill_level, mt.age_group, mt.match_type, mt.manner_score
        ORDER BY s.date DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        schedules = []
        """
        for row in rows:
            schedule = dict(row)
            # 날짜를 datetime 객체로 변환
            if schedule['date']:                
                 #schedule['date'] = datetime.strptime(schedule['date'], '%Y-%m-%d').date()
                print(f"Raw date value: {schedule['date']}")  # 디버깅용 출력
                #schedule['date'] = datetime.fromtimestamp(schedule['date'])                
                
            schedules.append(schedule)

        return schedules
        """
        return rows
    finally:
        conn.close()

def get_members() -> List[Dict]:
    """멤버 목록을 가져옵니다"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, birth_year, position, attendance_days, goals, assists
            FROM members
            ORDER BY name
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_schedule_participants(schedule_id: int) -> List[Dict]:
    """특정 일정의 참석자 목록을 가져옵니다"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.name, m.position, sp.goals
            FROM schedule_participants sp
            JOIN members m ON sp.member_id = m.id
            WHERE sp.schedule_id = ?
            ORDER BY m.name
        """, (schedule_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_member_stats() -> List[Dict]:
    """멤버 통계 정보를 가져옵니다"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, position, attendance_days, goals, assists,
                   ROUND(goals * 1.0 / NULLIF(attendance_days, 0), 2) as goals_per_match,
                   ROUND(assists * 1.0 / NULLIF(attendance_days, 0), 2) as assists_per_match
            FROM members
            ORDER BY goals DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def add_schedule(type: str, date: str, location: str, result: str = None) -> int:
    """새 일정 추가 (match/training)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO schedules (type, date, location, result)
            VALUES (?, ?, ?, ?)
        """, (type, date, location, result))
        schedule_id = cursor.lastrowid
        conn.commit()
        return schedule_id
    finally:
        conn.close()

def add_match_team(schedule_id: int, name: str, skill_level: str, age_group: str, manner_score: float, match_type: str = "5:5"):
    """매치 상대팀 정보 추가"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO match_teams (schedule_id, name, skill_level, age_group, match_type, manner_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (schedule_id, name, skill_level, age_group, match_type, manner_score))
        conn.commit()
    finally:
        conn.close()

def get_match_team(schedule_id: int) -> Optional[Dict]:
    """일정에 연결된 상대팀 정보를 가져옵니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, skill_level, age_group, match_type, manner_score
            FROM match_teams
            WHERE schedule_id = ?
        """, (schedule_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def update_match_team(schedule_id: int, name: str, skill_level: str, age_group: str, manner_score: float, match_type: str = "5:5"):
    """상대팀 정보를 수정하거나 없으면 새로 추가합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE match_teams
            SET name = ?, skill_level = ?, age_group = ?, match_type = ?, manner_score = ?
            WHERE schedule_id = ?
        """, (name, skill_level, age_group, match_type, manner_score, schedule_id))
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO match_teams (schedule_id, name, skill_level, age_group, match_type, manner_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (schedule_id, name, skill_level, age_group, match_type, manner_score))
        conn.commit()
    finally:
        conn.close()

def delete_match_team(schedule_id: int):
    """일정에 연결된 상대팀 정보를 삭제합니다."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM match_teams WHERE schedule_id = ?", (schedule_id,))
        conn.commit()
    finally:
        conn.close()

def update_schedule(schedule_id: int, type: str = None, date: str = None, location: str = None, result: str = None):
    """일정 정보 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        updates = []
        params = []
        if type is not None:
            updates.append("type = ?")
            params.append(type)
        if date is not None:
            updates.append("date = ?")
            params.append(date)
        if location is not None:
            updates.append("location = ?")
            params.append(location)
        if result is not None:
            updates.append("result = ?")
            params.append(result)

        if updates:
            params.append(schedule_id)
            cursor.execute(f"""
                UPDATE schedules
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, params)
            conn.commit()
    finally:
        conn.close()

def delete_schedule(schedule_id: int):
    """일정 삭제 (연관 데이터도 함께 삭제됨 - CASCADE)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
        conn.commit()
    finally:
        conn.close()

def add_member(name: str, birth_year: int = None, position: str = None, assists: int = 0) -> int:
    """새 멤버 추가"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO members (name, birth_year, position, assists)
            VALUES (?, ?, ?, ?)
        """, (name, birth_year, position, assists))
        member_id = cursor.lastrowid
        conn.commit()
        return member_id
    finally:
        conn.close()

def update_member(member_id: int, name: str = None, birth_year: int = None, position: str = None, assists: int = None):
    """멤버 정보 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if birth_year is not None:
            updates.append("birth_year = ?")
            params.append(birth_year)
        if position is not None:
            updates.append("position = ?")
            params.append(position)
        if assists is not None:
            updates.append("assists = ?")
            params.append(assists)

        if updates:
            params.append(member_id)
            cursor.execute(f"""
                UPDATE members
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, params)
            conn.commit()
    finally:
        conn.close()

def delete_member(member_id: int):
    """멤버 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
    finally:
        conn.close()

def add_participant(schedule_id: int, member_id: int, goals: int = 0, assists: int = 0):
    """일정에 참석자 추가"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO schedule_participants (schedule_id, member_id, goals, assists)
            VALUES (?, ?, ?, ?)
        """, (schedule_id, member_id, goals, assists))
        conn.commit()
    finally:
        conn.close()

def remove_participant(schedule_id: int, member_id: int):
    """일정에서 참석자 제거"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM schedule_participants
            WHERE schedule_id = ? AND member_id = ?
        """, (schedule_id, member_id))
        conn.commit()
    finally:
        conn.close()

def add_guest_member(name: str, position: str = "게스트") -> int:
    """게스트 멤버 추가"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO members (name, position, is_guest)
            VALUES (?, ?, 1)
        """, (name, position))
        member_id = cursor.lastrowid
        conn.commit()
        return member_id
    finally:
        conn.close()

def delete_guest_member(member_id: int):
    """게스트 멤버 삭제 (게스트인 경우만)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # 게스트인지 확인 후 삭제
        cursor.execute("SELECT is_guest FROM members WHERE id = ?", (member_id,))
        result = cursor.fetchone()
        if result and result['is_guest']:
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()
        else:
            raise ValueError("게스트 멤버가 아닙니다")
    finally:
        conn.close()

def get_schedule_participants_detailed(schedule_id: int) -> List[Dict]:
    """특정 일정의 참석자 상세 정보 (참석 상태, 골 수, 어시스트 수 포함)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id as member_id, m.name, m.position, sp.goals, sp.assists,
                   CASE WHEN sp.member_id IS NOT NULL THEN 1 ELSE 0 END as is_participating
            FROM members m
            LEFT JOIN schedule_participants sp ON m.id = sp.member_id AND sp.schedule_id = ?
            ORDER BY m.name
        """, (schedule_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def update_schedule_participants(schedule_id: int, participants_data: List[Dict]):
    """일정 참석자 정보 일괄 업데이트"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # 기존 참석자 모두 제거
        cursor.execute("DELETE FROM schedule_participants WHERE schedule_id = ?", (schedule_id,))

        # 새로운 참석자 추가
        for participant in participants_data:
            if participant['is_participating']:
                cursor.execute("""
                    INSERT INTO schedule_participants (schedule_id, member_id, goals, assists)
                    VALUES (?, ?, ?, ?)
                """, (schedule_id, participant['member_id'], participant['goals'], participant.get('assists', 0)))

        conn.commit()
    finally:
        conn.close()

# 데이터베이스 초기화 (모듈 로드 시 실행)
if not os.path.exists(SQLITE_DB_PATH):
    init_database()
    load_sample_data()