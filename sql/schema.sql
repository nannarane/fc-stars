-- FC Stars Database Schema
-- Cloud Firestore로 마이그레이션 예정이지만, 관계형 설계로 시작

-- Members table
CREATE TABLE members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birth_year INTEGER, -- 출생년도만 기록
    position TEXT, -- 직책 (예: 주장, 부주장, 선수 등)
    attendance_days INTEGER DEFAULT 0,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0, -- 추가: 어시스트 수
    is_guest BOOLEAN DEFAULT 0, -- 게스트 멤버 구분
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schedules table (matches and trainings)
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK (type IN ('match', 'training')),
    date DATE NOT NULL,
    location TEXT NOT NULL,
    result TEXT CHECK (result IN ('win', 'loss', 'draw')) NULL, -- only for matches
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Match teams table (one per match schedule)
CREATE TABLE match_teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    skill_level TEXT, -- 예: 초보, 중급, 고급
    age_group TEXT, -- 예: 20대, 30대, 청년부
    manner_score DECIMAL(3,1) CHECK (manner_score >= 0 AND manner_score <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES schedules(id) ON DELETE CASCADE
);

-- Schedule participants (many-to-many between schedules and members)
CREATE TABLE schedule_participants (
    schedule_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    goals INTEGER DEFAULT 0, -- goals scored by this member in this schedule (only for matches)
    assists INTEGER DEFAULT 0, -- assists made by this member in this schedule (only for matches)
    PRIMARY KEY (schedule_id, member_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(id) ON DELETE CASCADE,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX idx_schedules_date ON schedules(date);
CREATE INDEX idx_schedules_type ON schedules(type);
CREATE INDEX idx_match_teams_schedule_id ON match_teams(schedule_id);
CREATE INDEX idx_schedule_participants_schedule_id ON schedule_participants(schedule_id);
CREATE INDEX idx_schedule_participants_member_id ON schedule_participants(member_id);