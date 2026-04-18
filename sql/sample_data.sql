-- accounts.member_id는 members.id와 연결되므로 샘플 데이터에서 이미 존재하는 member id만 넣어야 합니다.
-- approved_by는 accounts.id를 참조하는 형태라서 관리자 계정 id=1이 먼저 들어가 있어야 합니다.
PRAGMA foreign_keys = ON;

-- =========================================================
-- members
-- =========================================================
INSERT INTO members (
    id, name, birth_year, position,
    attendance_days, goals, assists, is_guest,
    created_at, updated_at
) VALUES
(1, '박준환', 1983, '주장', 10, 5, 3, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, '윤여준', 1986, '부주장', 8, 2, 4, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, '한은주', 1986, '매니저', 12, 7, 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(4, '박정환', 1986, '선수', 6, 1, 2, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(5, '조한도', 1986, '코치', 9, 3, 5, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(6, '구자인', 1986, '선수', 1, 0, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(7, '유상빈', 1982, '게스트', 2, 1, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


-- =========================================================
-- schedules
-- =========================================================
INSERT INTO schedules (
    id, type, date, location, result,
    created_at, updated_at
) VALUES
(1, 'match', '2026-03-06 22:00:00', '언더플레이 풋살파크', 'win',
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(2, 'training', '2026-03-20 22:00:00', '구리 대복풋살장', NULL,
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(3, 'match', '2026-04-03 20:00:00', '백봉풋살장', 'loss',
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(4, 'training', '2026-04-17 21:00:00', '힐링FC풋살장', NULL,
 CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


-- =========================================================
-- accounts
-- =========================================================
INSERT INTO accounts (
    id, member_id, email, display_name, password_hash,
    role, status, approved_by, approved_at, last_login_at,
    firebase_uid, created_at, updated_at
) VALUES
(1, NULL, 'admin@fcstars.com', 'FC Stars Admin', '$2b$12$BQ86WTYSG0Lhopz.dcd6WOtV2PILZ7iVOisSRTZUjSmTPbkEQ.P0a',
 'admin', 'approved', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
 NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(2, NULL, 'operator@fcstars.com', 'FC Stars Operator', '$2b$12$4j/5IEMBo6rSm.vs4p1smOjagTiUzD8UnMeIjiki51SEwMySAgKx6',
 'operator', 'approved', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
 NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(3, 1, 'user1@fcstars.com', '홍길동', '$2b$12$wdEASNkriwL4qvPESRd.X.SgZRJB8AusJ1ipnDSFt1KZuKkjFFfey',
 'user', 'approved', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP,
 NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(4, 2, 'user2@fcstars.com', '김철수', '$2b$12$6DYkiuuw2GxcKFSXLTXLfOak3L3VpfeRXROLnONIrBClcwWvV5ukq',
 'user', 'pending', NULL, NULL, NULL,
 NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

(5, 3, 'user3@fcstars.com', '이방인', '$2b$12$Hdcj08Ox2MVjlfrownELk.UlTUH71iNqURncrumGAKKRiBxANHELa',
 'user', 'rejected', 1, CURRENT_TIMESTAMP, NULL,
 NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);



-- =========================================================
-- match_teams
-- one schedule = one opponent team
-- =========================================================
INSERT INTO match_teams (
    id, schedule_id, name, skill_level, age_group, manner_score,
    created_at, updated_at
) VALUES
(1, 1, 'FC Thunder', '초급', '30대', 4.5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 3, 'Seoul United', '중급', '20대', 4.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


-- =========================================================
-- schedule_participants
-- =========================================================
INSERT INTO schedule_participants (
    schedule_id, member_id, goals, assists
) VALUES
-- match #1
(1, 1, 1, 1),
(1, 2, 0, 1),
(1, 3, 2, 0),
(1, 4, 0, 0),
(1, 6, 0, 0),

-- training #2
(2, 1, 0, 0),
(2, 2, 0, 0),
(2, 3, 0, 0),
(2, 5, 0, 0),
(2, 7, 0, 0),

-- match #3
(3, 1, 0, 1),
(3, 2, 1, 0),
(3, 3, 1, 1),
(3, 4, 0, 0),
(3, 5, 0, 1),

-- training #4
(4, 1, 0, 0),
(4, 2, 0, 0),
(4, 3, 0, 0),
(4, 4, 0, 0),
(4, 5, 0, 0);