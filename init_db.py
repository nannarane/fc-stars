import sqlite3
import os

# 데이터베이스 파일 경로
db_path = 'fc_stars.db'

# 기존 데이터베이스 삭제
if os.path.exists(db_path):
    os.remove(db_path)
    print('기존 데이터베이스 파일 삭제됨')

# 새 데이터베이스 생성 및 스키마 적용
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 스키마를 개별적으로 실행 (외래 키 제약 조건 고려하여 순서 조정)
schema_statements = [
    """CREATE TABLE members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        birth_year INTEGER,
        position TEXT,
        attendance_days INTEGER DEFAULT 0,
        goals INTEGER DEFAULT 0,
        assists INTEGER DEFAULT 0,
        is_guest BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK (type IN ('match', 'training')),
        date DATE NOT NULL,
        location TEXT NOT NULL,
        result TEXT CHECK (result IN ('win', 'loss', 'draw')) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE schedule_participants (
        schedule_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        goals INTEGER DEFAULT 0,
        assists INTEGER DEFAULT 0,
        PRIMARY KEY (schedule_id, member_id),
        FOREIGN KEY (schedule_id) REFERENCES schedules(id) ON DELETE CASCADE,
        FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE match_teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        skill_level TEXT,
        age_group TEXT,
        manner_score DECIMAL(3,1) CHECK (manner_score >= 0 AND manner_score <= 5),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (schedule_id) REFERENCES schedules(id) ON DELETE CASCADE
    )""",
    "CREATE INDEX idx_schedules_date ON schedules(date)",
    "CREATE INDEX idx_schedules_type ON schedules(type)",
    "CREATE INDEX idx_match_teams_schedule_id ON match_teams(schedule_id)",
    "CREATE INDEX idx_schedule_participants_schedule_id ON schedule_participants(schedule_id)",
    "CREATE INDEX idx_schedule_participants_member_id ON schedule_participants(member_id)"
]

for statement in schema_statements:
    cursor.execute(statement)

conn.commit()
print('데이터베이스 스키마 생성 완료')

# 샘플 데이터 적용
sample_statements = [
    """INSERT INTO members (name, birth_year, position, attendance_days, goals) VALUES
    ('구자인', 1986, '선수', 0, 0),
    ('박정환', 1986, '선수', 0, 0),
    ('박준환', 1986, '주장', 0, 0),
    ('윤여준', 1986, '부주장', 0, 0),
    ('조한도', 1986, '코치', 0, 0),
    ('한은주', 1986, '매니저', 0, 0)""",
    """INSERT INTO schedules (type, date, location, result) VALUES
    ('match', '2026-04-10', '구리 대복풋살장', 'win'),
    ('training', '2026-04-13', '구리 아천스타디움', NULL),
    ('match', '2026-04-16', '언더플레이 풋살파크', 'loss'),
    ('training', '2026-04-19', '힐링FC풋살장', NULL),
    ('match', '2026-04-22', '김병지축구클럽 구리점', 'draw')""",
    """INSERT INTO match_teams (schedule_id, name, skill_level, age_group, manner_score) VALUES
    (1, 'Red Hawks', '중급', '20-30대', 4.2),
    (3, 'Blue Waves', '고급', '40대+', 3.8),
    (5, 'White Tigers', '초보', '30대', 4.5)""",
    """INSERT INTO schedule_participants (schedule_id, member_id, goals) VALUES
    (1, 1, 2), (1, 2, 1), (1, 3, 3), (1, 4, 0), (1, 6, 1)""",
    """INSERT INTO schedule_participants (schedule_id, member_id, goals) VALUES
    (2, 1, 0), (2, 2, 0), (2, 3, 0), (2, 4, 0), (2, 5, 0), (2, 6, 0)""",
    """INSERT INTO schedule_participants (schedule_id, member_id, goals) VALUES
    (3, 1, 0), (3, 2, 1), (3, 3, 0), (3, 4, 2), (3, 6, 0)""",
    """INSERT INTO schedule_participants (schedule_id, member_id, goals) VALUES
    (4, 1, 0), (4, 2, 0), (4, 3, 0), (4, 5, 0)""",
    """INSERT INTO schedule_participants (schedule_id, member_id, goals) VALUES
    (5, 1, 1), (5, 2, 0), (5, 3, 2), (5, 4, 1), (5, 6, 0)"""
]

for statement in sample_statements:
    cursor.execute(statement)

conn.commit()
print('샘플 데이터 삽입 완료')

# assists 데이터 추가 (샘플 데이터에 assists가 없으므로 랜덤하게 추가)
print('어시스트 데이터 추가 중...')
cursor.execute("UPDATE schedule_participants SET assists = ABS(RANDOM() % 3) WHERE schedule_id IN (SELECT id FROM schedules WHERE type = 'match')")
conn.commit()
print('어시스트 데이터 추가 완료')

conn.close()
print('데이터베이스 초기화 및 데이터 구성 완료!')